# ADR 0002 — Uso do Redis como Mecanismo de Distributed Lock no Sistema de Agendamentos

**Data:** 2025-11-11  
**Status:** Aceito  
**Autor:** Igor Lage  
**Contexto:** Módulo de Scheduling / Agenda Inteligente  
**Versão:** 1.0  

---

# 1. Contexto

O módulo de agendamentos é parte central do sistema, responsável por:

- controlar horários disponíveis  
- evitar sobreposição de atendimentos  
- garantir consistência nos agendamentos  
- suportar múltiplos profissionais (workers)  
- operar em ambientes com escalabilidade horizontal  
- rodar em containers Docker, futuramente Kubernetes

A arquitetura exige que múltiplas instâncias da API possam processar requisições simultâneas sem causar **race conditions**, especialmente no caso:

> Dois clientes tentam marcar horário simultaneamente para o mesmo worker.

Se duas requisições concorrentes executarem:

1. cálculo de disponibilidade  
2. validação de horários  
3. criação do agendamento  

ao mesmo tempo, existe risco real de:

- sobreposição de horários  
- criação de agendamentos conflitantes  
- inconsistência nos dados  
- perda de integridade lógica do sistema  

---

# 2. Problema

No cenário atual (e futuro), o sistema será executado:

- em múltiplos processos Gunicorn  
- em múltiplos containers Docker  
- com escalabilidade horizontal (replicas > 1)  
- potencialmente em ambiente Kubernetes  

Isso significa que:

- **locks em memória (threading.Lock)** não funcionam  
- **locks por processo** não garantem consistência entre containers  
- **o banco de dados não oferece lock por chave (worker_id)** nativamente  
- **race conditions são quase inevitáveis** sem sincronização externa  

O sistema precisa de um mecanismo de sincronização **entre instâncias**, não apenas dentro de um único processo.

---

# 3. Decisão

Adotar **Redis** como mecanismo de **Distributed Lock**, aplicando travas exclusivamente por `worker_id` no processo de criação de agendamentos.

O lock será implementado através de:

```
lock:worker:<id>
```

Sempre que o sistema precisar criar um agendamento:

```python
with redis_lock(f"worker:{worker_id}"):
    # calcular janelas
    # validar horários
    # salvar agendamento
```

Assim:

- apenas **um processo** pode manipular a agenda de um worker por vez  
- múltiplos workers podem ser processados **em paralelo**  
- múltiplos containers podem rodar em produção sem conflito  

---

# 4. Justificativas

### ✔ Evita race conditions mesmo com múltiplas réplicas  
Redis é externo e compartilhado, portanto o lock é respeitado entre containers, processos e máquinas.

### ✔ Lock por chave (worker_id)  
Precisamos apenas garantir exclusividade na agenda do profissional específico.

Não há necessidade de lock global.

### ✔ Redis é extremamente rápido para operações atômicas  
Sua latência média está na casa dos microssegundos, tornando quase imperceptível o tempo extra.

### ✔ Solução já consolidada no mercado  
Redis Redlock é utilizado por:

- Uber  
- Stripe  
- GitHub  
- Shopify  
- plataformas de reserva e e-commerce

### ✔ Suporte nativo na biblioteca redis-py  
O Django integra naturalmente com Redis via django-redis.

### ✔ Operações são expandidas horizontalmente  
Esse é o maior ponto de vantagem:

- Podem existir 2  
- 5  
- 10  
- 20 instâncias da API  
- Em Kubernetes com autoscaling automático  

**Nada quebra**.

### ✔ Simplicidade na implementação  
Não requer alterações profundas no código, nem estrutura nova de banco.

### ✔ Tolerância a falhas  
Se um container cair com o lock ativo, o timeout libera automaticamente.

### ✔ Evita uso indevido do banco para locks  
Banco de dados é caro e lento para esse tipo de lógica.

Redis é ideal.

---

# 5. Alternativas Consideradas

### ❌ 1. PostgreSQL Advisory Lock  
Funciona, mas:

- adiciona complexidade nas transações  
- pode gerar deadlocks mais difíceis de diagnosticar  
- não escala tão bem em ambientes com grande paralelismo  
- exige que toda operação seja feita dentro de transações longas

Foi considerado, mas rejeitado.

---

### ❌ 2. Lock em memória usando threading.Lock  
Impossível para escalabilidade horizontal:

- cada instância teria seu próprio lock  
- containers independentes → concorrência garantida  
- não funciona quando a API escala automaticamente

---

### ❌ 3. Fila por worker (RabbitMQ)  
Altamente robusto, porém:

- exigiria reescrever todo fluxo para processamento assíncrono  
- adiciona acoplamento desnecessário nesta fase  
- aumenta latência entre requisição HTTP e resultado

Poderá ser avaliado futuramente como evolução da arquitetura.

---

### ❌ 4. Tabela de locks no banco de dados  
Gera contenção desnecessária, leitura e escrita constante e uso incorreto do banco para sincronização.

---

# 6. Consequências

### 📈 Positivas

- **Agendamentos seguros**, sem risco de colisão  
- Possibilidade de **escala automática** em Kubernetes  
- Baixa latência  
- Baixo custo operacional  
- O lock restringe apenas o worker, nunca o sistema inteiro  
- A API se torna **thread-safe e container-safe**  
- Fluxo de agendamento se mantém síncrono, simples e direto  
- Infraestrutura preparada para crescimento real

---

### ⚠️ Negativas / Trade-offs

- Dependência externa do Redis  
- Necessidade de monitoramento (ex: RedisMemoryUsed)  
- Timeout deve ser dimensionado corretamente  
- Falhas de rede podem causar retries  
- Redis não deve rodar sem persistência desnecessária (performance)

---

# 7. Onde e como Redis é usado no negócio

Redis é utilizado **exclusivamente** para garantir integridade no fluxo de agendamentos, que é:

- crítico  
- sensível a concorrência  
- central para o modelo de negócio  
- vital para a experiência do cliente final  
- base para todas as operações do sistema

Redis impede:

- horários duplicados  
- perda de integridade da agenda  
- falhas de sincronização  
- decisões incorretas de disponibilidade  
- inconsistências de estoque de horários

Isso garante que:

👉 Nenhum profissional tenha horários conflitantes  
👉 O sistema entregue confiança para o cliente final  
👉 A plataforma possa operar com múltiplos servidores simultâneos  
👉 O crescimento horizontal seja seguro e previsível  
👉 A experiência de agendamento seja confiável — essencial para clínicas, salões, consultórios e serviços

---

# 8. Status

**Aceito** — Esta decisão se torna parte oficial da arquitetura.  
Mudanças futuras deverão gerar uma nova ADR ligada a esta.

---

# 9. Links Relacionados

- ADR 0001 — Arquitetura Geral do Sistema  
- ADR 0003 — Remoção de SchedulingWindow e cálculo dinâmico  
- ADR 0004 — Cálculo de disponibilidade on-the-fly  

