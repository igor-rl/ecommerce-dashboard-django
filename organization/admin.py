from django.contrib import admin
from django.db.models import F, Value
from django.db.models.functions import Coalesce
from .models import Enterprise
from organization.models import Member, Enterprise, SchedulingConfig
from django.utils.html import format_html
from django.urls import reverse

# ============================================================
# ENTERPRISE ADMIN
# ============================================================
@admin.register(Enterprise)
class EnterpriseAdmin(admin.ModelAdmin):

    list_display = (
        "domain_display",
        "name",
        "city_display",
        "created_at",
    )

    search_fields = ("document", "address_city", "contract__domain")
    readonly_fields = ("domain", "created_at", "updated_at")

    ordering = ()  # usamos ordering no queryset

    fieldsets = (
        ("Informações Básicas", {
            "fields": ("document", "description", "domain"),
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

        qs = qs.annotate(
            contract_domain=Coalesce(F("contract__domain"), Value(""))
        ).order_by("contract_domain")

        if request.user.is_superuser:
            return qs

        enterprise_id = request.session.get("enterprise_id")
        if enterprise_id:
            return qs.filter(id=enterprise_id)

        return qs.none()

    def domain_display(self, obj):
        return obj.contract_domain or "-"
    domain_display.short_description = "Domínio"

    def city_display(self, obj):
        if obj.address_city and obj.address_state:
            return f"{obj.address_city}/{obj.address_state}"
        return "-"
    city_display.short_description = "Cidade"


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
        "email",
        "role",
        "invite_status_badge",
        "created_at",
        "updated_at",
    )

    list_filter = ("role", "invite_status", "created_at")
    search_fields = ("email", "cpf")
    ordering = ("email",)

    # ============
    # Domínio da empresa (superuser only)
    # ============
    def domain_display(self, obj):
        if obj.enterprise and obj.enterprise.contract:
            return obj.enterprise.contract.domain
        return "-"
    domain_display.short_description = "Domínio"

    def get_list_display(self, request):
        base = list(self.list_display)

        if request.user.is_superuser:
            # Sempre aparece primeiro
            return ["domain_display"] + base

        return base

    # ============
    # Badge do status
    # ============
    def invite_status_badge(self, obj):
        colors = {
            "sent": "#3498db",
            "not_sent": "#7f8c8d",
            "accepted": "#2ecc71",
            "rejected": "#e74c3c",
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
            "fields": ("email", "cpf"),
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


# ============================================================
# SCHEDULING CONFIG ADMIN
# ============================================================
@admin.register(SchedulingConfig)
class SchedulingConfigAdmin(EnterpriseFilteredAdminMixin, admin.ModelAdmin):

    list_display = ("overlap_tolerance",)
    ordering = ("enterprise__contract__domain",)
    search_fields = ("enterprise__contract__domain",)

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Configuração de Agendamento", {
            "fields": ("enterprise", "overlap_tolerance"),
        }),
        ("Sistema", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    # --------------------------
    # Botão EDITAR apenas para usuários comuns
    # --------------------------
    def edit_link(self, obj):
        url = reverse("admin:organization_schedulingconfig_change", args=[obj.pk])
        return format_html(f'<a class="button" href="{url}">Editar</a>')
    edit_link.short_description = "Editar"

    # --------------------------
    # Domínio visível só para superuser
    # --------------------------
    def domain_display(self, obj):
        if obj.enterprise and obj.enterprise.contract:
            return obj.enterprise.contract.domain
        return "-"
    domain_display.short_description = "Domínio"
    domain_display.admin_order_field = "enterprise__contract__domain"  # ✔ agora é ordenável!

    # --------------------------
    # List Display dinâmico
    # --------------------------
    def get_list_display(self, request):
        base = ["overlap_tolerance"]

        if request.user.is_superuser:
            # domínio aparece antes de tudo
            return ["domain_display"] + base

        # usuário comum → mostrar botão editar
        return ["edit_link"] + base

    # --------------------------
    # Filtros dinâmicos
    # --------------------------
    def get_list_filter(self, request):
        if request.user.is_superuser:
            # ✔ filtro por domínio só para superuser
            return ("enterprise__contract__domain",)

        return ()

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        # Usuário comum → remover 'enterprise' do fieldset
        if not request.user.is_superuser:
            new_fieldsets = []
            for title, opts in fieldsets:
                fields = opts.get("fields", ())
                # remove enterprise
                cleaned_fields = tuple(f for f in fields if f != "enterprise")
                new_fieldsets.append((title, {"fields": cleaned_fields, **{k: v for k, v in opts.items() if k != "fields"}}))
            return new_fieldsets

        return fieldsets
