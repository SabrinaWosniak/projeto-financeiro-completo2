import sqlite3
from datetime import date

from financeiro.dominio.categoria import Categoria
from financeiro.dominio.conta import Conta
from financeiro.dominio.lancamento import Lancamento
from financeiro.dominio.repositorios import RepositorioContas

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS contas (
    id    TEXT PRIMARY KEY,
    nome  TEXT NOT NULL,
    saldo REAL NOT NULL,
    ativa INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS lancamentos (
    id        TEXT PRIMARY KEY,
    conta_id  TEXT NOT NULL REFERENCES contas(id),
    descricao TEXT NOT NULL,
    valor     REAL NOT NULL,
    data      TEXT NOT NULL,
    categoria TEXT NOT NULL,
    tipo      TEXT NOT NULL
);
"""

_SALVAR_CONTA = """
INSERT INTO contas (id, nome, saldo, ativa) VALUES (?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    nome = excluded.nome, saldo = excluded.saldo, ativa = excluded.ativa
"""


class RepositorioContasSqlite(RepositorioContas):
    """Guarda contas e lançamentos em um arquivo SQLite (ou ':memory:')."""

    def __init__(self, caminho: str = "financeiro.db") -> None:
        self._conexao = sqlite3.connect(caminho)
        self._conexao.execute("PRAGMA foreign_keys = ON")
        self._conexao.executescript(_ESQUEMA)

    def fechar(self) -> None:
        self._conexao.close()

    @staticmethod
    def _dados_conta(conta: Conta) -> tuple:
        return (conta.id, conta.nome, conta.saldo, 1 if conta.ativa else 0)

    def salvar(self, conta: Conta) -> None:
        with self._conexao:
            self._conexao.execute(_SALVAR_CONTA, self._dados_conta(conta))

    def obter(self, conta_id: str) -> Conta | None:
        linha = self._conexao.execute(
            "SELECT id, nome, saldo, ativa FROM contas WHERE id = ?", (conta_id,)
        ).fetchone()
        return self._montar_conta(linha) if linha else None

    def listar(self) -> list[Conta]:
        linhas = self._conexao.execute(
            "SELECT id, nome, saldo, ativa FROM contas ORDER BY rowid"
        ).fetchall()
        return [self._montar_conta(l) for l in linhas]

    def registrar_lancamento(self, conta: Conta, lancamento: Lancamento) -> None:
        if lancamento.conta_id != conta.id:
            raise ValueError("Lançamento pertence a outra conta")

        try:
            # "with" abre uma transação: se qualquer comando falhar, o saldo
            # e o lançamento voltam ao que eram (rollback automático).
            with self._conexao:
                self._conexao.execute(_SALVAR_CONTA, self._dados_conta(conta))
                self._conexao.execute(
                    "INSERT INTO lancamentos "
                    "(id, conta_id, descricao, valor, data, categoria, tipo) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        lancamento.id,
                        lancamento.conta_id,
                        lancamento.descricao,
                        lancamento.valor,
                        lancamento.data.isoformat(),
                        lancamento.categoria.nome,
                        lancamento.tipo,
                    ),
                )
        except sqlite3.IntegrityError as erro:
            raise ValueError("Lançamento já registrado") from erro

    def listar_lancamentos(self, conta_id: str) -> list[Lancamento]:
        linhas = self._conexao.execute(
            "SELECT id, conta_id, descricao, valor, data, categoria, tipo "
            "FROM lancamentos WHERE conta_id = ? ORDER BY rowid",
            (conta_id,),
        ).fetchall()
        return [
            Lancamento(
                descricao=l[2],
                valor=l[3],
                data=date.fromisoformat(l[4]),
                categoria=Categoria(l[5]),
                tipo=l[6],
                conta_id=l[1],
                id=l[0],
            )
            for l in linhas
        ]

    @staticmethod
    def _montar_conta(linha: tuple) -> Conta:
        return Conta(nome=linha[1], saldo=linha[2], id=linha[0], ativa=bool(linha[3]))
