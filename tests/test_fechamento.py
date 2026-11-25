from datetime import date

import pytest

from financeiro.dominio.categoria import Categoria
from financeiro.dominio.fechamento import Fechamento
from financeiro.dominio.lancamento import Lancamento


class TestFechamento:
    def setup_method(self) -> None:
        self.categoria = Categoria("Alimentação")

        self.debito = Lancamento(
            "Mercado", 100.0, date.today(), self.categoria, "debito"
        )

        self.credito = Lancamento(
            "Salário", 500.0, date.today(), self.categoria, "credito"
        )

    def test_criar_fechamento(self) -> None:
        fechamento = Fechamento([self.debito, self.credito])

        assert fechamento.total_debitos() == 100.0
        assert fechamento.total_creditos() == 500.0

    def test_total_debitos(self) -> None:
        fechamento = Fechamento([self.debito, self.credito])

        assert fechamento.total_debitos() == 100.0

    def test_total_creditos(self) -> None:
        fechamento = Fechamento([self.debito, self.credito])

        assert fechamento.total_creditos() == 500.0

    def test_saldo(self) -> None:
        fechamento = Fechamento([self.debito, self.credito])

        assert fechamento.saldo() == 400.0

    def test_fechamento_sem_lancamentos(self) -> None:
        with pytest.raises(ValueError):
            Fechamento([])

#Esse arquivo testa a classe Fechamento. Ele verifica os totais de débitos e créditos, o cálculo do saldo e também confirma que não é possível criar um fechamento sem lançamentos