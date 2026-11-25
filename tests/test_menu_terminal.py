"""Testa o menu com respostas digitadas "de mentira" (entrada falsa)."""
from financeiro.composicao import montar_sistema
from financeiro.interface.menu_terminal import MenuTerminal


def rodar(respostas: list[str], casos=None) -> str:
    casos = casos or montar_sistema(None)  # None = memória
    fila = iter(respostas)
    saida: list[str] = []
    MenuTerminal(casos, entrada=lambda _: next(fila), saida=saida.append).executar()
    return "\n".join(saida)


def test_sair() -> None:
    assert "Até logo!" in rodar(["0"])


def test_opcao_invalida() -> None:
    assert "Opção inválida" in rodar(["9", "0"])


def test_criar_e_listar_conta() -> None:
    saida = rodar(["1", "Nubank", "1000,50", "2", "0"])

    assert "Conta 'Nubank' criada" in saida
    assert "Nubank - R$ 1.000,50" in saida


def test_registrar_lancamento_e_ver_extrato(capsys) -> None:
    saida = rodar(
        ["1", "Nubank", "1000", "3", "1", "1", "Mercado", "200", "Alimentação", "", "5", "1", "0"]
    )

    # o aviso vem do manipulador de evento (NotificadorTerminal), não do menu
    assert "Lançamento de débito de R$ 200,00 registrado" in capsys.readouterr().out
    assert "Mercado" in saida
    assert "Saldo atual:       R$ 800,00" in saida


def test_erro_do_dominio_vira_mensagem_e_o_menu_continua() -> None:
    saida = rodar(["1", "Nubank", "50", "3", "1", "1", "Luxo", "500", "Geral", "", "0"])

    assert "Erro: Saldo insuficiente" in saida
    assert "Até logo!" in saida


def test_numero_invalido_vira_mensagem() -> None:
    saida = rodar(["1", "Nubank", "abc", "0"])

    assert "Erro: Número inválido" in saida


def test_data_invalida_vira_mensagem() -> None:
    saida = rodar(["1", "N", "100", "3", "1", "1", "x", "10", "G", "31-02-2026", "0"])

    assert "Data inválida" in saida


def test_ajuste_de_rendimento(capsys) -> None:
    # opção 1 do menu de ajustes = rendimento fixo, 10%
    rodar(["1", "Nubank", "1000", "4", "1", "1", "10", "0"])

    assert "Ajuste de rendimento: R$ 100,00 aplicado" in capsys.readouterr().out


def test_sem_contas_o_menu_avisa() -> None:
    assert "Nenhuma conta cadastrada" in rodar(["2", "3", "0"])


def test_encerrar_conta_com_saldo_mostra_erro() -> None:
    saida = rodar(["1", "Nubank", "10", "6", "1", "0"])

    assert "Erro: Só é possível encerrar uma conta com saldo zero" in saida
