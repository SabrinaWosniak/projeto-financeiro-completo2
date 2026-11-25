# Projeto final de programação

Projeto final de Programação Orientada a Objetos II. É um programa de terminal
para controlar contas e lançamentos (débitos e créditos), com rendimento, juros
e correção monetária, avisos automáticos e dados guardados em SQLite.

## Como rodar

Precisa só do Python 3.10+ (o programa em si não usa nenhuma biblioteca externa).

```bash
git clone https://github.com/SabrinaWosniak/projeto-financeiro-completo2.git
cd projeto-financeiro-completo2

python main.py --demo      # abre o menu já com contas de exemplo
python main.py             # abre o menu (usa/cria o arquivo financeiro.db)
python main.py --memoria   # não grava nada em disco
python main.py --db outro.db
```

**Para demonstrar a persistência:** rode `python main.py --demo`, saia com `0`,
rode de novo `python main.py` e escolha `2. Listar contas`: os dados continuam lá.

**Testes** (precisa do pytest: `pip install pytest`):

```bash
python -m pytest
```

Funciona também no terminal do GitHub Codespaces (basta abrir o repositório lá
e rodar os mesmos comandos).

## Estrutura

```
main.py                       ponto de entrada (lê argumentos e liga tudo)
financeiro/
  composicao.py               RAIZ DE COMPOSIÇÃO: único lugar que conhece todas as camadas
  dominio/                    regras de negócio, sem nada de banco ou terminal
    conta.py, lancamento.py, categoria.py, fechamento.py, extrato.py, conciliacao.py
    eventos.py                fatos imutáveis (LancamentoRegistrado, SaldoAjustado)
    repositorios.py           contrato RepositorioContas
    fabricas.py               FabricaEstrategias
    regras_lancamento.py      cadeia de regras (padrão do bônus)
    estrategias/              rendimento, juros, correção (Strategy)
  aplicacao/                  casos de uso e reações aos eventos
    casos_de_uso.py, manipuladores.py, portas.py, erros.py
  infraestrutura/             detalhes técnicos
    repositorio_memoria.py, repositorio_sqlite.py,
    barramento_memoria.py, notificador_terminal.py
  interface/                  menu de terminal (só chama casos de uso)
    menu_terminal.py, cenario_demo.py
tests/
```

Regra de dependência (verificada em `tests/test_arquitetura.py`): as setas
apontam sempre para o domínio.

```
interface ──► aplicacao ──► dominio ◄── infraestrutura
                 ▲                            ▲
                 └──────── composicao.py ─────┘   (liga as peças)
```

## Documento de decisões

### 1. Quais padrões usei e para qual problema?

| Padrão | Dor antes | Como ficou |
|---|---|---|
| **Strategy** (rendimento, juros, correção) | O cálculo mudava de um tipo de ajuste para outro; colocar tudo na `Conta` exigiria vários `if`. | Cada cálculo é uma classe com `calcular()`. A `Conta` recebe a estratégia e não sabe qual é. |
| **Factory** (`FabricaEstrategias`) | O menu/caso de uso teria que conhecer as 6 classes concretas e converter taxa (%) para cada uma. | Quem chama só diz `("juros", "simples", 1.5)` e recebe a estratégia pronta. |
| **Repository** (`RepositorioContas`) | Regras de negócio misturadas com SQL; impossível testar sem banco. | Um contrato, duas implementações (memória e SQLite). Os testes de contrato rodam nas duas. |
| **Caso de uso + camadas** | O menu poderia chamar o domínio e o banco direto, e tudo ficaria acoplado. | Menu → caso de uso → domínio. Trocar o menu por REST não mexe no resto. |
| **Injeção de dependência + raiz de composição** | Classes criando as próprias dependências (ex.: um caso de uso dando `new` no repositório SQLite). | Tudo chega pelo construtor; só `composicao.py` decide quem usa quem. |
| **Eventos de domínio + barramento** | Registrar um lançamento teria que chamar também o aviso, o alerta de saldo baixo etc., e cada novo aviso mexeria no caso de uso. | O caso de uso só anuncia o fato; os manipuladores assinam e reagem por conta própria. |
| **Chain of Responsibility** (bônus) | Ver seção do bônus abaixo. | |

### 2. Quais padrões considerei e recusei?

- **ORM:** com 2 tabelas e SQL simples, `sqlite3` puro é mais fácil de explicar. Valeria usar um ORM se o modelo crescesse (muitas tabelas, relações, migrações).
- **Unit of Work completo:** o único ponto que precisa de gravação conjunta (saldo + lançamento) cabe em um método do repositório com transação. Uma classe a mais seria exagero.
- **Factory Method com hierarquia de criadores:** só temos uma família de criação, então fiz uma fábrica simples (um dicionário de "receitas"), não uma hierarquia de criadores.
- **Fila externa / mensageria de verdade:** não há outro sistema para avisar. O barramento em memória resolve.
- **Singleton:** recusado de propósito; o que precisa ser único (o repositório) é criado uma vez na raiz de composição e passado adiante.
- **State, Decorator, Command, Builder, Composite, Adapter:** não tinham dor real aqui (veja a comparação no bônus para State e Decorator).

