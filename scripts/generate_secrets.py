#!/usr/bin/env python3
"""
Script para gerar secrets para ambientes de produção
Use este script para gerar valores seguros para as suas secrets do Kubernetes
"""

import os
import secrets
import string
import base64

def generate_password(length=24):
    """Gera uma senha aleatória segura"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_django_secret_key():
    """Gera uma secret key para o Django"""
    return ''.join(secrets.choice(
        string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    ) for _ in range(50))

def encode_secret(value):
    """Codifica um valor para uso no Kubernetes Secret"""
    return base64.b64encode(value.encode('utf-8')).decode('utf-8')

def main():
    """Função principal que gera e exibe as secrets"""
    # Criar diretório para os secrets gerados
    os.makedirs('generated_secrets', exist_ok=True)
    
    # Gerar secrets
    secrets_dict = {
        'django-secret-key': generate_django_secret_key(),
        'db-password': generate_password(),
        'rabbitmq-password': generate_password()
    }
    
    # Salvar valores originais (não codificados)
    with open('generated_secrets/secrets.txt', 'w') as f:
        for key, value in secrets_dict.items():
            f.write(f"{key}={value}\n")
    
    # Salvar valores codificados para kubectl
    with open('generated_secrets/secrets_encoded.txt', 'w') as f:
        for key, value in secrets_dict.items():
            f.write(f"{key}={encode_secret(value)}\n")
    
    print("Secrets geradas com sucesso e salvas em:")
    print("- generated_secrets/secrets.txt (valores originais)")
    print("- generated_secrets/secrets_encoded.txt (valores codificados para kubectl)")
    print("\nIMPORTANTE: Guarde estes arquivos em local seguro e depois exclua-os deste sistema.")

if __name__ == "__main__":
    main() 