from .models import SiteUser

def logged_in_user(request):
    user = None
    if 'user_email' in request.session:
        user = SiteUser.objects.filter(
            email=request.session['user_email']
        ).first()

    return {'logged_user': user}
