from django.contrib import admin
from django.utils.html import format_html

from organization.models import Member, Enterprise


# ============================================================
# ENTERPRISE ADMIN
# ============================================================
@admin.register(Enterprise)
class EnterpriseAdmin(admin.ModelAdmin):

    list_display = ("name", "domain_display", "city_display", "created_at")
    search_fields = ("name", "document", "address_city")
    readonly_fields = ("domain_display", "created_at", "updated_at")
    ordering = ("name",)

    fieldsets = (
        ("Informações Básicas", {
            "fields": ("name", "document", "description", "domain_display")
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

    # 🔥 Exibir domínio vindo do contrato
    def domain_display(self, obj):
        return obj.contract.domain if hasattr(obj, "contract") and obj.contract else "-"
    domain_display.short_description = "Domínio"

    # Exibe cidade resumida
    def city_display(self, obj):
        if obj.address_city and obj.address_state:
            return f"{obj.address_city}/{obj.address_state}"
        return "-"
    city_display.short_description = "Cidade"

    # Filtra por enterprise ativa para usuários comuns
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        enterprise_id = request.session.get("enterprise_id")
        if enterprise_id:
            return qs.filter(id=enterprise_id)
        return qs.none()



# ============================================================
# 🔥 Mixin usado em todas as Admins que dependem de Enterprise
# ============================================================
class EnterpriseFilteredAdminMixin:

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        enterprise_id = request.session.get("enterprise_id")
        return qs.filter(enterprise_id=enterprise_id)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "enterprise" and not request.user.is_superuser:
            enterprise_id = request.session.get("enterprise_id")
            kwargs["queryset"] = Enterprise.objects.filter(id=enterprise_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if hasattr(obj, "enterprise") and not request.user.is_superuser:
            obj.enterprise_id = request.session.get("enterprise_id")
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        if not request.user.is_superuser:
            return [f for f in fields if f != "enterprise"]

        return fields

    # =========================================
    # 🔥 Exibir domínio em todas as Admins
    # =========================================
    def get_enterprise_domain(self, obj):
        if hasattr(obj.enterprise, "contract") and obj.enterprise.contract:
            return obj.enterprise.contract.domain
        return "-"
    get_enterprise_domain.short_description = "Domínio"

    # Colocar domínio **após o nome** (ou equivalente)
    def get_list_display(self, request):
        base = list(self.list_display)

        if not request.user.is_superuser:
            return tuple(base)

        name_like_fields = ["name", "email", "get_user_full_name"]

        insert_after = None
        for fld in name_like_fields:
            if fld in base:
                insert_after = fld
                break

        if insert_after:
            idx = base.index(insert_after) + 1
            base.insert(idx, "get_enterprise_domain")
        else:
            base.insert(0, "get_enterprise_domain")

        return tuple(base)



# ============================================================
# MEMBER ADMIN
# ============================================================
@admin.register(Member)
class MemberAdmin(EnterpriseFilteredAdminMixin, admin.ModelAdmin):

    list_display = (
        "name",
        "email",
        "role",
        "invite_status_badge",
        "created_at",
        "updated_at",
    )

    list_filter = ("role", "invite_status", "created_at")
    search_fields = ("name", "email", "cpf")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Identificação", {
            "fields": ("name", "email", "cpf")
        }),
        ("Configurações de Acesso", {
            "fields": ("role", "invite_status")
        }),
        ("Empresa", {
            "fields": ("enterprise",)
        }),
        ("Sistema", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    # =============================================
    # Badge de status
    # =============================================
    def invite_status_badge(self, obj):
        colors = {
            "sent": "#3498db",
            "not_sent": "#7f8c8d",
            "accepted": "#2ecc71",
            "rejected": "#e74c3c",
        }

        return format_html(
            f"<span style='padding:4px 8px; border-radius:4px; background:{colors.get(obj.invite_status, '#7f8c8d')}; color:white;'>"
            f"{obj.get_invite_status_display()}</span>"
        )

    invite_status_badge.short_description = "Status do Convite"
