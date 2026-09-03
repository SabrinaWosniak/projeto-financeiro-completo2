from abc import ABC, abstractmethod


class EstrategiaCorrecao(ABC):

    @abstractmethod
    def calcular(self, valor: float) -> float:
        pass


class CorrecaoPercentual(EstrategiaCorrecao):

    def __init__(self, taxa: float) -> None:
        if taxa < 0:
            raise ValueError("Taxa não pode ser negativa")

        self._taxa = taxa

    def calcular(self, valor: float) -> float:
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")

        return valor * self._taxa


class CorrecaoFixa(EstrategiaCorrecao):

    def __init__(self, valor_correcao: float) -> None:
        if valor_correcao < 0:
            raise ValueError("Valor da correção não pode ser negativo")

        self._valor_correcao = valor_correcao

    def calcular(self, valor: float) -> float:
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")

        return self._valor_correcao