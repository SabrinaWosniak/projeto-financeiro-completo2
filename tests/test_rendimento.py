import pytest

from financeiro.dominio.estrategias.rendimento import (
    EstrategiaRendimento,
    RendimentoFixo,
    RendimentoPercentual,
)


class TestRendimento:

    def test_rendimento_fixo(self) -> None:
        estrategia = RendimentoFixo(0.10)

        assert estrategia.calcular(1000.0) == 100.0

    def test_rendimento_fixo_valor_invalido(self) -> None:
        estrategia = RendimentoFixo(0.10)

        with pytest.raises(ValueError):
            estrategia.calcular(0)

    def test_rendimento_fixo_taxa_negativa(self) -> None:
        with pytest.raises(ValueError):
            RendimentoFixo(-0.10)

    def test_rendimento_percentual(self) -> None:
        estrategia = RendimentoPercentual(10)

        assert estrategia.calcular(1000.0) == 100.0

    def test_rendimento_percentual_valor_invalido(self) -> None:
        estrategia = RendimentoPercentual(10)

        with pytest.raises(ValueError):
            estrategia.calcular(0)

    def test_rendimento_percentual_percentual_negativo(self) -> None:
        with pytest.raises(ValueError):
            RendimentoPercentual(-10)