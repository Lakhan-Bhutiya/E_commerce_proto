from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import SiteUser, Product, Category


# =========================
# AUTH (MANUAL — NO BUILT-IN)
# =========================

def register_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirmPassword']

        if SiteUser.objects.filter(email=email).exists():
            return render(request, 'registration/register.html', {
                'msg': 'Email already registered'
            })

        if password != confirm:
            return render(request, 'registration/register.html', {
                'msg': 'Passwords do not match'
            })

        SiteUser.objects.create(
            name=request.POST['name'],
            email=email,
            password=password,
            profile_image=request.FILES.get('profile_image')
        )

        return redirect('login')

    return render(request, 'registration/register.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = SiteUser.objects.filter(
            email=email,
            password=password
        ).first()

        if user:
            request.session['user_email'] = user.email
            request.session['user_name'] = user.name
            next_url = request.POST.get('next') or request.GET.get('next', 'store')
            return redirect(next_url)

        return render(request, 'registration/login.html', {
            'msg': 'Invalid credentials',
            'next': request.GET.get('next', '')
        })

    return render(request, 'registration/login.html', {
        'next': request.GET.get('next', '')
    })


def logout_view(request):
    request.session.flush()
    return redirect('login')


# =========================
# HOME (LANDING)
# =========================

def home(request):
    return render(request, 'home.html')


# =========================
# STORE (ECOMMERCE — BROWSE PUBLIC)
# =========================

from django.utils import timezone
from datetime import timedelta
from urllib.parse import urlencode

def store(request):
    cat_id = request.GET.get('cat')
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'newest')
    date_filter = request.GET.get('date', 'all')

    def query_url(**overrides):
        params = {}
        cat_val = overrides.get('cat')
        if cat_val is None:
            cat_val = cat_id
        if cat_val:
            params['cat'] = cat_val
        if q:
            params['q'] = q
        params['sort'] = overrides.get('sort', sort)
        params['date'] = overrides.get('date', date_filter)
        return '?' + urlencode(params)

    products = Product.objects.all()

    # Category filter
    if cat_id:
        products = products.filter(category_id=cat_id)

    # Search (title + description)
    if q:
        from django.db.models import Q
        products = products.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        )

    # Date filter (by created_at)
    if date_filter == 'week':
        since = timezone.now() - timedelta(days=7)
        products = products.filter(created_at__gte=since)
    elif date_filter == 'month':
        since = timezone.now() - timedelta(days=30)
        products = products.filter(created_at__gte=since)
    # date_filter == 'all' → no date filter

    # Sort
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name_asc':
        products = products.order_by('title')
    elif sort == 'name_desc':
        products = products.order_by('-title')
    elif sort == 'oldest':
        products = products.order_by('created_at')
    else:
        # newest (default)
        products = products.order_by('-created_at')

    categories = Category.objects.all()

    store_base = reverse('store')
    filter_urls = {
        'all_cats': store_base + query_url(cat=''),
        'sort_newest': store_base + query_url(sort='newest'),
        'sort_oldest': store_base + query_url(sort='oldest'),
        'sort_price_asc': store_base + query_url(sort='price_asc'),
        'sort_price_desc': store_base + query_url(sort='price_desc'),
        'sort_name_asc': store_base + query_url(sort='name_asc'),
        'sort_name_desc': store_base + query_url(sort='name_desc'),
        'date_all': store_base + query_url(date='all'),
        'date_week': store_base + query_url(date='week'),
        'date_month': store_base + query_url(date='month'),
    }
    categories_with_urls = [(c, store_base + query_url(cat=str(c.id))) for c in categories]

    return render(request, 'store.html', {
        'products': products,
        'categories': categories,
        'categories_with_urls': categories_with_urls,
        'search_query': q,
        'current_sort': sort,
        'current_date': date_filter,
        'current_cat': cat_id,
        'filter_urls': filter_urls,
    })


from .models import CartItem, Order, OrderItem


# =========================
# CART
# =========================

def add_to_cart(request, pid):
    if 'user_email' not in request.session:
        return redirect(reverse('login') + '?next=' + reverse('cart'))

    user = SiteUser.objects.get(email=request.session['user_email'])

    try:
        product = Product.objects.get(id=pid)
    except Product.DoesNotExist:
        return redirect('store')

    if product.stock < 1:
        return redirect('product_detail', pid=pid)  # stay on product; could pass message via session

    item, created = CartItem.objects.get_or_create(
        user=user,
        product_id=pid,
        defaults={'quantity': 1}
    )
    if not created:
        item.quantity += 1
    if item.quantity > product.stock:
        item.quantity = product.stock
    item.save()

    return redirect('cart')


def cart_view(request):
    if 'user_email' not in request.session:
        return redirect(reverse('login') + '?next=' + reverse('cart'))

    user = SiteUser.objects.get(
        email=request.session['user_email']
    )

    items = CartItem.objects.filter(user=user)

    total = sum(
        i.product.price * i.quantity for i in items
    )

    return render(request, 'cart.html', {
        'items': items,
        'total': total
    })


# =========================
# CHECKOUT
# =========================

def checkout(request):
    if 'user_email' not in request.session:
        return redirect(reverse('login') + '?next=' + reverse('checkout'))

    user = SiteUser.objects.get(email=request.session['user_email'])
    items = CartItem.objects.filter(user=user)

    if not items:
        return redirect('cart')

    # Check stock before creating order
    for i in items:
        if i.quantity > i.product.stock:
            return render(request, 'cart.html', {
                'items': items,
                'total': sum(ii.product.price * ii.quantity for ii in items),
                'msg': f'"{i.product.title}" only has {i.product.stock} in stock. Please update quantity.'
            })

    total = sum(i.product.price * i.quantity for i in items)

    order = Order.objects.create(user=user, total=total)

    for i in items:
        OrderItem.objects.create(
            order=order,
            product=i.product,
            price=i.product.price,
            quantity=i.quantity
        )
        i.product.stock -= i.quantity
        i.product.save()

    items.delete()

    return render(request, 'success.html', {'order': order})


# =========================
# ORDER HISTORY
# =========================

def order_history(request):
    if 'user_email' not in request.session:
        return redirect(reverse('login') + '?next=' + reverse('order_history'))

    user = SiteUser.objects.get(email=request.session['user_email'])
    orders = Order.objects.filter(user=user).select_related('user').prefetch_related('orderitem_set').order_by('-created_at')

    return render(request, 'order_history.html', {
        'orders': orders,
    })


# =========================
# PRODUCT DETAIL
# =========================

def product_detail(request, pid):
    product = get_object_or_404(Product, id=pid)
    return render(request, 'product_detail.html', {
        'product': product
    })


# =========================
# CART UPDATE QTY
# =========================

def update_cart_qty(request, cid, action):
    if 'user_email' not in request.session:
        return redirect('login')

    user = SiteUser.objects.get(email=request.session['user_email'])
    item = CartItem.objects.filter(id=cid, user=user).first()
    if not item:
        return redirect('cart')

    if action == 'inc':
        if item.quantity < item.product.stock:
            item.quantity += 1
    elif action == 'dec' and item.quantity > 1:
        item.quantity -= 1

    item.save()
    return redirect('cart')
from django.shortcuts import render

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def services(request):
    return render(request, "services.html")
