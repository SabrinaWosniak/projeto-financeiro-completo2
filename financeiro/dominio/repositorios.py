from abc import ABC, abstractmethod

from financeiro.dominio.conta import Conta
from financeiro.dominio.lancamento import Lancamento


class RepositorioContas(ABC):
    """Contrato de guarda de contas e seus lançamentos.

    Quem usa só conhece este contrato; se os dados estão em memória ou em
    SQLite é decisão da raiz de composição.
    """

    @abstractmethod
    def salvar(self, conta: Conta) -> None:
        """Insere a conta ou atualiza se ela já existir."""

    @abstractmethod
    def obter(self, conta_id: str) -> Conta | None:
        """Devolve a conta ou None se não existir."""

    @abstractmethod
    def listar(self) -> list[Conta]:
        """Todas as contas, na ordem em que foram criadas."""

    @abstractmethod
    def registrar_lancamento(self, conta: Conta, lancamento: Lancamento) -> None:
        """Grava o lançamento E o novo saldo da conta de forma atômica.

        Ou os dois ficam gravados, ou nenhum. Se o lançamento já existir
        (mesmo id), levanta ValueError e o saldo guardado não muda.
        """

    @abstractmethod
    def listar_lancamentos(self, conta_id: str) -> list[Lancamento]:
        """Lançamentos da conta, na ordem em que foram registrados."""
