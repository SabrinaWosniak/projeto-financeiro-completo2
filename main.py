"""Ponto de entrada: python main.py [--memoria] [--db ARQUIVO] [--demo]"""
import argparse

from financeiro.composicao import montar_sistema
from financeiro.interface.cenario_demo import carregar_cenario_demo
from financeiro.interface.menu_terminal import MenuTerminal


def main() -> None:
    parser = argparse.ArgumentParser(description="Controle Financeiro Pessoal")
    parser.add_argument(
        "--db", default="financeiro.db", help="arquivo SQLite (padrão: financeiro.db)"
    )
    parser.add_argument(
        "--memoria", action="store_true", help="não grava nada em disco"
    )
    parser.add_argument(
        "--demo", action="store_true", help="carrega contas de exemplo se estiver vazio"
    )
    args = parser.parse_args()

    casos = montar_sistema(None if args.memoria else args.db)

    if args.demo and carregar_cenario_demo(casos):
        print("Dados de exemplo carregados.")

    MenuTerminal(casos).executar()


if __name__ == "__main__":
    main()
