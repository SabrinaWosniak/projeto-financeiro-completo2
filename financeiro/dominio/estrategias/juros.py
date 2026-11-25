from abc import ABC, abstractmethod


class EstrategiaJuros(ABC):

    @abstractmethod
    def calcular(self, valor: float) -> float:
        pass


class JurosSimples(EstrategiaJuros):

    def __init__(self, taxa: float) -> None:
        if taxa < 0:
            raise ValueError("Taxa não pode ser negativa")

        self._taxa = taxa

    def calcular(self, valor: float) -> float:
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")

        return valor * self._taxa

class JurosCompostos(EstrategiaJuros):

    def __init__(self, taxa: float) -> None:
        if taxa < 0:
            raise ValueError("Taxa não pode ser negativa")

        self._taxa = taxa

    def calcular(self, valor: float) -> float:
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")

        return valor * ((1 + self._taxa) ** 2 - 1)