#!/bin/bash
set -e

echo "Banco de dados: $DB_NAME"
echo "Host: $DB_HOST"
echo "Usuário: $DB_USERNAME"

# Tenta aplicar migrações normalmente
echo "Executando migrate padrão..."
python manage.py migrate --noinput || {
  echo "Falha ao aplicar migrate padrão. Tentando fake..."
  python manage.py migrate --fake || true
}

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Criar superusuário (ambiente dev/local)
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Tentando criar superusuário..."
  python manage.py createsuperuser --noinput || echo "Superusuário já existe ou erro ao criar"
fi

# Executar o comando passado (gunicorn ou consumer)
echo "Executando comando: $@"
exec "$@"