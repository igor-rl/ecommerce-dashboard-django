from django.contrib import admin
from organization.admin import EnterpriseFilteredAdminMixin
from .models import Client


@admin.register(Client)
class ClientAdmin(EnterpriseFilteredAdminMixin, admin.ModelAdmin):

    list_display = ("name", "email", "cpf")
    search_fields = ("name", "email", "cpf")
    ordering = ("name",)

    # Domínio só aparece para superuser
    def domain_display(self, obj):
        if obj.enterprise and obj.enterprise.contract:
            return obj.enterprise.contract.domain
        return "-"
    domain_display.short_description = "Domínio"
    domain_display.admin_order_field = "enterprise__contract__domain"

    # -----------------------------
    # LISTA DINÂMICA
    # -----------------------------
    def get_list_display(self, request):
        base = ["name", "email", "cpf", "whatsapp"]
        if request.user.is_superuser:
            return ["domain_display"] + base
        return base

    # -----------------------------
    # FILTROS
    # -----------------------------
    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ("enterprise__contract__domain",)
        return ()

    # -----------------------------
    # REMOVER enterprise do FORM
    # -----------------------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "enterprise" and not request.user.is_superuser:
            return None
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # -----------------------------
    # FIELDSETS
    # -----------------------------
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ("Dados do Cliente", {
                "fields": ("name", "email", "cpf", "whatsapp")
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
            ("Sistema", {
                "fields": ("enterprise", "created_at", "updated_at"),
                "classes": ("collapse",),
            }),
        ]

        if not request.user.is_superuser:
            new_fieldsets = []
            for title, opts in fieldsets:
                fields = opts.get("fields", ())
                cleaned = tuple(f for f in fields if f != "enterprise")
                new_fieldsets.append((title, {**opts, "fields": cleaned}))
            return new_fieldsets

        return fieldsets

    readonly_fields = ("created_at", "updated_at")

    # -----------------------------
    # GARANTIR enterprise no SAVE
    # -----------------------------
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.enterprise_id = request.session.get("enterprise_id")
        super().save_model(request, obj, form, change)
