"""Reações aos eventos. Cada uma é independente das outras."""
from financeiro.aplicacao.portas import Notificador
from financeiro.dominio.eventos import LancamentoRegistrado, SaldoAjustado


def _reais(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


_NOMES_TIPO = {"debito": "débito", "credito": "crédito"}
_NOMES_AJUSTE = {"rendimento": "rendimento", "juros": "juros", "correcao": "correção"}


class NotificarLancamento:
    """Avisa que um lançamento foi registrado."""

    def __init__(self, notificador: Notificador) -> None:
        self._notificador = notificador

    def __call__(self, evento: LancamentoRegistrado) -> None:
        self._notificador.avisar(
            f"Lançamento de {_NOMES_TIPO[evento.tipo]} de {_reais(evento.valor)} registrado. "
            f"Saldo: {_reais(evento.saldo_apos)}"
        )


class AlertarSaldoBaixo:
    """Alerta quando um débito deixa o saldo abaixo do limite."""

    def __init__(self, notificador: Notificador, limite: float = 100.0) -> None:
        self._notificador = notificador
        self._limite = limite

    def __call__(self, evento: LancamentoRegistrado) -> None:
        if evento.tipo == "debito" and evento.saldo_apos < self._limite:
            self._notificador.avisar(
                f"ATENÇÃO: saldo baixo ({_reais(evento.saldo_apos)}), "
                f"abaixo de {_reais(self._limite)}"
            )


class NotificarAjuste:
    """Avisa que rendimento, juros ou correção mudaram o saldo."""

    def __init__(self, notificador: Notificador) -> None:
        self._notificador = notificador

    def __call__(self, evento: SaldoAjustado) -> None:
        self._notificador.avisar(
            f"Ajuste de {_NOMES_AJUSTE[evento.ajuste]}: "
            f"{_reais(evento.valor_aplicado)} aplicado. "
            f"Saldo: {_reais(evento.saldo_apos)}"
        )
