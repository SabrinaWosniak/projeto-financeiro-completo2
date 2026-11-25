"""O que é específico do SQLite: os dados sobrevivem ao reinício."""
from datetime import date

from financeiro.dominio.categoria import Categoria
from financeiro.dominio.conta import Conta
from financeiro.dominio.lancamento import Lancamento
from financeiro.infraestrutura.repositorio_sqlite import RepositorioContasSqlite


def test_dados_continuam_depois_de_reabrir_o_arquivo(tmp_path) -> None:
    caminho = str(tmp_path / "financeiro.db")

    primeiro = RepositorioContasSqlite(caminho)
    conta = Conta("Nubank", 100.0)
    primeiro.salvar(conta)
    lancamento = Lancamento(
        "Mercado", 40.0, date(2026, 6, 1), Categoria("Alimentação"), "debito",
        conta_id=conta.id,
    )
    conta.registrar(lancamento)
    primeiro.registrar_lancamento(conta, lancamento)
    primeiro.fechar()  # "desliga o programa"

    segundo = RepositorioContasSqlite(caminho)  # "liga de novo"

    contas = segundo.listar()
    assert [(c.nome, c.saldo) for c in contas] == [("Nubank", 60.0)]
    assert [l.descricao for l in segundo.listar_lancamentos(conta.id)] == ["Mercado"]
    segundo.fechar()
