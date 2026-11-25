from dataclasses import dataclass
from datetime import date

from financeiro.aplicacao.erros import ContaNaoEncontrada
from financeiro.aplicacao.portas import BarramentoEventos
from financeiro.dominio.categoria import Categoria
from financeiro.dominio.conta import Conta
from financeiro.dominio.eventos import LancamentoRegistrado, SaldoAjustado
from financeiro.dominio.extrato import Extrato
from financeiro.dominio.fabricas import FabricaEstrategias
from financeiro.dominio.fechamento import Fechamento
from financeiro.dominio.lancamento import Lancamento
from financeiro.dominio.regras_lancamento import RegraLancamento
from financeiro.dominio.repositorios import RepositorioContas


def _dados_conta(conta: Conta) -> dict:
    return {
        "id": conta.id,
        "nome": conta.nome,
        "saldo": conta.saldo,
        "ativa": conta.ativa,
    }


def _obter_ou_falhar(repositorio: RepositorioContas, conta_id: str) -> Conta:
    conta = repositorio.obter(conta_id)

    if conta is None:
        raise ContaNaoEncontrada(conta_id)

    return conta


class CriarConta:
    def __init__(self, repositorio: RepositorioContas) -> None:
        self._repositorio = repositorio

    def executar(self, nome: str, saldo_inicial: float = 0.0) -> dict:
        conta = Conta(nome, saldo_inicial)
        self._repositorio.salvar(conta)
        return _dados_conta(conta)


class ListarContas:
    def __init__(self, repositorio: RepositorioContas) -> None:
        self._repositorio = repositorio

    def executar(self) -> list[dict]:
        return [_dados_conta(c) for c in self._repositorio.listar()]


class RegistrarLancamento:
    def __init__(
        self,
        repositorio: RepositorioContas,
        barramento: BarramentoEventos,
        regras: RegraLancamento,
    ) -> None:
        self._repositorio = repositorio
        self._barramento = barramento
        self._regras = regras

    def executar(
        self,
        conta_id: str,
        descricao: str,
        valor: float,
        data: date,
        categoria: str,
        tipo: str,
    ) -> dict:
        conta = _obter_ou_falhar(self._repositorio, conta_id)

        lancamento = Lancamento(
            descricao, valor, data, Categoria(categoria), tipo, conta_id=conta_id
        )

        do_dia = [
            l for l in self._repositorio.listar_lancamentos(conta_id) if l.data == data
        ]
        self._regras.validar(lancamento, do_dia)  # cadeia de regras

        conta.registrar(lancamento)  # regra do domínio (saldo, conta ativa)

        # saldo + lançamento gravados juntos (atômico, dentro do repositório)
        self._repositorio.registrar_lancamento(conta, lancamento)

        # só depois de gravado é que o fato é anunciado
        self._barramento.publicar(
            LancamentoRegistrado(
                conta_id=conta_id,
                lancamento_id=lancamento.id,
                tipo=tipo,
                valor=valor,
                saldo_apos=conta.saldo,
            )
        )
        return _dados_conta(conta)


class AplicarAjuste:
    """Aplica rendimento, juros ou correção usando a estratégia escolhida."""

    def __init__(
        self, repositorio: RepositorioContas, barramento: BarramentoEventos
    ) -> None:
        self._repositorio = repositorio
        self._barramento = barramento

    def opcoes(self) -> list[dict]:
        return FabricaEstrategias.opcoes()

    def executar(
        self, conta_id: str, familia: str, modalidade: str, valor: float
    ) -> dict:
        conta = _obter_ou_falhar(self._repositorio, conta_id)
        estrategia = FabricaEstrategias.criar(familia, modalidade, valor)

        aplicar = {
            "rendimento": conta.aplicar_rendimento,
            "juros": conta.aplicar_juros,
            "correcao": conta.aplicar_correcao,
        }[familia]

        saldo_antes = conta.saldo
        aplicar(estrategia)
        self._repositorio.salvar(conta)

        self._barramento.publicar(
            SaldoAjustado(
                conta_id=conta_id,
                ajuste=familia,
                valor_aplicado=round(conta.saldo - saldo_antes, 2),
                saldo_apos=conta.saldo,
            )
        )
        return _dados_conta(conta)


class GerarExtrato:
    def __init__(self, repositorio: RepositorioContas) -> None:
        self._repositorio = repositorio

    def executar(self, conta_id: str) -> dict:
        conta = _obter_ou_falhar(self._repositorio, conta_id)
        lancamentos = self._repositorio.listar_lancamentos(conta_id)

        if lancamentos:
            extrato = Extrato([Fechamento(lancamentos)])
            debitos = extrato.total_debitos()
            creditos = extrato.total_creditos()
        else:
            debitos = creditos = 0.0

        return {
            "conta": _dados_conta(conta),
            "lancamentos": [
                {
                    "data": l.data,
                    "descricao": l.descricao,
                    "categoria": l.categoria.nome,
                    "tipo": l.tipo,
                    "valor": l.valor,
                }
                for l in lancamentos
            ],
            "total_debitos": debitos,
            "total_creditos": creditos,
        }


class EncerrarConta:
    def __init__(self, repositorio: RepositorioContas) -> None:
        self._repositorio = repositorio

    def executar(self, conta_id: str) -> dict:
        conta = _obter_ou_falhar(self._repositorio, conta_id)
        conta.encerrar()
        self._repositorio.salvar(conta)
        return _dados_conta(conta)


@dataclass
class CasosDeUso:
    """Tudo o que uma interface (menu, REST...) pode chamar."""

    criar_conta: CriarConta
    listar_contas: ListarContas
    registrar_lancamento: RegistrarLancamento
    aplicar_ajuste: AplicarAjuste
    gerar_extrato: GerarExtrato
    encerrar_conta: EncerrarConta
