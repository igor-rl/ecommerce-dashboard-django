from decimal import Decimal, InvalidOperation
import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from organization.models import Enterprise


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
