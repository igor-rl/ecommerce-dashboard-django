from decimal import Decimal, InvalidOperation
from pyexpat import model
import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

from organization.models import Enterprise

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
  
  name = models.CharField(
    max_length=150,
    unique=True,
    verbose_name="Nome"
  )

  slug = models.SlugField(
    max_length=160,
    unique=True,
    blank=True,
    editable=False
  )

  description = models.TextField(
    blank=True,
    verbose_name="Descrição"
  )

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

  is_active = models.BooleanField(
    default=True,
    verbose_name="Visível"
  )
  
  created_at = models.DateTimeField(
    auto_now_add=True,
    verbose_name="Criado em"
  )

  updated_at = models.DateTimeField(
    auto_now=True,
    verbose_name="Atualizado em"
  )

  class Meta:
    verbose_name = "Tipo de Atendimento"
    verbose_name_plural = "Tipos de Atendimentos"
    ordering = ["name"]

  def clean(self):
    """Gera o slug automaticamente e garante formato numérico."""
    if not self.slug:
      self.slug = slugify(self.name)

    # Garante que price sempre seja Decimal
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
      self.full_clean()  # chama clean() antes de salvar
      super().save(*args, **kwargs)

  @property
  def formatted_price(self):
    """Retorna o preço formatado em R$."""
    if self.price is None:
        return "R$ 0,00"
    formatted = f"R$ {self.price:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")

  def __str__(self):
        return self.name 

# WORKER

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

  is_active = models.BooleanField(
    default=True,
    verbose_name="Ativo"
  )

  created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

  class Meta:
    verbose_name = "Colaborador"
    verbose_name_plural = "Colaboradores"
    ordering = ["-created_at"]

  def __str__(self):
    return self.user.get_full_name() or self.user.username

# WorkerAvailability

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

    worker = models.OneToOneField(
        "Worker",
        on_delete=models.CASCADE,
        related_name="availability",
        verbose_name="Colaborador",
    )

    monday = models.JSONField(default=list, verbose_name="Monday", blank=True, null=True)
    tuesday = models.JSONField(default=list, verbose_name="Tuesday", blank=True, null=True)
    wednesday = models.JSONField(default=list, verbose_name="Wednesday", blank=True, null=True)
    thursday = models.JSONField(default=list, verbose_name="Thursday", blank=True, null=True)
    friday = models.JSONField(default=list, verbose_name="Friday", blank=True, null=True)
    saturday = models.JSONField(default=list, verbose_name="Saturday", blank=True, null=True)
    sunday = models.JSONField(default=list, verbose_name="Sunday", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        verbose_name = "Disponibilidade"
        verbose_name_plural = "Disponibilidade"
        db_table = "worker_availability"  # força o nome da tabela em inglês

    def __str__(self):
        # mostra o nome do colaborador e e-mail
        if self.worker and self.worker.user:
            return f"{self.worker.user.get_full_name() or self.worker.user.username} ({self.worker.user.email})"
        return f"Worker Availability #{self.id}"
