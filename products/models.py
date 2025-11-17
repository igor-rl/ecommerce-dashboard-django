from decimal import Decimal, InvalidOperation
import uuid
from django.db import models
from django.utils.text import slugify

from organization.models import Enterprise


class Product(models.Model):
  """
  Representa um produto disponível na plataforma de e-commerce.
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
      related_name="productEnterprise",
      verbose_name="Enterprise",
  )

  name = models.CharField(
    max_length=150,
    unique=True,
    verbose_name="Nome do Produto"
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

  stock = models.PositiveIntegerField(
    default=0,
    verbose_name="Estoque"
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
      verbose_name = "Produto"
      verbose_name_plural = "Produtos"
      ordering = ["-created_at"]

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
