from uuid import uuid4

from financeiro.dominio.estrategias.correcao import EstrategiaCorrecao
from financeiro.dominio.estrategias.juros import EstrategiaJuros
from financeiro.dominio.estrategias.rendimento import EstrategiaRendimento


class Conta:
    """Conta financeira. Estados: ativa -> encerrada (sem volta)."""

    def __init__(
        self,
        nome: str,
        saldo: float = 0.0,
        id: str | None = None,
        ativa: bool = True,
    ) -> None:
        if not nome:
            raise ValueError("Nome da conta é obrigatório")

        if saldo < 0:
            raise ValueError("Saldo inicial não pode ser negativo")

        self._id = id or uuid4().hex
        self._nome = nome
        self._saldo = round(saldo, 2)
        self._ativa = ativa

    @property
    def id(self) -> str:
        return self._id

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def saldo(self) -> float:
        return self._saldo

    @property
    def ativa(self) -> bool:
        return self._ativa

    def _exigir_ativa(self) -> None:
        if not self._ativa:
            raise ValueError("Conta encerrada não aceita operações")

    def depositar(self, valor: float) -> None:
        self._exigir_ativa()

        if valor <= 0:
            raise ValueError("Valor deve ser positivo")

        self._saldo = round(self._saldo + valor, 2)

    def sacar(self, valor: float) -> None:
        self._exigir_ativa()

        if valor <= 0:
            raise ValueError("Valor deve ser positivo")

        if valor > self._saldo:
            raise ValueError("Saldo insuficiente")

        self._saldo = round(self._saldo - valor, 2)

    def registrar(self, lancamento) -> None:
        """Aplica um lançamento ao saldo: crédito soma, débito subtrai."""
        if lancamento.tipo == "credito":
            self.depositar(lancamento.valor)
        else:
            self.sacar(lancamento.valor)

    def aplicar_rendimento(self, estrategia: EstrategiaRendimento) -> None:
        self._exigir_ativa()
        rendimento = estrategia.calcular(self._saldo)
        self._saldo = round(self._saldo + rendimento, 2)

    def aplicar_juros(self, estrategia: EstrategiaJuros) -> None:
        self._exigir_ativa()
        juros = estrategia.calcular(self._saldo)
        self._saldo = round(self._saldo + juros, 2)

    def aplicar_correcao(self, estrategia: EstrategiaCorrecao) -> None:
        self._exigir_ativa()
        correcao = estrategia.calcular(self._saldo)
        self._saldo = round(self._saldo + correcao, 2)

    def encerrar(self) -> None:
        """Transição válida: ativa -> encerrada, apenas com saldo zerado."""
        self._exigir_ativa()

        if self._saldo != 0:
            raise ValueError("Só é possível encerrar uma conta com saldo zero")

        self._ativa = False
