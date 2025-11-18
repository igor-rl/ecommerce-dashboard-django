from django.contrib import admin
from django.contrib.admin import AdminSite
from organization.models import Enterprise


class CustomAdminSite(AdminSite):
    site_header = "Administração do Django"
    site_title = "Administração do Django"
    index_title = "Administração"

    def each_context(self, request):
        ctx = super().each_context(request)

        enterprise_id = request.session.get("enterprise_id")
        if enterprise_id:
            try:
                enterprise = Enterprise.objects.get(id=enterprise_id)
                ctx["site_header"] = enterprise.name
                ctx["site_title"] = enterprise.name
                ctx["index_title"] = "Administração"
            except Enterprise.DoesNotExist:
                pass

        return ctx


custom_admin_site = CustomAdminSite(name="custom_admin")

# --- clonar models do admin padrão ---
for model, model_admin in admin.site._registry.items():
    try:
        custom_admin_site.register(model, model_admin.__class__)
    except admin.sites.AlreadyRegistered:
        pass
