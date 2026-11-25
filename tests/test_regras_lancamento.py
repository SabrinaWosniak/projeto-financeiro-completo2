"""Testes do padrão do bônus: Chain of Responsibility."""
from datetime import date, timedelta

import pytest

from financeiro.dominio.categoria import Categoria
from financeiro.dominio.lancamento import Lancamento
from financeiro.dominio.regras_lancamento import (
    DataNaoFutura,
    LimiteDiarioDeDebitos,
    RegraLancamento,
    RegraViolada,
    ValorMaximoPorLancamento,
)

HOJE = date(2026, 6, 15)


def lanc(valor=100.0, tipo="debito", data=HOJE) -> Lancamento:
    return Lancamento("x", valor, data, Categoria("Geral"), tipo)


class TestRegrasIsoladas:
    def test_valor_maximo_aceita_ate_o_limite(self) -> None:
        ValorMaximoPorLancamento(500.0).validar(lanc(500.0), [])

    def test_valor_maximo_recusa_acima_do_limite(self) -> None:
        with pytest.raises(RegraViolada, match="máximo"):
            ValorMaximoPorLancamento(500.0).validar(lanc(500.01), [])

    def test_limite_diario_soma_debitos_do_dia(self) -> None:
        regra = LimiteDiarioDeDebitos(1000.0)

        with pytest.raises(RegraViolada, match="diário"):
            regra.validar(lanc(300.0), [lanc(800.0)])

    def test_limite_diario_ignora_creditos(self) -> None:
        LimiteDiarioDeDebitos(1000.0).validar(lanc(900.0), [lanc(5000.0, "credito")])

    def test_limite_diario_nao_vale_para_credito(self) -> None:
        LimiteDiarioDeDebitos(100.0).validar(lanc(5000.0, "credito"), [])

    def test_data_futura_e_recusada(self) -> None:
        regra = DataNaoFutura(hoje=lambda: HOJE)

        with pytest.raises(RegraViolada, match="futura"):
            regra.validar(lanc(data=HOJE + timedelta(days=1)), [])

    def test_data_de_hoje_e_aceita(self) -> None:
        DataNaoFutura(hoje=lambda: HOJE).validar(lanc(), [])


class TestCadeia:
    def _cadeia(self) -> RegraLancamento:
        primeira = ValorMaximoPorLancamento(500.0)
        primeira.encadear(LimiteDiarioDeDebitos(600.0)).encadear(
            DataNaoFutura(hoje=lambda: HOJE)
        )
        return primeira

    def test_lancamento_valido_passa_por_todas(self) -> None:
        self._cadeia().validar(lanc(100.0), [])

    def test_cada_regra_da_cadeia_pode_recusar(self) -> None:
        cadeia = self._cadeia()

        with pytest.raises(RegraViolada, match="máximo"):
            cadeia.validar(lanc(501.0), [])

        with pytest.raises(RegraViolada, match="diário"):
            cadeia.validar(lanc(200.0), [lanc(450.0)])

        with pytest.raises(RegraViolada, match="futura"):
            cadeia.validar(lanc(data=HOJE + timedelta(days=2)), [])

    def test_encadear_devolve_a_proxima_regra(self) -> None:
        a, b = ValorMaximoPorLancamento(1.0), ValorMaximoPorLancamento(2.0)

        assert a.encadear(b) is b

    def test_nova_regra_entra_sem_mudar_as_existentes(self) -> None:
        class SemCategoriaProibida(RegraLancamento):
            def _verificar(self, lancamento, lancamentos_do_dia) -> None:
                if lancamento.categoria.nome == "Proibida":
                    raise RegraViolada("Categoria proibida")

        cadeia = self._cadeia()
        cadeia.encadear(SemCategoriaProibida())  # substitui a 2ª; só prova o encaixe

        proibido = Lancamento("x", 10.0, HOJE, Categoria("Proibida"), "debito")
        with pytest.raises(RegraViolada, match="proibida"):
            cadeia.validar(proibido, [])

    def test_regra_violada_e_um_value_error(self) -> None:
        assert issubclass(RegraViolada, ValueError)
