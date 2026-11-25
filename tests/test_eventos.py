from dataclasses import FrozenInstanceError

import pytest

from financeiro.dominio.eventos import LancamentoRegistrado, SaldoAjustado


def test_evento_e_imutavel() -> None:
    evento = LancamentoRegistrado("c1", "l1", "debito", 10.0, 90.0)

    with pytest.raises(FrozenInstanceError):
        evento.valor = 999.0  # type: ignore[misc]


def test_evento_carrega_identificadores_e_valores_simples() -> None:
    evento = SaldoAjustado("c1", "rendimento", 10.0, 110.0)

    assert evento.conta_id == "c1"
    assert isinstance(evento.conta_id, str)
    assert isinstance(evento.valor_aplicado, float)
