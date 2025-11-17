from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import JsonResponse

from .models import Contract


# =============================
# 🔹 Contratos
# =============================
@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "domain",
        "user",
        "is_active",
        "is_valid_contract",
        "valid_until",
        "created_at",
    )
    search_fields = ("domain", "user__username", "user__email")
    ordering = ("-created_at",)

    fieldsets = (
        ("Informações do Contrato", {
            "fields": ("domain", "user", "is_active")
        }),
        ("Validade", {
            "fields": ("valid_until", "created_at"),
        }),
    )

    readonly_fields = ("created_at",)

    def is_valid_contract(self, obj):
        color = "green" if obj.is_valid else "red"
        label = "Válido" if obj.is_valid else "Expirado"
        return format_html(f"<b><span style='color:{color}'>{label}</span></b>")
    is_valid_contract.short_description = "Status"

    # =============================
    # 🔸 Validação dinâmica de domínio (AJAX)
    # =============================

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("check-domain/", self.admin_site.admin_view(self.check_domain_view), name="check-domain"),
        ]
        return custom_urls + urls

    def check_domain_view(self, request):
        """Endpoint usado para validar se o domínio está disponível."""
        domain = request.GET.get("domain", "").strip()
        if not domain:
            return JsonResponse({"available": False, "error": "Domínio não informado."})
        exists = Contract.objects.filter(domain=domain).exists()
        return JsonResponse({"available": not exists})
