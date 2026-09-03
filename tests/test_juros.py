import pytest

from financeiro.estrategias.juros import (
    EstrategiaJuros,
    JurosSimples,
    JurosCompostos,
)


class TestJuros:

    def test_juros_simples(self) -> None:
        estrategia = JurosSimples(0.10)

        assert estrategia.calcular(1000.0) == 100.0

    def test_juros_valor_invalido(self) -> None:
        estrategia = JurosSimples(0.10)

        with pytest.raises(ValueError):
            estrategia.calcular(0)

    def test_juros_taxa_negativa(self) -> None:
        with pytest.raises(ValueError):
            JurosSimples(-0.10)

    def test_juros_compostos(self) -> None:
        estrategia = JurosCompostos(0.10)

        assert estrategia.calcular(1000.0) == pytest.approx(210.0)

    def test_juros_compostos_valor_invalido(self) -> None:
        estrategia = JurosCompostos(0.10)

        with pytest.raises(ValueError):
            estrategia.calcular(0)

    def test_juros_compostos_taxa_negativa(self) -> None:
        with pytest.raises(ValueError):
            JurosCompostos(-0.10)