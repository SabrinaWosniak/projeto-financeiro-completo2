# Roteiro de apresentação (5 a 8 minutos)

Prepare o terminal já na pasta do projeto, com `financeiro.db` apagado.

1. **Abrir (30 s):** "É um controle financeiro de terminal em 3 camadas:
   domínio, aplicação e infraestrutura." Mostre a árvore de pastas do README.
2. **Rodar (1 min):** `python main.py --demo`. Opção `2` (contas) e `5` (extrato)
   da Conta Corrente. Repare nos avisos que apareceram ao carregar os dados:
   são os manipuladores de eventos reagindo.
3. **Caminho de um lançamento (2 min):** opção `3`, débito de R$ 1.900 na
   Conta Corrente (saldo ~R$ 1.968). Explique a sequência:
   menu → `RegistrarLancamento` → cadeia de regras → `Conta.registrar` →
   repositório (saldo + lançamento numa transação) → evento
   `LancamentoRegistrado` → `NotificarLancamento` e `AlertarSaldoBaixo`.
   Aparece o aviso de **saldo baixo**.
4. **Regras (1 min):** tente um lançamento de R$ 20.000 (recusado pela cadeia)
   e um débito maior que o saldo (recusado pela `Conta`). Mostre que o erro
   aparece em português e o menu continua.
5. **Persistência (1 min):** saia (`0`), rode `python main.py` de novo e liste
   as contas: os dados continuam.
6. **Strategy + Factory (30 s):** opção `4`, escolher `juros composto` 2%.
7. **Bônus (1 min):** abra `regras_lancamento.py` e `composicao.py`: "para ter
   uma regra nova, escrevo uma classe e encaixo na cadeia; o caso de uso não muda."
8. **Testes (30 s):** `python -m pytest`. Cite: contrato do repositório rodando
   em memória e SQLite, testes de arquitetura, teste de reação que falha.

Perguntas prováveis: *"Por que a falha da reação é isolada?"* (o lançamento já
foi gravado; desfazer seria pior) e *"O que muda com uma fila externa?"*
(só o barramento em `infraestrutura/` e a `composicao.py`).
