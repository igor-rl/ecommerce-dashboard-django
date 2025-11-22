from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from organization.models import Enterprise
from clientes.models import Client
from django.core.exceptions import ValidationError

# ============================================================
# APPOINTMENT
# ============================================================
class Appointment(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        related_name="appointmentEnterprise",
        verbose_name="Enterprise",
    )

    name = models.CharField(max_length=150, verbose_name="Nome")

    slug = models.SlugField(max_length=160, blank=True, editable=False)

    description = models.TextField(blank=True, verbose_name="Descrição")

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.01,
        null=True,
        verbose_name="Preço (R$)"
    )

    duration = models.PositiveIntegerField(
        default=30,
        verbose_name="Duração (minutos)",
        help_text="Tempo estimado do atendimento, em minutos (ex: 30, 45, 60)"
    )

    is_active = models.BooleanField(default=True, verbose_name="Visível")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Tipo de Atendimento"
        verbose_name_plural = "Tipos de Atendimentos"
        ordering = ["name"]
        unique_together = ("enterprise", "name")

    def clean(self):
        if not self.slug:
            self.slug = slugify(self.name)

        if isinstance(self.price, str):
            clean = (
                self.price.replace("R$", "")
                .replace(".", "")
                .replace(",", ".")
                .strip()
            )
            try:
                self.price = Decimal(clean or "0.00")
            except InvalidOperation:
                self.price = Decimal("0.00")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def formatted_price(self):
        if self.price is None:
            return "R$ 0,00"
        formatted = f"R$ {self.price:,.2f}"
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")

    def __str__(self):
        return self.name


