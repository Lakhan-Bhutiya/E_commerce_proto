from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('store/', views.store, name='store'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:pid>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),

    path('product/<int:pid>/', views.product_detail, name='product_detail'),
    path('cart-update/<int:cid>/<str:action>/', views.update_cart_qty, name='cart_update'),

    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
]
