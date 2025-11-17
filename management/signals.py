# management/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from organization.models import Enterprise
from .models import Contract


@receiver(post_save, sender=Contract)
def criar_enterprise_automatica(sender, instance, created, **kwargs):
    if created and not hasattr(instance, "enterprise"):
        Enterprise.objects.create(
            contract=instance,
            name=f"Enterprise de {instance.user.get_full_name() or instance.user.username}"
        )
