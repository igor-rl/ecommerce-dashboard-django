import os
import jwt
from datetime import datetime, timedelta, timezone

class JwtAccessToken:
  def __init__(self):
    self.token = self.generate_jwt()

  def get_private_key(self) -> str:
      private_key = os.environ.get('JWT_PRIVATE_KEY').replace(r'\n', '\n')
      return private_key


  def get_client_id(self) -> str:
      client_id = os.environ.get('JWT_CLIENT_ID')
      return client_id


  def generate_jwt(self) -> str:
      private_key = self.get_private_key()
      payload = {
          "iss": self.get_client_id(),
          "aud": "ex-dashboard",
          "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
          "iat": datetime.now(timezone.utc),
      }
      token = jwt.encode(payload, private_key, algorithm="RS256")
      return token
  
  def __str__(self) -> str:
    return self.token