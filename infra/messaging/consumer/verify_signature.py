import os
import jwt
import logging
from jwt import InvalidTokenError

logger = logging.getLogger(__name__)


def get_client_public_key(env_name: str) -> str:
    client_id = os.environ.get(env_name).replace("\\n", "\n")
    return client_id


def get_client_id(env_name: str) -> str:
    client_id = os.environ.get(env_name)
    logger.debug(f"client_id: {client_id}")
    return client_id


def verify_signature(token: str, client_public_key_env_name: str, audience: str, client_id_env_name: str) -> dict | None:
    try:

        public_key = get_client_public_key(client_public_key_env_name)

        decoded = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=audience,
            issuer=get_client_id(client_id_env_name),
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
            }
        )
        return decoded
    except InvalidTokenError as e:
        logger.error(f"JWT inválido: {e}")
        return None