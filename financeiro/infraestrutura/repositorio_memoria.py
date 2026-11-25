from copy import deepcopy

from financeiro.dominio.conta import Conta
from financeiro.dominio.lancamento import Lancamento
from financeiro.dominio.repositorios import RepositorioContas


class RepositorioContasEmMemoria(RepositorioContas):
    """Guarda cópias, como um banco de verdade faria: alterar o objeto
    devolvido não muda o que está guardado até chamar salvar()."""

    def __init__(self) -> None:
        self._contas: dict[str, Conta] = {}
        self._lancamentos: list[Lancamento] = []

    def salvar(self, conta: Conta) -> None:
        self._contas[conta.id] = deepcopy(conta)

    def obter(self, conta_id: str) -> Conta | None:
        conta = self._contas.get(conta_id)
        return deepcopy(conta) if conta else None

    def listar(self) -> list[Conta]:
        return [deepcopy(c) for c in self._contas.values()]

    def registrar_lancamento(self, conta: Conta, lancamento: Lancamento) -> None:
        if lancamento.conta_id != conta.id:
            raise ValueError("Lançamento pertence a outra conta")

        if any(l.id == lancamento.id for l in self._lancamentos):
            raise ValueError("Lançamento já registrado")

        # as duas gravações só acontecem depois de todas as verificações
        self._contas[conta.id] = deepcopy(conta)
        self._lancamentos.append(deepcopy(lancamento))

    def listar_lancamentos(self, conta_id: str) -> list[Lancamento]:
        return [deepcopy(l) for l in self._lancamentos if l.conta_id == conta_id]
