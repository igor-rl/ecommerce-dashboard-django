import django
import json
import logging
from kombu import Connection, Exchange, Queue, Consumer
from infra.messaging.subscribe import get_rabbitmq_url
from ex_permissao_back.models.clients import Client
from .verify_signature import verify_signature

django.setup()


client_aud_name = 'ex-permissao_back'
client_id_env_name = 'PERMISSAO_BACK_JWT_CLIENT_ID'
client_public_key_env_name = 'PERMISSAO_BACK_JWT_PUBLIC_KEY'


logger = logging.getLogger(__name__)

RABBIT_URL = get_rabbitmq_url()

exchange = Exchange("amq.direct", type="direct")
queue = Queue(
    name="dashboard/client/updated/on-permission-api",
    exchange=exchange,
    routing_key="ClientCreatedIntegrationEvent"
)


def handle_message(body, message):
    try:
        print("Mensagem recebida:", body)
        
        if isinstance(body, str):
            body = json.loads(body)

        client_id = body['payload']['id_client']
        public_key = body['payload']['public_key']
        private_key = body['payload']['private_key']
        
        jwt_token = body['jwt']

        if not verify_signature(jwt_token, client_public_key_env_name, client_aud_name, client_id_env_name ):
            logger.error("Assinatura JWT inválida")
            message.reject()
            return

        client = Client.objects.get(id=client_id)
        client.public_key = public_key
        client.private_key = private_key
        client.save()

        logger.info(f"Chaves do client {client_id} atualizadas com sucesso")
        message.ack()
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        message.reject()


def start_consumer():
    with Connection(RABBIT_URL) as conn:
        with Consumer(conn, queues=[queue], callbacks=[handle_message], accept=["json"]):
            logger.info("Consumer iniciado, aguardando mensagens...")
            while True:
                conn.drain_events()


if __name__ == "__main__":
    start_consumer()
