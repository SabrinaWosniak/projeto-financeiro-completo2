import logging
from collections import defaultdict
from typing import Callable

from financeiro.aplicacao.portas import BarramentoEventos

log = logging.getLogger(__name__)


class BarramentoEmMemoria(BarramentoEventos):
    """Entrega cada evento aos manipuladores do seu tipo.

    Decisão: a falha de uma reação é ISOLADA. O lançamento já foi gravado
    (o fato aconteceu), então um manipulador quebrado não pode desfazê-lo
    nem impedir os outros de rodar. A falha é registrada em `falhas`, no
    log e, se houver, comunicada por `ao_falhar`.
    """

    def __init__(self, ao_falhar: Callable[[str], None] | None = None) -> None:
        self._manipuladores: dict[type, list[Callable]] = defaultdict(list)
        self._ao_falhar = ao_falhar
        self.falhas: list[tuple[object, Exception]] = []

    def assinar(self, tipo_evento: type, manipulador: Callable) -> None:
        self._manipuladores[tipo_evento].append(manipulador)

    def publicar(self, evento) -> None:
        for manipulador in self._manipuladores[type(evento)]:
            try:
                manipulador(evento)
            except Exception as erro:  # isolamento: um erro não derruba os demais
                self.falhas.append((evento, erro))
                nome = type(manipulador).__name__
                log.warning("Reação %s falhou: %s", nome, erro)

                if self._ao_falhar is not None:
                    self._ao_falhar(f"A reação {nome} falhou: {erro}")
