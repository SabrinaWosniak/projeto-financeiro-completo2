import pytest

from financeiro.dominio.categoria import Categoria
from financeiro.dominio.conta import Conta
from financeiro.dominio.lancamento import Lancamento
from datetime import date


class TestEstadosDaConta:
    def test_conta_nasce_ativa_e_com_id(self) -> None:
        conta = Conta("Nubank", 100.0)

        assert conta.ativa is True
        assert conta.id

    def test_encerrar_conta_com_saldo_zero(self) -> None:
        conta = Conta("Nubank", 0.0)

        conta.encerrar()

        assert conta.ativa is False

    def test_nao_encerra_conta_com_saldo(self) -> None:
        conta = Conta("Nubank", 50.0)

        with pytest.raises(ValueError, match="saldo zero"):
            conta.encerrar()

        assert conta.ativa is True

    def test_nao_encerra_duas_vezes(self) -> None:
        conta = Conta("Nubank")
        conta.encerrar()

        with pytest.raises(ValueError, match="encerrada"):
            conta.encerrar()

    def test_conta_encerrada_recusa_operacoes(self) -> None:
        conta = Conta("Nubank")
        conta.encerrar()

        with pytest.raises(ValueError):
            conta.depositar(10.0)

        with pytest.raises(ValueError):
            conta.sacar(10.0)

    def test_saldo_inicial_negativo_e_recusado(self) -> None:
        with pytest.raises(ValueError):
            Conta("Nubank", -1.0)


class TestRegistrarLancamentoNaConta:
    def _lanc(self, tipo: str, valor: float) -> Lancamento:
        return Lancamento("x", valor, date.today(), Categoria("Geral"), tipo)

    def test_credito_soma_no_saldo(self) -> None:
        conta = Conta("Nubank", 100.0)

        conta.registrar(self._lanc("credito", 50.0))

        assert conta.saldo == 150.0

    def test_debito_subtrai_do_saldo(self) -> None:
        conta = Conta("Nubank", 100.0)

        conta.registrar(self._lanc("debito", 30.0))

        assert conta.saldo == 70.0

    def test_debito_maior_que_saldo_e_recusado(self) -> None:
        conta = Conta("Nubank", 10.0)

        with pytest.raises(ValueError, match="Saldo insuficiente"):
            conta.registrar(self._lanc("debito", 30.0))

        assert conta.saldo == 10.0

    def test_lancamento_tem_id_proprio(self) -> None:
        a = self._lanc("debito", 1.0)
        b = self._lanc("debito", 1.0)

        assert a.id != b.id
