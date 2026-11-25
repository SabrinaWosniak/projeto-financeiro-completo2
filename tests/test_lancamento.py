from datetime import date

import pytest

from financeiro.dominio.categoria import Categoria
from financeiro.dominio.lancamento import Lancamento


class TestLancamento:
    def setup_method(self) -> None:
        self.categoria = Categoria("Alimentação")

    def test_criar_lancamento(self) -> None:
        lancamento = Lancamento(
            "Mercado", 150.0, date.today(), self.categoria, "debito"
        )

        assert lancamento.descricao == "Mercado"
        assert lancamento.valor == 150.0
        assert lancamento.categoria == self.categoria
        assert lancamento.tipo == "debito"

    def test_lancamento_com_valor_invalido(self) -> None:
        with pytest.raises(ValueError):
            Lancamento("Mercado", 0, date.today(), self.categoria, "debito")

    def test_lancamento_com_tipo_invalido(self) -> None:
        with pytest.raises(ValueError):
            Lancamento("Mercado", 150.0, date.today(), self.categoria, "outro")

#Esse arquivo testa a classe Lancamento. Ele verifica se um lançamento é criado corretamente e se suas informações são armazenadas. Também testa as validações para impedir valores inválidos e tipos de lançamento que não sejam débito ou crédito.