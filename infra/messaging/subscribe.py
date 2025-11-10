import os
import logging
from typing import Dict, Any

from commun.jwt_access_token import JwtAccessToken

from kombu import Connection, Exchange, Producer
from django.conf import settings

# Configurar logger
logger = logging.getLogger(__name__)


def get_rabbitmq_url() -> str:
    # Obter as variáveis individuais do RabbitMQ
    # rabbit_user = os.environ.get('RABBITMQ_DEFAULT_USER') or getattr(settings, 'RABBITMQ_DEFAULT_USER')
    rabbit_user = os.environ.get('RABBITMQ_DEFAULT_USER')
    # rabbit_password = os.environ.get('RABBITMQ_DEFAULT_PASS') or getattr(settings, 'RABBITMQ_DEFAULT_PASS')
    rabbit_password = os.environ.get('RABBITMQ_DEFAULT_PASS')
    # rabbit_host = os.environ.get('RABBITMQ_HOST') or getattr(settings, 'RABBITMQ_HOST')
    rabbit_host = os.environ.get('RABBITMQ_HOST')
    # rabbit_port = os.environ.get('RABBITMQ_AMQP_PORT') or getattr(settings, 'RABBITMQ_AMQP_PORT')
    rabbit_port = os.environ.get('RABBITMQ_AMQP_PORT')
    
    formatted_url = f"amqp://{rabbit_user}:{rabbit_password}@{rabbit_host}:{rabbit_port}"

    return formatted_url


def send_rabbitmq_message(payload: Dict[str, Any], routing_key: str, url: str = None) -> bool:
    # Obter URL do RabbitMQ
    rabbitmq_url = url or get_rabbitmq_url()
    
    # Estruturar a mensagem
    message = {
        'payload': payload,
        'jwt': JwtAccessToken().token
    }
    
    # Log para debug
    logger.debug(f"Preparando envio para RabbitMQ: {routing_key} - {payload}")
    
    # Enviar a mensagem
    try:
        with Connection(rabbitmq_url) as conn:
            # Use o exchange padrão amq.direct
            exchange = Exchange('amq.direct', type='direct')
            producer = Producer(conn)
            
            # Publica com a routing key apropriada
            producer.publish(
                message,
                exchange=exchange,
                routing_key=routing_key,
                retry=True,
                retry_policy={
                    'interval_start': 0,  # Começa imediatamente
                    'interval_step': 2,   # Aumenta 2s por retry
                    'interval_max': 30,   # Máximo de 30s entre retries
                    'max_retries': 5,     # Tenta até 5 vezes
                },
            )
            logger.info(f"Mensagem enviada para RabbitMQ: {routing_key}")
            return True
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem para RabbitMQ: {e}", exc_info=True)
        return False 