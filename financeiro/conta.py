from financeiro.estrategias.rendimento import EstrategiaRendimento
from financeiro.estrategias.juros import EstrategiaJuros
from financeiro.estrategias.correcao import EstrategiaCorrecao

class Conta:
    def __init__(self, nome: str, saldo: float = 0.0) -> None:
        if not nome:
            raise ValueError("Nome da conta é obrigatório")

        self._nome = nome
        self._saldo = saldo

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def saldo(self) -> float:
        return self._saldo

    def depositar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")

        self._saldo += valor

    def sacar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")

        if valor > self._saldo:
            raise ValueError("Saldo insuficiente")

        self._saldo -= valor

    def aplicar_rendimento(self, estrategia: EstrategiaRendimento) -> None:
        rendimento = estrategia.calcular(self._saldo)
        self._saldo += rendimento

    def aplicar_juros(self, estrategia: EstrategiaJuros) -> None:
        juros = estrategia.calcular(self._saldo)
        self._saldo += juros

    def aplicar_correcao(self, estrategia: EstrategiaCorrecao) -> None:
        correcao = estrategia.calcular(self._saldo)
        self._saldo += correcao

       # aplica uma estratégia de correção monetária ao saldo da conta.
# A conta recebe a estratégia, calcula a correção e adiciona esse valor ao saldo.