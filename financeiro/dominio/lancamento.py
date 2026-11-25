from datetime import date
from uuid import uuid4


class Lancamento:

    def __init__(
        self,
        descricao: str,
        valor: float,
        data: date,
        categoria,
        tipo: str,
        conta_id: str | None = None,
        id: str | None = None,
    ) -> None:

        if not descricao:
            raise ValueError("Descrição é obrigatória")

        if valor <= 0:
            raise ValueError("Valor deve ser positivo")

        if tipo not in ["debito", "credito"]:
            raise ValueError("Tipo deve ser 'debito' ou 'credito'")

        self._id = id or uuid4().hex
        self._conta_id = conta_id
        self._descricao = descricao
        self._valor = valor
        self._data = data
        self._categoria = categoria
        self._tipo = tipo

    @property
    def id(self) -> str:
        return self._id

    @property
    def conta_id(self) -> str | None:
        return self._conta_id

    @property
    def descricao(self) -> str:
        return self._descricao

    @property
    def valor(self) -> float:
        return self._valor

    @property
    def data(self) -> date:
        return self._data

    @property
    def categoria(self):
        return self._categoria

    @property
    def tipo(self) -> str:
        return self._tipo

    #ela armazena informações como descrição, valor, data, categoria e tipo, indicando se é um débito ou crédito. Ela também valida esses dados antes de criar o lançamento.