### 3. Que fatos o sistema anuncia? Eventos carregam objetos ou identificadores?

- `LancamentoRegistrado` (conta, lançamento, tipo, valor, saldo depois)
- `SaldoAjustado` (conta, qual ajuste, valor aplicado, saldo depois)

São os dois momentos em que o dinheiro de uma conta realmente muda, e são
os que interessam a quem reage (avisar, alertar). Não criei evento para
"conta criada" nem "extrato consultado" porque ninguém reage a eles.

Os eventos são `dataclass(frozen=True)` (fatos não mudam) e carregam
**identificadores e valores simples, não objetos**. Assim quem reage não consegue
alterar a `Conta` por acidente, e o mesmo evento poderia virar uma mensagem de
fila sem mudar nada. Por isso o evento já leva `saldo_apos`: o manipulador não
precisa buscar a conta de novo.

### 4. Se uma reação falha, o que acontece?

Eu **isolo** a falha. Quando o evento é publicado, o lançamento já foi gravado:
o fato aconteceu. Se um aviso quebrar, desfazer o lançamento seria pior que
perder o aviso, e uma reação quebrada não pode impedir as outras.

O `BarramentoEmMemoria` captura a exceção de cada manipulador, guarda em
`barramento.falhas`, registra no `logging` e avisa o usuário no terminal
(`A reação X falhou: ...`). Está testado em `test_barramento.py` e, de ponta a
ponta, em `test_falha_de_reacao_no_sistema.py` (lançamento continua gravado,
outra reação roda, a falha fica visível). O custo: uma falha pode passar
despercebida se ninguém olhar o aviso/log. Em um sistema real eu faria um
reenvio ou uma fila de "mensagens com erro".

### 5. O que precisa ser atômico?

Registrar um lançamento muda **duas coisas**: grava o lançamento e atualiza o
saldo da conta. Se só uma acontecesse, o saldo ficaria inconsistente com o
extrato. Por isso `registrar_lancamento(conta, lancamento)` faz as duas
gravações **dentro de uma única transação** (`with conexao:` no SQLite: se algo
falhar, tudo volta atrás). Está dentro de uma única operação do repositório.
O teste `test_lancamento_duplicado_e_recusado_e_saldo_nao_muda` prova isso nas
duas implementações. O evento só é publicado **depois** da gravação.

### 6. O que não está persistido? Quando usar um ORM?

Persistido: contas (nome, saldo, ativa) e lançamentos.

Não persistido:
- **Histórico de eventos e avisos** (some quando o programa fecha).
- **Fechamentos e extratos** (são calculados na hora a partir dos lançamentos; `Fechamento` e `Conciliacao` existem no domínio, mas o menu só usa o `Extrato`).
- **Categorias** como entidade própria (hoje é só o nome gravado no lançamento).
- **Parâmetros** (limites da cadeia de regras e do alerta ficam em `composicao.py`).

Para ficar completo: tabelas para categorias, fechamentos e um histórico de eventos.
Um ORM passaria a valer quando houvesse muitas tabelas e relações, porque o
mapeamento manual e as migrações começam a dar mais trabalho que o ORM.

Limitação conhecida: valores em dinheiro usam `float` (arredondados a 2 casas).
Em um sistema real eu usaria `Decimal` ou centavos inteiros.

### 7. Qual interface escolhi e o que mudaria se trocasse?

**Menu de terminal** (com `--demo` para dados de exemplo). Escolhi porque é
simples de demonstrar e de testar (o teste digita as respostas "de mentira"),
e o enunciado não pede nada além de um ponto de entrada.

Se trocasse por REST: criaria uma nova pasta de interface (ex.: `interface/api.py`)
que chama os **mesmos casos de uso** e traduz erros para códigos HTTP, e
mudaria `main.py`. `dominio/`, `aplicacao/` e `infraestrutura/` ficam intactos.
Isso é garantido por teste: a interface não pode importar domínio nem
infraestrutura.

### 8. Se passasse a usar uma fila externa, quais arquivos mudariam?

**Mudariam:** `infraestrutura/barramento_memoria.py` (nasceria um
`barramento_fila.py` que publica na fila) e `composicao.py` (para escolher o novo
barramento). Os manipuladores passariam a ser consumidores da fila, mas o código
de cada um continua igual.

