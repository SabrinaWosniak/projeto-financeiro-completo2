from financeiro.dominio.conta import Conta
from financeiro.dominio.estrategias.juros import JurosSimples


class TestContaJuros:

    def test_aplicar_juros(self) -> None:
        conta = Conta("Conta Principal", 1000.0)
        estrategia = JurosSimples(0.10)

        conta.aplicar_juros(estrategia)

        assert conta.saldo == 1100.0