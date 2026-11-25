"""Contratos que a aplicação precisa; quem implementa fica na infraestrutura."""
from abc import ABC, abstractmethod
from typing import Callable


class BarramentoEventos(ABC):
    @abstractmethod
    def assinar(self, tipo_evento: type, manipulador: Callable) -> None:
        """Registra um manipulador para um tipo de evento."""

    @abstractmethod
    def publicar(self, evento) -> None:
        """Entrega o evento a todos os manipuladores do seu tipo."""


class Notificador(ABC):
    @abstractmethod
    def avisar(self, mensagem: str) -> None:
        """Mostra uma mensagem para quem usa o sistema."""
