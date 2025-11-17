from django.contrib import admin
from .models import Enterprise


@admin.register(Enterprise)
class EnterpriseAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "city_display", "created_at")
    search_fields = ("name", "document", "address_city")
    readonly_fields = ("domain", "created_at", "updated_at")
    ordering = ("name",)

    fieldsets = (
        ("Informações Básicas", {
            "fields": ("name", "document", "description", "domain", )
        }),
        ("Endereço", {
            "fields": (
                "address_street",
                "address_number",
                "address_neighborhood",
                "address_city",
                "address_state",
                "address_zipcode",
            )
        }),
        ("Informações do Sistema", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    # Exibe cidade resumida na tabela
    def city_display(self, obj):
        if obj.address_city and obj.address_state:
            return f"{obj.address_city}/{obj.address_state}"
        return "-"
    city_display.short_description = "Cidade"

    # Domínio vem do contrato
    def domain(self, obj):
        return obj.contract.domain if obj.contract else "-"
    domain.short_description = "Domínio"
