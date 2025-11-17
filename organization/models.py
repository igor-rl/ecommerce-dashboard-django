import uuid
from django.db import models
from management.models import Contract


class Enterprise(models.Model):
    """
    Representa a enterprise vinculada a um contrato.
    Só pode existir uma enterprise por contrato.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name="enterprise",
        verbose_name="Contrato"
    )

    name = models.CharField(
        max_length=150,
        verbose_name="Nome da Enterprise"
    )

    document = models.CharField(
        max_length=18,
        blank=True,
        null=True,
        verbose_name="Documento (CNPJ ou CPF)"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição da Enterprise"
    )

    address_street = models.CharField(max_length=150, blank=True, null=True, verbose_name="Rua")
    address_number = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    address_neighborhood = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    address_city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    address_state = models.CharField(max_length=2, blank=True, null=True, verbose_name="UF")
    address_zipcode = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Enterprise"
        verbose_name_plural = "Enterprises"
        ordering = ["name"]

    def __str__(self):
        return self.name

    # 💡 Exibe o domínio (vem do contrato)
    @property
    def domain(self):
        return self.contract.domain if self.contract else "-"
