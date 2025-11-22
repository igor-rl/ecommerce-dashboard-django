import uuid
from django.db import models
from django.core.exceptions import ValidationError
from organization.models import Enterprise


class Client(models.Model):
    """
    Cliente pertencente a uma Enterprise.
    Uma enterprise pode ter vários clientes.
    Email e CPF não podem se repetir dentro da mesma enterprise.
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
        related_name="clients",
        verbose_name="Empresa"
    )

    # ---- Dados principais ----
    name = models.CharField(
        max_length=150,
        verbose_name="Nome do Cliente"
    )

    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="E-mail"
    )

    cpf = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        verbose_name="CPF"
    )

    whatsapp = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="WhatsApp"
    )

    # ---- Endereço (opcional) ----
    address_street = models.CharField(max_length=150, blank=True, null=True, verbose_name="Rua")
    address_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número")
    address_neighborhood = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    address_city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    address_state = models.CharField(max_length=2, blank=True, null=True, verbose_name="UF")
    address_zipcode = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["name"]

        constraints = [
            models.UniqueConstraint(
                fields=["enterprise", "email"],
                name="unique_client_email_per_enterprise"
            ),
            models.UniqueConstraint(
                fields=["enterprise", "cpf"],
                name="unique_client_cpf_per_enterprise"
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """
        Validações adicionais:
        - email não pode se repetir dentro da mesma empresa (se informado)
        - cpf não pode se repetir dentro da mesma empresa (se informado)
        """

        # ⚠️ Enterprise ainda não definido? (usuário normal criando)
        # Então NÃO validar agora — será preenchido no save_model
        if not self.enterprise_id:
            return

        # valida email
        if self.email:
            if Client.objects.filter(
                enterprise=self.enterprise,
                email=self.email
            ).exclude(id=self.id).exists():
                raise ValidationError({"email": "Este e-mail já está cadastrado nesta empresa."})

        # valida cpf
        if self.cpf:
            if Client.objects.filter(
                enterprise=self.enterprise,
                cpf=self.cpf
            ).exclude(id=self.id).exists():
                raise ValidationError({"cpf": "Este CPF já está cadastrado nesta empresa."})
