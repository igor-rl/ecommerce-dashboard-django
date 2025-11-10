from django.core.management.base import BaseCommand
from infra.messaging.consumer.client_consumer import start_consumer

class Command(BaseCommand):
    help = 'Inicia o consumer de atualização de client'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando consumer...")
        start_consumer()
