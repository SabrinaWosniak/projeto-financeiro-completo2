# Parte 1-

# Sistema de Controle Financeiro Pessoal

Projeto feito para a disciplina de Programação Orientada a Objetos II.

## Classes do projeto

- Conta: controla uma conta e seu saldo.
- Categoria: serve para organizar os lançamentos.
- Lancamento: registra uma entrada ou saída de dinheiro.
- Fechamento: junta os lançamentos de um período.
- Conciliacao: verifica se os débitos e créditos estão iguais.
- Extrato: mostra um resumo dos fechamentos.

## Decisões do projeto

### Fechamento

O fechamento guarda uma cópia dos lançamentos.

Escolhi fazer assim para que mudanças na lista original não alterem o fechamento.

### Conciliacao

A conciliação foi feita como uma classe separada.

Escolhi assim porque ela tem uma função própria: verificar se os débitos e créditos estão iguais.

### Sem lançamentos

Um fechamento pode ser criado sem lançamentos. Nesse caso, os valores ficam zerados.

### Conciliação diferente

Se os débitos e créditos forem diferentes, a conciliação não é válida e o sistema mostra um erro.

## Testes

O projeto usa pytest.

Foram feitos testes para verificar os casos corretos e os casos de erro.

Atualmente, os 23 testes estão passando.

## Para executar todos os testes:

PYTHONPATH=. pytest
 ou 
 python -m pytest

## Executar cada teste:
python -m pytest nomearquivo/nome.py
ex:
python -m pytest tests/test_juros.py


# Parte 2-

## Suas estratégias de rendimento, juros e correção monetária são interfaces separadas ou a mesma interface reaproveitada?

Como uma melhor forma de organizar decidi fazer interfaces separadas.Devido que facilitaria na hora de fazer os teste e decobrir os erros,como tbm fica mais organizado.


## Estratégias de rendimento

Foi criada a interface EstrategiaRendimento, que define o método calcular().

Também foram criadas duas estratégias de rendimento:

- RendimentoFixo: calcula o rendimento utilizando uma taxa definida.
- RendimentoPercentual: calcula o rendimento utilizando um percentual.

As duas estratégias utilizam a mesma interface, permitindo que novas formas de cálculo sejam adicionadas sem alterar a interface existente.

## Estratégias de juros

Foi criada a interface EstrategiaJuros, que define o método calcular().

Também foi criada a estratégia JurosSimples, responsável pelo cálculo de juros simples utilizando uma taxa.

## Testes das estratégias

Foram criados testes automatizados para as estratégias de rendimento e juros, verificando tanto os cálculos corretos quanto situações de erro, como valores inválidos e taxas negativas.



## Onde a estratégia escolhida é guardada — passada por parâmetro, ou como atributo de outra entidade (como fizemos com Cupom em relação a Pedido)? Por quê?

A estratégia escolhidEu poderia adicionar uma nova estratégia de rendimento, juros ou correção sem precisar alterar as classes que já existem.Por exemplo, poderia criar uma estratégia CorrecaoPorInflacao, que implementaria a interface EstrategiaCorrecao. Assim, ela poderia ser usada na Conta sem precisar modificar a classe Conta.a é passada por parâmetro nos métodos da classe Conta.Escolhi fazer dessa forma porque assim a conta pode receber estratégias diferentes quando for necessário, sem precisar ficar presa a uma estratégia específica.

## Que novo tipo de regra você conseguiria adicionar hoje sem editar nenhuma classe já existente?

Eu poderia adicionar uma nova estratégia de correção, como uma correção pela inflação, sem precisar alterar as classes que já existem.