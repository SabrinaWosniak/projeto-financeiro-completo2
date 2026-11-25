"""Raiz de composição: o ÚNICO lugar que conhece todas as camadas.

Aqui se decide quem implementa cada contrato (memória ou SQLite), quais
regras entram na cadeia e quais manipuladores reagem a cada evento.
"""
from financeiro.aplicacao.casos_de_uso import (
    AplicarAjuste,
    CasosDeUso,
    CriarConta,
    EncerrarConta,
    GerarExtrato,
    ListarContas,
    RegistrarLancamento,
)
from financeiro.aplicacao.manipuladores import (
    AlertarSaldoBaixo,
    NotificarAjuste,
    NotificarLancamento,
)
from financeiro.dominio.eventos import LancamentoRegistrado, SaldoAjustado
from financeiro.dominio.regras_lancamento import (
    DataNaoFutura,
    LimiteDiarioDeDebitos,
    ValorMaximoPorLancamento,
)
from financeiro.infraestrutura.barramento_memoria import BarramentoEmMemoria
from financeiro.infraestrutura.notificador_terminal import NotificadorTerminal
from financeiro.infraestrutura.repositorio_memoria import RepositorioContasEmMemoria
from financeiro.infraestrutura.repositorio_sqlite import RepositorioContasSqlite


def montar_sistema(caminho_db: str | None = "financeiro.db") -> CasosDeUso:
    """Monta o sistema. caminho_db=None usa memória (nada é guardado)."""
    if caminho_db is None:
        repositorio = RepositorioContasEmMemoria()
    else:
        repositorio = RepositorioContasSqlite(caminho_db)

    notificador = NotificadorTerminal()

    # eventos: quem publica não sabe quem reage
    barramento = BarramentoEmMemoria(ao_falhar=notificador.avisar)
    barramento.assinar(LancamentoRegistrado, NotificarLancamento(notificador))
    barramento.assinar(LancamentoRegistrado, AlertarSaldoBaixo(notificador, 100.0))
    barramento.assinar(SaldoAjustado, NotificarAjuste(notificador))

    # cadeia de regras (padrão do bônus): para ter outra regra, encaixe aqui
    regras = ValorMaximoPorLancamento(10_000.0)
    regras.encadear(LimiteDiarioDeDebitos(5_000.0)).encadear(DataNaoFutura())

    return CasosDeUso(
        criar_conta=CriarConta(repositorio),
        listar_contas=ListarContas(repositorio),
        registrar_lancamento=RegistrarLancamento(repositorio, barramento, regras),
        aplicar_ajuste=AplicarAjuste(repositorio, barramento),
        gerar_extrato=GerarExtrato(repositorio),
        encerrar_conta=EncerrarConta(repositorio),
    )
