"""Roda o programa de verdade, duas vezes, e confere que os dados ficaram."""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def executar(argumentos: list[str], entrada: str) -> str:
    resultado = subprocess.run(
        [sys.executable, "main.py", *argumentos],
        input=entrada, capture_output=True, text=True, cwd=RAIZ, timeout=30,
    )
    assert resultado.returncode == 0, resultado.stderr
    return resultado.stdout


def test_dados_persistem_entre_duas_execucoes(tmp_path) -> None:
    banco = str(tmp_path / "demo.db")

    primeira = executar(["--db", banco], "1\nMinha Conta\n250\n0\n")
    assert "Conta 'Minha Conta' criada" in primeira

    segunda = executar(["--db", banco], "2\n0\n")  # programa novo, mesmo arquivo
    assert "Minha Conta - R$ 250,00" in segunda


def test_demo_nao_duplica_dados_na_segunda_execucao(tmp_path) -> None:
    banco = str(tmp_path / "demo.db")

    primeira = executar(["--db", banco, "--demo"], "2\n0\n")
    segunda = executar(["--db", banco, "--demo"], "2\n0\n")

    assert "Dados de exemplo carregados." in primeira
    assert "Dados de exemplo carregados." not in segunda
    assert segunda.count("Conta Corrente") == 1


def test_modo_memoria_nao_cria_arquivo(tmp_path) -> None:
    executar(["--memoria"], "1\nTemporaria\n0\n0\n")

    assert not (RAIZ / "financeiro.db").exists()
