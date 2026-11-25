import pytest

from financeiro.dominio.estrategias.correcao import CorrecaoFixa, CorrecaoPercentual
from financeiro.dominio.estrategias.juros import JurosCompostos, JurosSimples
from financeiro.dominio.estrategias.rendimento import (
    RendimentoFixo,
    RendimentoPercentual,
)
from financeiro.dominio.fabricas import FabricaEstrategias


@pytest.mark.parametrize(
    "familia, modalidade, classe",
    [
        ("rendimento", "fixo", RendimentoFixo),
        ("rendimento", "percentual", RendimentoPercentual),
        ("juros", "simples", JurosSimples),
        ("juros", "composto", JurosCompostos),
        ("correcao", "percentual", CorrecaoPercentual),
        ("correcao", "fixa", CorrecaoFixa),
    ],
)
def test_fabrica_cria_a_estrategia_certa(familia, modalidade, classe) -> None:
    assert isinstance(FabricaEstrategias.criar(familia, modalidade, 5.0), classe)


def test_taxa_entra_em_porcentagem() -> None:
    estrategia = FabricaEstrategias.criar("juros", "simples", 10.0)

    assert estrategia.calcular(1000.0) == pytest.approx(100.0)


def test_correcao_fixa_usa_reais() -> None:
    estrategia = FabricaEstrategias.criar("correcao", "fixa", 25.0)

    assert estrategia.calcular(1000.0) == 25.0


def test_ajuste_desconhecido_e_erro() -> None:
    with pytest.raises(ValueError, match="desconhecido"):
        FabricaEstrategias.criar("rendimento", "magico", 1.0)


def test_opcoes_listam_todas_as_estrategias() -> None:
    assert len(FabricaEstrategias.opcoes()) == 6
