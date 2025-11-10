# Executando a Aplicação no Kubernetes

Este guia mostra como executar a aplicação no Kubernetes localmente, usando Kind ou Minikube.

## Pré-requisitos

Você precisa ter instalado:
- Docker
- Kind ou Minikube
- kubectl

## Opção 1: Usando Kind (Kubernetes in Docker)

### Instalação do Kind (se não tiver instalado)

```bash
# Para Linux
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Para macOS (usando Homebrew)
brew install kind
```

### Criando um cluster Kind

```bash
# Criar um cluster básico
kind create cluster --name permissao-cluster

# Verificar se o cluster está funcionando
kubectl cluster-info
```

### Carregando a imagem para o Kind

```bash
# Construir a imagem Docker
docker build -t permisao-dashboard:0.0 -f Dockerfile .

# Carregar a imagem no cluster Kind
kind load docker-image permisao-dashboard:0.0 --name permissao-cluster
```

### Implantando a aplicação

```bash
# Aplicar os manifestos do Kubernetes
kubectl apply -f k8s/deploy.yaml
kubectl apply -f k8s/service.yaml

# Verificar se os pods estão rodando
kubectl get pods -l app=django-app
```

### Acessando a aplicação

```bash
# Port-forward para acessar o serviço
kubectl port-forward service/django-service 8000:8000
```

Agora você pode acessar a aplicação em http://localhost:8000

## Opção 2: Usando Minikube

### Instalação do Minikube (se não tiver instalado)

```bash
# Para Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Para macOS (usando Homebrew)
brew install minikube
```

### Iniciando o Minikube

```bash
# Iniciar Minikube
minikube start

# Verificar status
minikube status
```

### Carregando a imagem para o Minikube

```bash
# Construir a imagem Docker
docker build -t permisao-dashboard:0.0 -f Dockerfile .

# Carregar a imagem no Minikube
minikube image load permisao-dashboard:0.0
```

### Implantando a aplicação

```bash
# Aplicar os manifestos do Kubernetes
kubectl apply -f k8s/deploy.yaml
kubectl apply -f k8s/service.yaml

# Verificar se os pods estão rodando
kubectl get pods -l app=django-app
```

### Acessando a aplicação

```bash
# Opção 1: Port-forward
kubectl port-forward service/django-service 8000:8000

# Opção 2: Usando serviço Minikube
minikube service django-service
```

## Solução de problemas

### Verificar o status dos pods

```bash
kubectl get pods
```

### Ver logs do pod

```bash
kubectl logs -l app=django-app
```

### Descrever o pod para ver eventos e possíveis erros

```bash
kubectl describe pod -l app=django-app
```

### Se o pod estiver com ErrImagePull ou ImagePullBackOff

Isso significa que o Kubernetes não consegue encontrar a imagem. Certifique-se de:

1. Ter construído a imagem corretamente: `docker build -t permisao-dashboard:0.0 -f Dockerfile .`
2. Ter carregado a imagem no cluster:
   - Para Kind: `kind load docker-image permisao-dashboard:0.0 --name permissao-cluster`
   - Para Minikube: `minikube image load permisao-dashboard:0.0`
3. Ter definido `imagePullPolicy: Never` no arquivo deploy.yaml

### Se a aplicação não conectar ao banco de dados

Verifique se:

1. O host.docker.internal está resolvendo para o IP correto
2. O PostgreSQL está rodando e aceitando conexões externas
3. As credenciais do banco de dados estão corretas 