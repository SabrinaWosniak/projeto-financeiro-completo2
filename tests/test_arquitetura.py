"""Testes de arquitetura: a regra de dependência é verificada, não só combinada.

Lê o código-fonte (módulo ast) e confere quem importa quem.
Regra geral: as dependências apontam para dentro.
    interface -> aplicacao -> dominio <- infraestrutura
"""
import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent / "financeiro"


def imports_de(pasta: str) -> dict[str, set[str]]:
    """Devolve {arquivo: módulos importados} de uma camada."""
    resultado = {}
    for arquivo in (RAIZ / pasta).rglob("*.py"):
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        modulos = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                modulos.update(alias.name for alias in no.names)
            elif isinstance(no, ast.ImportFrom) and no.module:
                modulos.add(no.module)
        resultado[str(arquivo.relative_to(RAIZ))] = modulos
    return resultado


def violacoes(pasta: str, proibidos: list[str]) -> list[str]:
    return [
        f"{arquivo} importa {modulo}"
        for arquivo, modulos in imports_de(pasta).items()
        for modulo in modulos
        for proibido in proibidos
        if modulo == f"financeiro.{proibido}" or modulo.startswith(f"financeiro.{proibido}.")
    ]


def test_dominio_nao_depende_de_nenhuma_outra_camada() -> None:
    assert violacoes("dominio", ["aplicacao", "infraestrutura", "interface", "composicao"]) == []


def test_aplicacao_nao_depende_de_infraestrutura_nem_interface() -> None:
    assert violacoes("aplicacao", ["infraestrutura", "interface", "composicao"]) == []


def test_interface_so_conhece_a_aplicacao() -> None:
    """O menu só chama casos de uso: não enxerga domínio nem infraestrutura."""
    assert violacoes("interface", ["dominio", "infraestrutura", "composicao"]) == []


def test_infraestrutura_nao_depende_da_interface() -> None:
    assert violacoes("infraestrutura", ["interface", "composicao"]) == []


def test_dominio_nao_usa_sqlite_nem_print_de_terminal() -> None:
    """Domínio puro: sem banco de dados no import."""
    for arquivo, modulos in imports_de("dominio").items():
        assert "sqlite3" not in modulos, arquivo


@pytest.mark.parametrize("camada", ["dominio", "aplicacao", "infraestrutura", "interface"])
def test_camadas_existem_como_pacotes(camada: str) -> None:
    assert (RAIZ / camada / "__init__.py").exists()


def test_so_a_raiz_de_composicao_conhece_todas_as_camadas() -> None:
    modulos = set()
    for no in ast.walk(ast.parse((RAIZ / "composicao.py").read_text(encoding="utf-8"))):
        if isinstance(no, ast.ImportFrom) and no.module:
            modulos.add(no.module.split(".")[1])
    assert {"aplicacao", "dominio", "infraestrutura"} <= modulos
