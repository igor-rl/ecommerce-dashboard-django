from django.contrib import admin
from django.utils.html import format_html
from django import forms
import traceback

from schedule.domain.services.available_time_service import AvailableTimeService
from schedule.domain.services.scheduling_service import SchedulingService
from schedule.forms import AppointmentForm, SchedulingAdminForm, WorkerAvailabilityForm
from .models import Appointment, Worker, WorkerAvailability, Scheduling
from organization.models import Enterprise, Member
from clientes.models import Client


# ============================================================
# 🔥 MIXIN — Filtro automático + domínio visível
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

    def get_enterprise_domain(self, obj):
        return obj.enterprise.domain if obj.enterprise else "-"
    get_enterprise_domain.short_description = "Domínio"
    get_enterprise_domain.admin_order_field = "enterprise__domain"

    def get_list_display(self, request):
        base = list(self.list_display)

        if not request.user.is_superuser:
            return tuple(base)

        name_like = ["name", "get_user_full_name", "worker_email"]
        insert_after = next((f for f in name_like if f in base), None)

        if insert_after:
            idx = base.index(insert_after) + 1
            base.insert(idx, "get_enterprise_domain")
        else:
            base.insert(0, "get_enterprise_domain")

        return tuple(base)


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
        formatted = f"R$ {obj.price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return formatted
    get_price_display.short_description = "Preço"

    @staticmethod
    def get_created_short(obj):
        return obj.created_at.strftime("%d/%m/%y %H:%M") if obj.created_at else "-"
    get_created_short.short_description = "Criado em"

    def save_model(self, request, obj, form, change):

        # Apenas usuários normais precisam deste ajuste
        if not request.user.is_superuser:
            enterprise_id = request.session.get("enterprise_id")
            obj.enterprise_id = enterprise_id

        # Agora sim salva
        super().save_model(request, obj, form, change)


# ============================================================
# WORKER ADMIN
# ============================================================
@admin.register(Worker)
class WorkerAdmin(EnterpriseFilteredAdminMixin, admin.ModelAdmin):

    list_display = ("get_user_full_name", "get_appointments_names", "is_active", "get_created_short")
    list_filter = ("is_active", "created_at")
    search_fields = ("user__username", "user__first_name", "user__last_name", "appointments__name")
    ordering = ("-created_at",)

    class Media:
        js = ("js/filter-by-enterprise.js",)

    # --------------------------------------------
    # Helper central: sempre acha a enterprise certa
    # --------------------------------------------
    def _get_enterprise_id(self, request, obj=None):
        return (
            request.GET.get("enterprise_selected")
            or (obj.enterprise_id if obj else None)
            or request.session.get("enterprise_id")
        )

    # --------------------------------------------
    # Mantém enterprise selecionada (superuser e normal)
    # --------------------------------------------
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        enterprise_id = self._get_enterprise_id(request, obj)

        # se o campo existir no form, seta initial
        if enterprise_id and "enterprise" in form.base_fields:
            form.base_fields["enterprise"].initial = enterprise_id

        return form

    # --------------------------------------------
    # FK user filtrado pela enterprise correta
    # --------------------------------------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "user":
            enterprise_id = self._get_enterprise_id(request)

            if enterprise_id:
                member_ids = Member.objects.filter(
                    enterprise_id=enterprise_id
                ).values_list("user_id", flat=True)

                UserModel = db_field.remote_field.model
                kwargs["queryset"] = UserModel.objects.filter(id__in=member_ids)
            else:
                kwargs["queryset"] = db_field.remote_field.model.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # --------------------------------------------
    # M2M appointments filtrado pela enterprise correta
    # --------------------------------------------
    def formfield_for_manytomany(self, db_field, request, **kwargs):

        if db_field.name == "appointments":
            enterprise_id = self._get_enterprise_id(request)

            if enterprise_id:
                kwargs["queryset"] = Appointment.objects.filter(
                    enterprise_id=enterprise_id
                )
            else:
                kwargs["queryset"] = Appointment.objects.none()

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # --------------------------------------------
    # save_model mantém sua lógica original
    # --------------------------------------------
    def save_model(self, request, obj, form, change):

        if not request.user.is_superuser:
            obj.enterprise_id = request.session.get("enterprise_id")

        member = Member.objects.filter(user=obj.user).first()
        if member:
            obj.enterprise_id = member.enterprise_id

        super().save_model(request, obj, form, change)

    # --------------------------------------------
    # Display helpers
    # --------------------------------------------
    def get_user_full_name(self, obj):
        full_name = obj.user.get_full_name().strip()
        return full_name or obj.user.username
    get_user_full_name.short_description = "Nome"

    def get_appointments_names(self, obj):
        names = [a.name for a in obj.appointments.all()]
        return ", ".join(names) if names else "-"
    get_appointments_names.short_description = "Atendimentos"

    @staticmethod
    def get_created_short(obj):
        return obj.created_at.strftime("%d/%m/%y %H:%M") if obj.created_at else "-"
    get_created_short.short_description = "Criado em"


