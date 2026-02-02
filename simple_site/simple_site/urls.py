from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from simple_site.admin_site import DashboardAdminSite
from pages.admin import register_pages_models

# Custom admin site with dashboard counts
admin_site = DashboardAdminSite(name="admin")
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
register_pages_models(admin_site)

urlpatterns = [
    path("admin/", admin_site.urls),
    path("", include("pages.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
