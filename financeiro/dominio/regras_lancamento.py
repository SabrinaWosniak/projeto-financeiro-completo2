"""Padrão do bônus: Chain of Responsibility.

Cada regra olha o lançamento, aprova (passando para a próxima) ou recusa
levantando RegraViolada. Para criar uma regra nova basta escrever uma
classe e encaixá-la na cadeia (em composicao.py); o caso de uso não muda.
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import Callable


def _reais(valor: float) -> str:
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


class RegraViolada(ValueError):
    """Um lançamento foi recusado por uma regra da cadeia."""


class RegraLancamento(ABC):
    def __init__(self) -> None:
        self._proxima: "RegraLancamento | None" = None

    def encadear(self, proxima: "RegraLancamento") -> "RegraLancamento":
        """Define a próxima regra e a devolve (para encadear em sequência)."""
        self._proxima = proxima
        return proxima

    def validar(self, lancamento, lancamentos_do_dia: list) -> None:
        self._verificar(lancamento, lancamentos_do_dia)

        if self._proxima is not None:
            self._proxima.validar(lancamento, lancamentos_do_dia)

    @abstractmethod
    def _verificar(self, lancamento, lancamentos_do_dia: list) -> None:
        """Levanta RegraViolada se o lançamento não puder passar."""


class ValorMaximoPorLancamento(RegraLancamento):
    def __init__(self, limite: float) -> None:
        super().__init__()
        self._limite = limite

    def _verificar(self, lancamento, lancamentos_do_dia: list) -> None:
        if lancamento.valor > self._limite:
            raise RegraViolada(
                f"Valor acima do máximo por lançamento ({_reais(self._limite)})"
            )


class LimiteDiarioDeDebitos(RegraLancamento):
    def __init__(self, limite: float) -> None:
        super().__init__()
        self._limite = limite

    def _verificar(self, lancamento, lancamentos_do_dia: list) -> None:
        if lancamento.tipo != "debito":
            return

        ja_gasto = sum(l.valor for l in lancamentos_do_dia if l.tipo == "debito")

        if ja_gasto + lancamento.valor > self._limite:
            raise RegraViolada(
                f"Limite diário de débitos excedido ({_reais(self._limite)})"
            )


class DataNaoFutura(RegraLancamento):
    def __init__(self, hoje: Callable[[], date] = date.today) -> None:
        super().__init__()
        self._hoje = hoje

    def _verificar(self, lancamento, lancamentos_do_dia: list) -> None:
        if lancamento.data > self._hoje():
            raise RegraViolada("Não é permitido lançamento com data futura")