# ============================================================
# WORKER AVAILABILITY ADMIN
# ============================================================
@admin.register(WorkerAvailability)
class WorkerAvailabilityAdmin(EnterpriseFilteredAdminMixin, admin.ModelAdmin):

    form = WorkerAvailabilityForm
    readonly_fields = ["created_at", "updated_at"]

    class Media:
        css = {'all': ('css/custom.css',)}
        js = ('js/time-mask.js',)

    list_display = ["worker_email", "display_availability", "created_at", "updated_at"]
    search_fields = ["worker__user__email", "worker__user__first_name", "worker__user__last_name"]

    # TORNA O WORKER ESCONDIDO NA EDIÇÃO, MAS ENVIADO NO POST
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if obj:  # edição
            form.base_fields["worker"].widget = forms.HiddenInput()
            form.base_fields["worker"].initial = obj.worker_id

        return form

    # SALVAR ENTERPRISE SEMPRE DO WORKER
    def save_model(self, request, obj, form, change):

        try:
            if obj.worker:
                obj.enterprise_id = obj.worker.enterprise_id

            super().save_model(request, obj, form, change)

        except Exception:
            print("\n\n===== ERROR TRACEBACK =====")
            traceback.print_exc()
            print("===========================\n\n")
            raise

    # READONLY FIELDS — NÃO REMOVE WORKER!
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields

    # ======================================================
    # UI
    # ======================================================
    def worker_email(self, obj):
        return obj.worker.user.email if obj.worker else "-"
    worker_email.short_description = "E-mail"

    fieldsets = (
        ('Agenda', {'fields': ('worker',)}),

        ('Segunda-feira', {
            'fields': (('monday_start_at', 'monday_finish_at'),
                       ('monday_start_at_b', 'monday_finish_at_b')),
        }),

        ('Terça-feira', {
            'fields': (('tuesday_start_at', 'tuesday_finish_at'),
                       ('tuesday_start_at_b', 'tuesday_finish_at_b')),
        }),

        ('Quarta-feira', {
            'fields': (('wednesday_start_at', 'wednesday_finish_at'),
                       ('wednesday_start_at_b', 'wednesday_finish_at_b')),
        }),

        ('Quinta-feira', {
            'fields': (('thursday_start_at', 'thursday_finish_at'),
                       ('thursday_start_at_b', 'thursday_finish_at_b')),
        }),

        ('Sexta-feira', {
            'fields': (('friday_start_at', 'friday_finish_at'),
                       ('friday_start_at_b', 'friday_finish_at_b')),
        }),

        ('Sábado', {
            'fields': (('saturday_start_at', 'saturday_finish_at'),
                       ('saturday_start_at_b', 'saturday_finish_at_b')),
        }),

        ('Domingo', {
            'fields': (('sunday_start_at', 'sunday_finish_at'),
                       ('sunday_start_at_b', 'sunday_finish_at_b')),
        }),

        ('Informações do Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

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
        for label, turnos in dias:
            if not turnos:
                continue

            faixas = []
            for t in turnos:
                if t and all(t):
                    inicio, fim = t
                    faixas.append(f"<span style='color:#f5b342;'>{inicio}–{fim}</span>")

            if faixas:
                html.append(
                    f"<div style='margin-bottom:3px;'><strong>{label}:</strong> {' / '.join(faixas)}</div>"
                )

        return format_html("".join(html)) if html else "–"

    display_availability.short_description = "Horários"


# ============================================================
# SCHEDULING ADMIN
# ============================================================
@admin.register(Scheduling)
class SchedulingAdmin(EnterpriseFilteredAdminMixin, admin.ModelAdmin):
    form = SchedulingAdminForm

    list_display = (
        "date",
        "start_time",
        "end_time",
        "duration",
        "worker",
        "client",
    )

    ordering = ("date", "start_time")
    list_filter = ("date",)
    search_fields = ("worker__user__username", "client__name")
    filter_horizontal = ("appointments",)

    class Media:
        js = (
            "/static/js/scheduling-filter-by-worker.js",
            "/static/js/scheduling-edit-selected-appointments.js",
        )

    # ------------------------------------------------------------
    # Filtrar FK conforme enterprise
    # ------------------------------------------------------------
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        if not request.user.is_superuser:
            enterprise_id = request.session.get("enterprise_id")

            if "worker" in form.base_fields:
                form.base_fields["worker"].queryset = Worker.objects.filter(
                    enterprise_id=enterprise_id
                )

            if "client" in form.base_fields:
                form.base_fields["client"].queryset = Client.objects.filter(
                    enterprise_id=enterprise_id
                )

        return form

    # ------------------------------------------------------------
    # Filtrar tipos de atendimento pela agenda (worker)
    # ------------------------------------------------------------
    def formfield_for_manytomany(self, db_field, request, **kwargs):

        if db_field.name == "appointments":
            worker_id = request.GET.get("worker")

            if worker_id:
                kwargs["queryset"] = Appointment.objects.filter(
                    workers__id=worker_id
                ).distinct()
            else:
                kwargs["queryset"] = Appointment.objects.none()

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # ------------------------------------------------------------
    # Campos exibidos (inclui schedule_option)
    # ------------------------------------------------------------
    def get_fields(self, request, obj=None):
        fields = [
            "worker",
            "client",
            "appointments",
            "date",
            "schedule_option",
            "notes",
        ]

        if request.user.is_superuser:
            fields.insert(0, "enterprise")

        return fields

    # ------------------------------------------------------------
    # Fieldsets visuais
    # ------------------------------------------------------------
    def get_fieldsets(self, request, obj=None):
        return [
            ("Agendamento", {"fields": self.get_fields(request, obj)})
        ]

    # ------------------------------------------------------------
    # Enterprise automático + Redis Lock via Service
    # ------------------------------------------------------------
    def save_model(self, request, obj, form, change):

        if not request.user.is_superuser:
            obj.enterprise_id = request.session.get("enterprise_id")

        # Em criação (ADD) usamos o service para pegar o lock
        if not change:
            created = SchedulingService.create(
                worker_id=obj.worker_id,
                client_id=obj.client_id,
                appointments=list(form.cleaned_data["appointments"].values_list("id", flat=True)),
                date=obj.date,  # pode vir date ou string, service normaliza
                start_time=obj.start_time,
                enterprise_id=obj.enterprise_id,
                notes=obj.notes
            )

            # garantir que o admin continue o fluxo normal
            obj.pk = created.pk
            form.instance = created
            return

        # Em edição mantém comportamento original
        super().save_model(request, obj, form, change)

    # ------------------------------------------------------------
    # Calcula duração-total e end_time (mantido)
    # ------------------------------------------------------------
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        scheduling = form.instance
        scheduling.update_duration_and_end_time()
        scheduling.save(update_fields=["duration", "end_time"])
