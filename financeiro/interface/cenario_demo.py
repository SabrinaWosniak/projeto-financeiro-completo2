"""Dados fixos para demonstrar o sistema. Usa só os casos de uso."""
from datetime import date, timedelta

from financeiro.aplicacao.casos_de_uso import CasosDeUso


def carregar_cenario_demo(casos: CasosDeUso) -> bool:
    """Cria dados de exemplo se ainda não houver nenhuma conta.

    Devolve True se carregou, False se já havia dados (assim rodar o
    programa duas vezes não duplica nada).
    """
    if casos.listar_contas.executar():
        return False

    hoje = date.today()
    corrente = casos.criar_conta.executar("Conta Corrente", 500.0)
    casos.criar_conta.executar("Poupança", 2000.0)

    registrar = casos.registrar_lancamento.executar
    registrar(corrente["id"], "Salário", 3000.0, hoje - timedelta(days=5), "Renda", "credito")
    registrar(corrente["id"], "Aluguel", 1200.0, hoje - timedelta(days=3), "Moradia", "debito")
    registrar(corrente["id"], "Mercado", 350.90, hoje - timedelta(days=1), "Alimentação", "debito")

    casos.aplicar_ajuste.executar(corrente["id"], "rendimento", "percentual", 1.0)
    return True
