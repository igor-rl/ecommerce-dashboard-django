from django.contrib import admin
from django.utils.safestring import mark_safe

from schedule.forms import AppointmentForm, WorkerAvailabilityForm
from .models import Appointment, Worker, WorkerAvailability
from organization.models import Enterprise


# ============================================================
# 🔥 MIXIN — Filtro automático por enterprise
# ============================================================
class EnterpriseFilteredAdminMixin:
    """Limita dados pela enterprise ativa (se não for superusuário)."""

    # 1. Filtra o queryset automaticamente
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        enterprise_id = request.session.get("enterprise_id")
        return qs.filter(enterprise_id=enterprise_id)

    # 2. Limita o campo enterprise no formulário
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "enterprise" and not request.user.is_superuser:
            enterprise_id = request.session.get("enterprise_id")
            kwargs["queryset"] = Enterprise.objects.filter(id=enterprise_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # 3. Enterprise é preenchido automaticamente ao salvar
    def save_model(self, request, obj, form, change):
        if hasattr(obj, "enterprise") and not request.user.is_superuser:
            obj.enterprise_id = request.session.get("enterprise_id")
        super().save_model(request, obj, form, change)

    # 4. Oculta enterprise do formulário para usuários comuns
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            return [f for f in fields if f != "enterprise"]
        return fields



# ============================================================
# APPOINTMENT ADMIN
# ============================================================
@admin.register(Appointment)
class AppointmentAdmin(EnterpriseFilteredAdminMixin, admin.ModelAdmin):

    form = AppointmentForm

    list_display = ("name", "get_price_display", "duration", "is_active", "get_created_short")
    list_display_links = ("name",)
    search_fields = ("name", "description")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("slug",)
    ordering = ("-created_at",)

    class Media:
        js = ("js/price_mask.js",)

    @staticmethod
    def get_price_display(obj):
        if obj.price is None:
            return "R$ 0,00"
        formatted = f"R$ {obj.price:,.2f}"
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    get_price_display.short_description = "Preço"
    get_price_display.admin_order_field = "price"

    @staticmethod
    def get_created_short(obj):
        if not obj.created_at:
            return "-"
        return obj.created_at.strftime("%d/%m/%y %H:%M")
    get_created_short.short_description = "Criado em"
    get_created_short.admin_order_field = "created_at"



# ============================================================
# WORKER ADMIN
# ============================================================
@admin.register(Worker)
class WorkerAdmin(EnterpriseFilteredAdminMixin, admin.ModelAdmin):

    list_display = ("get_user_full_name", "get_appointments_names", "is_active", "get_created_short")
    list_filter = ("is_active", "created_at")
    search_fields = ("user__username", "user__first_name", "user__last_name", "appointments__name")
    ordering = ("-created_at",)

    def get_user_full_name(self, obj):
        full_name = obj.user.get_full_name().strip()
        return full_name or obj.user.username
    get_user_full_name.short_description = "Nome do Usuário"
    get_user_full_name.admin_order_field = "user__first_name"

    def get_appointments_names(self, obj):
        names = [a.name for a in obj.appointments.all()]
        if not names:
            return "-"
        return ", ".join(names)
    get_appointments_names.short_description = "Atendimentos"

    @staticmethod
    def get_created_short(obj):
        if not obj.created_at:
            return "-"
        return obj.created_at.strftime("%d/%m/%y %H:%M")
    get_created_short.short_description = "Criado em"
    get_created_short.admin_order_field = "created_at"



# ============================================================
# WORKER AVAILABILITY ADMIN
# ============================================================
@admin.register(WorkerAvailability)
class WorkerAvailabilityAdmin(EnterpriseFilteredAdminMixin, admin.ModelAdmin):

    form = WorkerAvailabilityForm
    readonly_fields = ['created_at', 'updated_at']

    class Media:
        css = {'all': ('css/custom.css',)}
        js = ('js/time-mask.js',)

    list_display = ['worker_email', 'display_availability', 'created_at', 'updated_at']

    def worker_email(self, obj):
        return obj.worker.user.email if obj.worker and obj.worker.user else "-"
    worker_email.short_description = "E-mail"

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editando existente
            return self.readonly_fields + ['worker']
        return self.readonly_fields

    # AGRUPAMENTO ORGANIZADO POR DIAS
    fieldsets = (
        ('Agenda', {'fields': ('worker',)}),

        ('Segunda-feira', {
            'fields': (
                ('monday_start_at', 'monday_finish_at'),
                ('monday_start_at_b', 'monday_finish_at_b'),
            ),
        }),

        ('Terça-feira', {
            'fields': (
                ('tuesday_start_at', 'tuesday_finish_at'),
                ('tuesday_start_at_b', 'tuesday_finish_at_b'),
            ),
        }),

        ('Quarta-feira', {
            'fields': (
                ('wednesday_start_at', 'wednesday_finish_at'),
                ('wednesday_start_at_b', 'wednesday_finish_at_b'),
            ),
        }),

        ('Quinta-feira', {
            'fields': (
                ('thursday_start_at', 'thursday_finish_at'),
                ('thursday_start_at_b', 'thursday_finish_at_b'),
            ),
        }),

        ('Sexta-feira', {
            'fields': (
                ('friday_start_at', 'friday_finish_at'),
                ('friday_start_at_b', 'friday_finish_at_b'),
            ),
        }),

        ('Sábado', {
            'fields': (
                ('saturday_start_at', 'saturday_finish_at'),
                ('saturday_start_at_b', 'saturday_finish_at_b'),
            ),
        }),

        ('Domingo', {
            'fields': (
                ('sunday_start_at', 'sunday_finish_at'),
                ('sunday_start_at_b', 'sunday_finish_at_b'),
            ),
        }),

        ('Informações do Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # Render Bonita das Disponibilidades
    def display_availability(self, obj):
        dias = [
            ('Seg', obj.monday),
            ('Ter', obj.tuesday),
            ('Qua', obj.wednesday),
            ('Qui', obj.thursday),
            ('Sex', obj.friday),
            ('Sáb', obj.saturday),
            ('Dom', obj.sunday),
        ]

        html = []
        for dia, turnos in dias:
            if not turnos:
                continue
            faixas = []
            for t in turnos:
                if t and all(t):
                    inicio, fim = t
                    faixas.append(f"<span style='color:#f5b342;'>{inicio}–{fim}</span>")
            if faixas:
                html.append(
                    f"<div style='margin-bottom:3px;'><strong>{dia}:</strong> {' / '.join(faixas)}</div>"
                )

        if not html:
            return "–"

        return mark_safe("".join(html))
