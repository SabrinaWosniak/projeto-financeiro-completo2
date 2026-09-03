from abc import ABC, abstractmethod


class EstrategiaRendimento(ABC):

    @abstractmethod
    def calcular(self, valor: float) -> float:
        pass


class RendimentoFixo(EstrategiaRendimento):

    def __init__(self, taxa: float) -> None:
        if taxa < 0:
            raise ValueError("Taxa não pode ser negativa")

        self._taxa = taxa

    def calcular(self, valor: float) -> float:
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")

        return valor * self._taxa


class RendimentoPercentual(EstrategiaRendimento):

    def __init__(self, percentual: float) -> None:
        if percentual < 0:
            raise ValueError("Percentual não pode ser negativo")

        self._percentual = percentual

    def calcular(self, valor: float) -> float:
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")

        return valor * (self._percentual / 100)