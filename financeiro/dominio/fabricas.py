from financeiro.dominio.estrategias.correcao import CorrecaoFixa, CorrecaoPercentual
from financeiro.dominio.estrategias.juros import JurosCompostos, JurosSimples
from financeiro.dominio.estrategias.rendimento import (
    RendimentoFixo,
    RendimentoPercentual,
)


class FabricaEstrategias:
    """Cria a estratégia certa a partir de dois nomes e um número.

    Quem chama (o caso de uso, o menu) não precisa conhecer as classes
    concretas. As taxas entram sempre em % (ex.: 1.5 = 1,5%) e a fábrica
    converte para o que cada classe espera. Só CorrecaoFixa usa R$.
    """

    # (familia, modalidade) -> (unidade do número, como construir)
    _CATALOGO = {
        ("rendimento", "fixo"): ("%", lambda v: RendimentoFixo(v / 100)),
        ("rendimento", "percentual"): ("%", lambda v: RendimentoPercentual(v)),
        ("juros", "simples"): ("%", lambda v: JurosSimples(v / 100)),
        ("juros", "composto"): ("%", lambda v: JurosCompostos(v / 100)),
        ("correcao", "percentual"): ("%", lambda v: CorrecaoPercentual(v / 100)),
        ("correcao", "fixa"): ("R$", lambda v: CorrecaoFixa(v)),
    }

    @classmethod
    def criar(cls, familia: str, modalidade: str, valor: float):
        chave = (familia, modalidade)

        if chave not in cls._CATALOGO:
            raise ValueError(f"Ajuste desconhecido: {familia}/{modalidade}")

        _, construir = cls._CATALOGO[chave]
        return construir(valor)

    @classmethod
    def opcoes(cls) -> list[dict]:
        return [
            {"familia": familia, "modalidade": modalidade, "unidade": unidade}
            for (familia, modalidade), (unidade, _) in cls._CATALOGO.items()
        ]
