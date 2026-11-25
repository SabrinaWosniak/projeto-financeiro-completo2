"""Fixtures compartilhadas e dublês de teste."""
from datetime import date

import pytest

from financeiro.aplicacao.casos_de_uso import (
    AplicarAjuste,
    CriarConta,
    EncerrarConta,
    GerarExtrato,
    ListarContas,
    RegistrarLancamento,
)
from financeiro.aplicacao.portas import BarramentoEventos, Notificador
from financeiro.dominio.regras_lancamento import (
    DataNaoFutura,
    LimiteDiarioDeDebitos,
    ValorMaximoPorLancamento,
)
from financeiro.infraestrutura.repositorio_memoria import RepositorioContasEmMemoria


class NotificadorFalso(Notificador):
    def __init__(self) -> None:
        self.mensagens: list[str] = []

    def avisar(self, mensagem: str) -> None:
        self.mensagens.append(mensagem)


class BarramentoFalso(BarramentoEventos):
    """Só guarda o que foi publicado, para testar quem publica."""

    def __init__(self) -> None:
        self.publicados: list = []

    def assinar(self, tipo_evento, manipulador) -> None:
        pass

    def publicar(self, evento) -> None:
        self.publicados.append(evento)


def cadeia_padrao() -> ValorMaximoPorLancamento:
    regras = ValorMaximoPorLancamento(10_000.0)
    regras.encadear(LimiteDiarioDeDebitos(5_000.0)).encadear(DataNaoFutura())
    return regras


@pytest.fixture
def repositorio():
    return RepositorioContasEmMemoria()


@pytest.fixture
def barramento():
    return BarramentoFalso()


@pytest.fixture
def conta_id(repositorio):
    return CriarConta(repositorio).executar("Corrente", 1000.0)["id"]


@pytest.fixture
def registrar(repositorio, barramento):
    return RegistrarLancamento(repositorio, barramento, cadeia_padrao())


@pytest.fixture
def hoje() -> date:
    return date.today()
