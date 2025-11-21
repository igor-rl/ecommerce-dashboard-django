from django.db.models.signals import post_save
from django.dispatch import receiver
from organization.models import Enterprise, SchedulingConfig
from .models import Member


@receiver(post_save, sender=Enterprise)
def create_owner_member(sender, instance, created, **kwargs):
    if not created:
        return

    contract = instance.contract
    user = contract.user

    # Já existe owner? Evita duplicação
    if Member.objects.filter(enterprise=instance, role="owner").exists():
        return

    # Dono sempre é aceito automaticamente
    Member.objects.create(
        enterprise=instance,
        user=user,
        name=user.get_full_name() or user.username,
        email=user.email,
        role="owner",
        invite_status="accepted"
    )


# =====================================
# 🔥 Criar Configuração Automaticamente
# =====================================
@receiver(post_save, sender=Enterprise)
def create_scheduling_config(sender, instance, created, **kwargs):
    if not created:
        return

    # Evita duplicação caso já exista
    if hasattr(instance, "scheduling_config"):
        return

    SchedulingConfig.objects.create(
        enterprise=instance
    )
