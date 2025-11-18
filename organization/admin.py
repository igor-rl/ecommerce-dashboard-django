from django.contrib import admin
from .models import Enterprise
from organization.models import Member, Enterprise
from django.utils.html import format_html


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

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Superusuário vê todas as empresas
        if request.user.is_superuser:
            return qs

        # Usuário comum → filtrar pela enterprise ativa
        enterprise_id = request.session.get("enterprise_id")

        if enterprise_id:
            return qs.filter(id=enterprise_id)

        # Se não tiver enterprise na sessão, não mostrar nada
        return qs.none()

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


# ============================================================
# 🔥 Mix-in para filtrar por enterprise (o mesmo usado antes)
# ============================================================
class EnterpriseFilteredAdminMixin:
    """Limita dados ao enterprise da sessão se não for superusuário."""

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

    # Exibir badge estilizada para status do convite
    def invite_status_badge(self, obj):
        colors = {
            "sent": "#3498db",       # azul
            "not_sent": "#7f8c8d",   # cinza
            "accepted": "#2ecc71",   # verde
            "rejected": "#e74c3c",   # vermelho
        }

        color = colors.get(obj.invite_status, "#7f8c8d")

        return format_html(
            f"<span style='padding:4px 8px; border-radius:4px; background:{color}; color:white;'>"
            f"{obj.get_invite_status_display()}</span>"
        )

    invite_status_badge.short_description = "Invite Status"

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Identificação", {
            "fields": ("name", "email", "cpf"),
        }),

        ("Configurações de Acesso", {
            "fields": ("role", "invite_status"),
        }),

        ("Empresa", {
            "fields": ("enterprise",),
        }),

        ("Sistema", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
