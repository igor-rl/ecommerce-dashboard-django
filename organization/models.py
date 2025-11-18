import uuid
from django.core.validators import validate_domain_name
from django.db import models
from management.models import Contract
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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
        verbose_name = "Empresa"
        verbose_name_plural = "Empresa"
        ordering = ["name"]

    def __str__(self):
        return self.name

    # 💡 Exibe o domínio (vem do contrato)
    @property
    def domain(self):
        return self.contract.domain if self.contract else "-"


class Member(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("partner", "Partner"),
        ("admin", "Admin"),
        ("employee", "Employee"),
        ("guest", "Guest"),
    ]

    INVITE_STATUS = [
        ("sent", "Sent"),
        ("not_sent", "Not Sent"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        related_name="members",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="memberships",
    )

    name = models.CharField(max_length=120)
    email = models.EmailField()
    cpf = models.CharField(max_length=14, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="guest")
    invite_status = models.CharField(max_length=12, choices=INVITE_STATUS, default="not_sent")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def clean(self):
        # Evita email duplicado
        if Member.objects.filter(
            enterprise=self.enterprise,
            email=self.email
        ).exclude(id=self.id).exists():
            raise ValidationError({"email": "Este e-mail já está cadastrado nesta empresa."})

        # Evita CPF duplicado
        if self.cpf and Member.objects.filter(
            enterprise=self.enterprise,
            cpf=self.cpf
        ).exclude(id=self.id).exists():
            raise ValidationError({"cpf": "Este CPF já está cadastrado nesta empresa."})


    class Meta:
        verbose_name = "Membro"
        verbose_name_plural = "Membros"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["enterprise", "email"],
                name="unique_member_per_enterprise_email"
            ),
            models.UniqueConstraint(
                fields=["enterprise", "cpf"],
                name="unique_member_per_enterprise_cpf"
            ),
        ]

    @property
    def id_enterprise(self):
        return self.enterprise_id

    def __str__(self):
        return f"{self.name} ({self.role})"


# TODO
# ------------------------
# Criar uma model para armazenar os tokens de convites com uma validate_domain_name

# fluxo >>>>
# Contratante cria um membro
# Clica no botao de copiar link de acesso,
# envia pro usuario
# O usuario convidado vai acesar por ela, definir uma senha e pronto