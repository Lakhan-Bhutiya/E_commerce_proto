"""
Custom AdminSite that adds a dashboard with entity counts on the admin index page.
"""
from django.contrib import admin


class DashboardAdminSite(admin.AdminSite):
    index_template = "admin/dashboard_index.html"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Build counts for every registered model
        dashboard_counts = []
        for model, model_admin in self._registry.items():
            try:
                count = model.objects.count()
            except Exception:
                count = 0
            opts = model._meta
            # Use model's admin URL for "View" link
            info = (opts.app_label, opts.model_name)
            dashboard_counts.append({
                "label": opts.verbose_name_plural.title(),
                "model_name": opts.model_name,
                "app_label": opts.app_label,
                "count": count,
                "info": info,
            })
        extra_context["dashboard_counts"] = dashboard_counts
        return super().index(request, extra_context)