# ============================================================
# WORKER
# ============================================================
class Worker(models.Model):
    """
    Representa um profissional vinculado a um usuário do painel.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        related_name="workerEnterprise",
        verbose_name="Enterprise",
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="worker_profile",
        verbose_name="Usuário do Painel"
    )

    appointments = models.ManyToManyField(
        Appointment,
        related_name="workers",
        blank=True,
        verbose_name="Atendimentos"
    )

    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Agenda"
        verbose_name_plural = "Agendas"
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# ============================================================
# WORKER AVAILABILITY
# ============================================================
class WorkerAvailability(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        related_name="aworkerAvailabilityEnterprise",
        verbose_name="Enterprise",
    )

    # 🔥 Cada worker só pode ter uma disponibilidade
    worker = models.OneToOneField(
        Worker,
        on_delete=models.CASCADE,
        related_name="availability",
        verbose_name="Agenda",
    )

    # 🔥 JSONFields SEM null (evita "None" no banco)
    monday = models.JSONField(default=list, blank=True, verbose_name="Monday")
    tuesday = models.JSONField(default=list, blank=True, verbose_name="Tuesday")
    wednesday = models.JSONField(default=list, blank=True, verbose_name="Wednesday")
    thursday = models.JSONField(default=list, blank=True, verbose_name="Thursday")
    friday = models.JSONField(default=list, blank=True, verbose_name="Friday")
    saturday = models.JSONField(default=list, blank=True, verbose_name="Saturday")
    sunday = models.JSONField(default=list, blank=True, verbose_name="Sunday")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        verbose_name = "Disponibilidade"
        verbose_name_plural = "Disponibilidade"
        db_table = "worker_availability"
        constraints = [
            models.UniqueConstraint(fields=["worker"], name="unique_worker_availability")
        ]

    def __str__(self):
        if self.worker and self.worker.user:
            return f"{self.worker.user.get_full_name() or self.worker.user.username} ({self.worker.user.email})"
        return f"Worker Availability #{self.id}"


# ============================================================
# AGENDAMENTO
# ============================================================
class Scheduling(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Empresa",
    )

    worker = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Profissional / Agenda",
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="scheduling",
        verbose_name="Cliente"
    )

    appointments = models.ManyToManyField(
        Appointment,
        related_name="bookings",
        verbose_name="Tipos de Atendimento"
    )

    date = models.DateField(verbose_name="Data")
    start_time = models.TimeField(verbose_name="Início")

    end_time = models.TimeField(
        verbose_name="Horário de Fim",
        blank=True,
        null=True
    )

    duration = models.PositiveIntegerField(
        default=0,
        verbose_name="Duração Total (min)"
    )

    notes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.worker} - {self.date} {self.start_time}"

    # ==============================================================
    # 🔥 CALCULA DURAÇÃO TOTAL + END_TIME
    # ==============================================================

    def update_duration_and_end_time(self):
        total_minutes = sum(a.duration for a in self.appointments.all())
        self.duration = total_minutes

        if self.start_time and self.date and total_minutes > 0:
            start_dt = datetime.combine(self.date, self.start_time)
            end_dt = start_dt + timedelta(minutes=total_minutes)
            self.end_time = end_dt.time()
        else:
            self.end_time = None

    # ==============================================================
    # 🔥 Garante janela existente (cria se necessário)
    # ==============================================================

    def ensure_scheduling_window(self):
        worker = self.worker
        date = self.date

        window = SchedulingWindow.objects.filter(worker=worker, date=date).first()
        if window:
            return window

        availability = getattr(worker, "availability", None)
        if not availability:
            return None

        weekday = date.weekday()
        day_keys = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]

        day_field = day_keys[weekday]
        intervals_raw = getattr(availability, day_field, [])

        if not intervals_raw:
            return None

        window = SchedulingWindow.objects.create(
            enterprise_id=worker.enterprise_id,
            worker=worker,
            date=date
        )

        # Criar intervalos válidos
        for interval in intervals_raw:
            if not isinstance(interval, (list, tuple)) or len(interval) != 2:
                continue

            start_raw, end_raw = interval

            try:
                start_time = datetime.strptime(start_raw, "%H:%M").time()
                end_time = datetime.strptime(end_raw, "%H:%M").time()
            except Exception:
                continue

            if end_time <= start_time:
                continue

            SchedulingWindowInterval.objects.create(
                window=window,
                start_time=start_time,
                end_time=end_time
            )

        # Se não criou intervalos válidos, remover janela
        if not window.intervals.exists():
            window.delete()
            return None

        return window

    # ==============================================================
    # 🔥 VALIDAÇÃO
    # ==============================================================

    def clean(self):
        super().clean()

        window = self.ensure_scheduling_window()

        if not window:
            raise ValidationError("Não há disponibilidade cadastrada para este trabalhador neste dia.")

        intervals = window.intervals.all()
        if not intervals:
            raise ValidationError("Este dia não possui janelas de agendamento.")

        # Se start_time ainda não foi definido pelo form, pula validação
        if self.start_time is None:
            return

        # Validar se o horário está dentro de uma janela
        valid = False
        for interval in intervals:
            if interval.start_time <= self.start_time < interval.end_time:
                valid = True
                break

        if not valid:
            raise ValidationError(
                f"O horário {self.start_time} está fora da janela disponível do trabalhador."
            )

    # ==============================================================
    # 🔥 Salvar + recálculo
    # ==============================================================

    def save(self, *args, **kwargs):
        self.full_clean()     # chama clean()
        super().save(*args, **kwargs)

        # Garante que a janela exista para agendamentos futuros
        self.ensure_scheduling_window()




# ============================================================
# JANELA DE AGENDAMENTO
# ============================================================
class SchedulingWindow(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        related_name="scheduling_windows"
    )

    worker = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        related_name="scheduling_windows"
    )

    date = models.DateField()

    class Meta:
        unique_together = (("worker", "date"),)
        verbose_name = "Scheduling Window"
        verbose_name_plural = "Scheduling Windows"
        ordering = ("date",)

    def __str__(self):
        return f"{self.worker} — {self.date}"

    def generate_slots(self, appointment_duration_minutes):
        """
        Gera slots disponíveis com base nas janelas e duração do agendamento.
        """
        slots = []

        for interval in self.intervals.all():
            start_dt = datetime.combine(self.date, interval.start_time)
            end_dt   = datetime.combine(self.date, interval.end_time)

            duration = timedelta(minutes=appointment_duration_minutes)
            current = start_dt

            while current + duration <= end_dt:
                slots.append(current.time())
                current += duration

        return slots


# ============================================================
# INTERVALO DA JANELA DE AGENDAMENTO 
# ============================================================
class SchedulingWindowInterval(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    window = models.ForeignKey(
        SchedulingWindow,
        on_delete=models.CASCADE,
        related_name="intervals"
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    duration = models.PositiveIntegerField(editable=False)

    class Meta:
        ordering = ("start_time",)

    def save(self, *args, **kwargs):
        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = datetime.combine(datetime.today(), self.end_time)

        if end_dt <= start_dt:
            raise ValueError("end_time must be greater than start_time")

        delta = end_dt - start_dt
        self.duration = int(delta.total_seconds() // 60)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.start_time}–{self.end_time} ({self.duration} min)"