**Não mudariam:** `dominio/` (os eventos já são dados simples, fáceis de
serializar), os casos de uso (só conhecem a porta `BarramentoEventos`) e a
interface.

### 9. O que eu mudaria se começasse de novo?

- Teria separado desde o início o modelo de dinheiro (usar `Decimal`/centavos).
- Teria pensado nos eventos e nas camadas logo no começo, em vez de refatorar tudo no final.
- Teria escrito os testes de contrato do repositório antes da segunda implementação.
- Revisaria as estratégias de taxa: `RendimentoFixo`, `JurosSimples` e
  `CorrecaoPercentual` esperam a taxa como fração (0,01), mas
  `RendimentoPercentual` espera em % (1). A fábrica esconde isso do usuário,
  mas o certo seria padronizar. Além disso `JurosCompostos` está fixo em 2 períodos.

## Padrão do bônus: Chain of Responsibility

### A dor era real?

Antes de registrar um lançamento, o sistema precisa conferir **regras de
política** (não são invariantes da `Conta`): valor máximo por lançamento,
limite diário de débitos, proibição de data futura. Sem o padrão, o jeito mais direto seria
uma sequência de `if` dentro do caso de uso `RegistrarLancamento`. Cada regra nova
(ex.: "bloquear categoria X") obrigaria a editar o caso de uso, que ficaria cada
vez maior e mais difícil de testar.

Depois: cada regra é uma classe (`ValorMaximoPorLancamento`,
`LimiteDiarioDeDebitos`, `DataNaoFutura`) que valida e passa o lançamento para
a próxima. O caso de uso faz uma única chamada (`regras.validar(...)`). A cadeia é
montada em `composicao.py`:

```python
regras = ValorMaximoPorLancamento(10_000.0)
regras.encadear(LimiteDiarioDeDebitos(5_000.0)).encadear(DataNaoFutura())
```

As invariantes que são da conta (saldo suficiente, conta ativa) continuam
dentro de `Conta`, para não duplicar regra nos dois lugares.

### Implementação e testes

Código em `financeiro/dominio/regras_lancamento.py`. Testes em
`tests/test_regras_lancamento.py` (cada regra sozinha, a cadeia completa e a
prova de que uma regra nova entra sem mexer nas outras) e em
`tests/test_casos_de_uso.py` (o caso de uso recusa pela cadeia).

### O que pesquisei, o que adaptei e o custo

- Fontes: capítulo 23 do material da disciplina; Refactoring.Guru, "Chain of
  Responsibility"; livro *Design Patterns* (Gamma et al., a "Gang of Four").
- Adaptação: na versão clássica, cada elo decide se trata ou passa adiante.
  Aqui todas as regras **sempre** passam adiante e quem recusa levanta
  `RegraViolada`, porque queremos que todas as regras sejam conferidas, não que
  só uma "trate" o pedido. Também passei a lista de lançamentos do dia para
  as regras, para o limite diário funcionar sem a regra conhecer o repositório.
- Custo: mais classes (4 no lugar de uns `if`), mais indireção (para entender o
  que acontece é preciso olhar `composicao.py`), e a **ordem importa** (o erro
  mostrado é o da primeira regra que falhar). Para só 3 regras é perto do limite
  do que compensa; o ganho aparece quando as regras crescem.

### Por que ele e não outro?

- **State:** descartado. A `Conta` só tem dois estados (ativa/encerrada) e uma
  transição; um booleano com validação resolve. State valeria com mais estados
  e comportamentos diferentes em cada um.
- **Decorator:** descartado. Servia para "embrulhar" as estratégias de cálculo
  (ex.: limitar o teto do rendimento), mas hoje ninguém pede isso.

## Histórico das entregas anteriores

### Parte 1 - Domínio

- `Fechamento` guarda uma **cópia** dos lançamentos, para que mudanças na lista original não alterem o fechamento.
- `Conciliacao` é uma classe separada porque tem uma função própria: conferir se débitos e créditos batem. Se forem diferentes, levanta erro.
- Um fechamento não pode ser criado sem lançamentos.

### Parte 2 - Estratégias

- As interfaces `EstrategiaRendimento`, `EstrategiaJuros` e `EstrategiaCorrecao` são **separadas** (não uma só reaproveitada), porque cada família tem regras próprias e fica mais fácil de testar e organizar.
- A estratégia é **passada por parâmetro** para os métodos da `Conta` (`aplicar_rendimento`, `aplicar_juros`, `aplicar_correcao`), e não guardada como atributo, para a mesma conta poder receber estratégias diferentes quando precisar.
- Dá para adicionar hoje, sem alterar nenhuma classe existente, uma nova estratégia (ex.: `CorrecaoPorInflacao`) só implementando a interface.
