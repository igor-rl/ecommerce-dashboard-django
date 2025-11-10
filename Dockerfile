FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=permissao.settings
ENV DEBUG=False

WORKDIR /app

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY Pipfile Pipfile.lock ./

# Instalar pipenv e dependências
RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --ignore-pipfile && \
    pip install gunicorn && \
    pip cache purge

# Copiar o entrypoint e torná-lo executável
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Copiar o código do projeto
COPY . .

