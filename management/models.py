import uuid
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class Contract(models.Model):
    """
    Representa o contrato de um cliente com sua conta principal.
    Cada contrato gera automaticamente uma Enterprise.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    domain = models.CharField(
        max_length=80,
        unique=True,
        verbose_name="Domínio",
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9-]+$',
                message="Use apenas letras minúsculas, números e hífens (sem espaços)."
            )
        ]
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="contract_owner",
        verbose_name="Usuário do Painel"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    valid_until = models.DateField(
        verbose_name="Válido até",
        blank=True,
        null=True,
        help_text="Data de validade do contrato."
    )

    is_active = models.BooleanField(default=True, verbose_name="Contrato Ativo")

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} ({self.domain})"

    @property
    def is_valid(self):
        if not self.valid_until:
            return True
        return self.valid_until >= timezone.now().date()
