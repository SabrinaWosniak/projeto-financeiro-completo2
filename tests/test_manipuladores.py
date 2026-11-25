"""Cada manipulador testado sozinho, sem barramento e sem casos de uso."""
from financeiro.aplicacao.manipuladores import (
    AlertarSaldoBaixo,
    NotificarAjuste,
    NotificarLancamento,
)
from financeiro.dominio.eventos import LancamentoRegistrado, SaldoAjustado
from tests.conftest import NotificadorFalso


def evento(tipo="debito", valor=50.0, saldo=500.0) -> LancamentoRegistrado:
    return LancamentoRegistrado("c1", "l1", tipo, valor, saldo)


class TestNotificarLancamento:
    def test_avisa_com_tipo_valor_e_saldo(self) -> None:
        notificador = NotificadorFalso()

        NotificarLancamento(notificador)(evento("debito", 50.0, 450.0))

        (mensagem,) = notificador.mensagens
        assert "débito" in mensagem
        assert "R$ 50,00" in mensagem
        assert "R$ 450,00" in mensagem


class TestAlertarSaldoBaixo:
    def test_alerta_quando_debito_deixa_saldo_abaixo_do_limite(self) -> None:
        notificador = NotificadorFalso()

        AlertarSaldoBaixo(notificador, 100.0)(evento("debito", saldo=40.0))

        assert "saldo baixo" in notificador.mensagens[0]

    def test_nao_alerta_com_saldo_acima_do_limite(self) -> None:
        notificador = NotificadorFalso()

        AlertarSaldoBaixo(notificador, 100.0)(evento("debito", saldo=500.0))

        assert notificador.mensagens == []

    def test_nao_alerta_em_credito(self) -> None:
        notificador = NotificadorFalso()

        AlertarSaldoBaixo(notificador, 100.0)(evento("credito", saldo=40.0))

        assert notificador.mensagens == []


class TestNotificarAjuste:
    def test_avisa_o_ajuste_aplicado(self) -> None:
        notificador = NotificadorFalso()

        NotificarAjuste(notificador)(SaldoAjustado("c1", "juros", 12.5, 112.5))

        (mensagem,) = notificador.mensagens
        assert "Ajuste de juros" in mensagem
        assert "R$ 12,50" in mensagem
