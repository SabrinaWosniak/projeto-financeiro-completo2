import pytest

from financeiro.estrategias.correcao import (
    EstrategiaCorrecao,
    CorrecaoPercentual,
    CorrecaoFixa,
)


class TestCorrecao:

    def test_correcao_percentual(self) -> None:
        estrategia = CorrecaoPercentual(0.10)

        assert estrategia.calcular(1000.0) == 100.0

    def test_correcao_percentual_valor_invalido(self) -> None:
        estrategia = CorrecaoPercentual(0.10)

        with pytest.raises(ValueError):
            estrategia.calcular(0)

    def test_correcao_percentual_taxa_negativa(self) -> None:
        with pytest.raises(ValueError):
            CorrecaoPercentual(-0.10)

    def test_correcao_fixa(self) -> None:
        estrategia = CorrecaoFixa(50.0)

        assert estrategia.calcular(1000.0) == 50.0

    def test_correcao_fixa_valor_invalido(self) -> None:
        estrategia = CorrecaoFixa(50.0)

        with pytest.raises(ValueError):
            estrategia.calcular(0)

    def test_correcao_fixa_valor_negativo(self) -> None:
        with pytest.raises(ValueError):
            CorrecaoFixa(-50.0)