![header-igor-projetos](https://github.com/igor-rl/assets/blob/main/img/github-projetcs-header.jpg)

# 🛒 E-COMMERCE DASHBOARD

O aplicativo **E-Commerce Dashboard** é o painel administrativo do
projeto de e-commerce desenvolvido por [Igor
Lage](https://igorlage.vercel.app/home).\
Ele foi projetado para permitir que o proprietário do negócio gerencie
de forma eficiente sua plataforma de vendas online contratada junto ao
franqueador, priorizando **escalabilidade**, **isolamento de ambiente**
e **automação de setup** via containers.

## ⬇️ Comece a partir do projeto base

**Copie o projeto base disponibilizado no gitHub:**

```bash
git clone https://github.com/igor-rl/django-base.git
```

**Escolha um novo nome para o projeto:**
```bash
mv django-base <nome-novo>
```

**Acesse a pasta do projeto:**
```bash
cd <nome-novo>
```

**Abra o projeto com o cursor IDE:**
```bash
cursor .
```

<br>

---

### ⚠️ IMPORTANTE
Antes de seguir com os próximos passos, certifique-se de criar o
aquivo .env na pasta `.docker/` com as variáveis de ambiente. Você pode fazer isso facilmente usando o arquivo `.docker/.env.examplo` como referencia.

```bash
cp .docker/.env.example .docker/.env
```

___

<br>

## 🚀 Inicialização do Projeto com Dev Container

Este projeto foi configurado para execução em um **Dev Container**,
sendo compatível com os editores **Visual Studio Code** e **Cursor**.\
Essa configuração garante um ambiente de desenvolvimento
**padronizado**, com todas as **dependências**, **bibliotecas** e
**imagens Docker** já preparadas automaticamente.

Após abrir o projeto no Dev Container, as dependências serão instaladas
automaticamente.\
Quando o processo for concluído, inicie o servidor local executando o
comando abaixo:

**Ativar o ambiente virtual com Pipenv:**

``` bash
pipenv shell
```

**Processar as migrações:**
``` bash
python manage.py migrate
```

**Criar o usuário administrador:**

``` bash
python manage.py createsuperuser
```

**Iniciar o projeto e o servidor**

``` bash
python manage.py runserver 0.0.0.0:8000
```

A aplicação estará acessível através do endereço:\
👉 <http://localhost:8000/admin>


## 🧰 Comandos Úteis

**Criar um novo projeto Djando:**

``` bash
django-admin startproject <nome_do_projeto>
```



<br/>

---


<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-Igor_Lage-blue?style=social&logo=github)](https://github.com/igor-rl) 

![Static Badge](https://img.shields.io/badge/10--11--2025-black)


</div>
