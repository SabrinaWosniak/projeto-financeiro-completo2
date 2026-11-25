"""Suíte de contrato: os MESMOS testes rodam contra todas as implementações.

Para incluir uma nova implementação (ex.: outro banco), basta adicionar
uma linha em IMPLEMENTACOES.
"""
from datetime import date

import pytest

from financeiro.dominio.categoria import Categoria
from financeiro.dominio.conta import Conta
from financeiro.dominio.lancamento import Lancamento
from financeiro.infraestrutura.repositorio_memoria import RepositorioContasEmMemoria
from financeiro.infraestrutura.repositorio_sqlite import RepositorioContasSqlite

IMPLEMENTACOES = {
    "memoria": RepositorioContasEmMemoria,
    "sqlite": lambda: RepositorioContasSqlite(":memory:"),
}


@pytest.fixture(params=list(IMPLEMENTACOES))
def repo(request):
    return IMPLEMENTACOES[request.param]()


def novo_lancamento(conta: Conta, valor=10.0, tipo="debito", **extra) -> Lancamento:
    return Lancamento(
        "Compra", valor, date(2026, 6, 1), Categoria("Mercado"), tipo,
        conta_id=conta.id, **extra,
    )


class TestContas:
    def test_obter_conta_inexistente_devolve_none(self, repo) -> None:
        assert repo.obter("nao-existe") is None

    def test_salvar_e_obter(self, repo) -> None:
        conta = Conta("Nubank", 100.0)

        repo.salvar(conta)
        lida = repo.obter(conta.id)

        assert (lida.id, lida.nome, lida.saldo, lida.ativa) == (
            conta.id, "Nubank", 100.0, True,
        )

    def test_salvar_de_novo_atualiza(self, repo) -> None:
        conta = Conta("Nubank", 100.0)
        repo.salvar(conta)

        conta.depositar(50.0)
        repo.salvar(conta)

        assert repo.obter(conta.id).saldo == 150.0
        assert len(repo.listar()) == 1

    def test_estado_encerrada_e_guardado(self, repo) -> None:
        conta = Conta("Nubank", 0.0)
        conta.encerrar()

        repo.salvar(conta)

        assert repo.obter(conta.id).ativa is False

    def test_listar_na_ordem_de_criacao(self, repo) -> None:
        nomes = ["A", "B", "C"]
        for nome in nomes:
            repo.salvar(Conta(nome))

        assert [c.nome for c in repo.listar()] == nomes

    def test_alterar_objeto_lido_nao_altera_o_guardado(self, repo) -> None:
        conta = Conta("Nubank", 100.0)
        repo.salvar(conta)

        lida = repo.obter(conta.id)
        lida.depositar(999.0)

        assert repo.obter(conta.id).saldo == 100.0


class TestLancamentos:
    def test_registrar_grava_lancamento_e_saldo(self, repo) -> None:
        conta = Conta("Nubank", 100.0)
        repo.salvar(conta)
        lancamento = novo_lancamento(conta, 30.0)

        conta.registrar(lancamento)
        repo.registrar_lancamento(conta, lancamento)

        assert repo.obter(conta.id).saldo == 70.0
        lidos = repo.listar_lancamentos(conta.id)
        assert len(lidos) == 1
        lido = lidos[0]
        assert (lido.id, lido.descricao, lido.valor, lido.data, lido.tipo) == (
            lancamento.id, "Compra", 30.0, date(2026, 6, 1), "debito",
        )
        assert lido.categoria.nome == "Mercado"
        assert lido.conta_id == conta.id

    def test_listar_lancamentos_so_da_conta_e_em_ordem(self, repo) -> None:
        a, b = Conta("A", 100.0), Conta("B", 100.0)
        repo.salvar(a)
        repo.salvar(b)

        for conta, valor in [(a, 1.0), (b, 2.0), (a, 3.0)]:
            lanc = novo_lancamento(conta, valor)
            conta.registrar(lanc)
            repo.registrar_lancamento(conta, lanc)

        assert [l.valor for l in repo.listar_lancamentos(a.id)] == [1.0, 3.0]
        assert [l.valor for l in repo.listar_lancamentos(b.id)] == [2.0]

    def test_conta_sem_lancamentos_devolve_lista_vazia(self, repo) -> None:
        assert repo.listar_lancamentos("nao-existe") == []

    def test_lancamento_duplicado_e_recusado_e_saldo_nao_muda(self, repo) -> None:
        """Atomicidade: se o lançamento falha, o saldo também não é gravado."""
        conta = Conta("Nubank", 100.0)
        repo.salvar(conta)
        lancamento = novo_lancamento(conta, 30.0)
        conta.registrar(lancamento)
        repo.registrar_lancamento(conta, lancamento)  # saldo guardado: 70

        conta.registrar(lancamento)  # mesmo lançamento outra vez: saldo 40 na memória

        with pytest.raises(ValueError, match="já registrado"):
            repo.registrar_lancamento(conta, lancamento)

        assert repo.obter(conta.id).saldo == 70.0
        assert len(repo.listar_lancamentos(conta.id)) == 1

    def test_lancamento_de_outra_conta_e_recusado(self, repo) -> None:
        a, b = Conta("A", 100.0), Conta("B", 100.0)
        repo.salvar(a)
        repo.salvar(b)

        with pytest.raises(ValueError, match="outra conta"):
            repo.registrar_lancamento(a, novo_lancamento(b))
