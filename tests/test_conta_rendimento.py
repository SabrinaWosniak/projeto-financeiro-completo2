import pytest

from financeiro.conta import Conta
from financeiro.estrategias.rendimento import RendimentoFixo


class TestContaRendimento:

    def test_aplicar_rendimento(self) -> None:
        conta = Conta("Conta Principal", 1000.0)
        estrategia = RendimentoFixo(0.10)

        conta.aplicar_rendimento(estrategia)

        assert conta.saldo == 1100.0

    def test_aplicar_rendimento_valor_positivo(self) -> None:
        conta = Conta("Conta Principal", 500.0)
        estrategia = RendimentoFixo(0.20)

        conta.aplicar_rendimento(estrategia)

        assert conta.saldo == 600.0