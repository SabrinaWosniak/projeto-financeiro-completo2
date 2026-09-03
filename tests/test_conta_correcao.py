from financeiro.conta import Conta
from financeiro.estrategias.correcao import CorrecaoPercentual


class TestContaCorrecao:
    def test_aplicar_correcao(self) -> None:
        conta = Conta("Conta Principal", 1000.0)
        estrategia = CorrecaoPercentual(0.10)

        conta.aplicar_correcao(estrategia)

        assert conta.saldo == 1100.0