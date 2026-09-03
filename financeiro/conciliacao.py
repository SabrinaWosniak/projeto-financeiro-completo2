class Conciliacao:
    def __init__(self, debitos: list, creditos: list) -> None:
        self._debitos = list(debitos)
        self._creditos = list(creditos)

    def total_debitos(self) -> float:
        return sum(lancamento.valor for lancamento in self._debitos)

    def total_creditos(self) -> float:
        return sum(lancamento.valor for lancamento in self._creditos)

    def esta_conciliada(self) -> bool:
        return self.total_debitos() == self.total_creditos()

    def verificar(self) -> None:
        if not self.esta_conciliada():
            raise ValueError(
                f"Conciliação não bate: "
                f"débitos = {self.total_debitos()}, "
                f"créditos = {self.total_creditos()}"
            )
#é responsável por conferir se os valores financeiros estão corretos. Ela recebe os valores de débito e crédito, calcula o total de cada um e depois compara os dois valores. Se os totais forem iguais,  está correta. Caso sejam diferentes, o sistema gera um erro informando os valores encontrados.