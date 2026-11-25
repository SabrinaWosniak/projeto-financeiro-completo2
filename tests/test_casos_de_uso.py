"""Casos de uso, e também quem PUBLICA eventos (com barramento falso)."""
from datetime import timedelta

import pytest

from financeiro.aplicacao.casos_de_uso import (
    AplicarAjuste,
    CriarConta,
    EncerrarConta,
    GerarExtrato,
    ListarContas,
)
from financeiro.aplicacao.erros import ContaNaoEncontrada
from financeiro.dominio.conta import Conta
from financeiro.dominio.eventos import LancamentoRegistrado, SaldoAjustado
from financeiro.dominio.regras_lancamento import RegraViolada


def registrar_debito(registrar, conta_id, hoje, valor=100.0, desc="Mercado"):
    return registrar.executar(conta_id, desc, valor, hoje, "Geral", "debito")


class TestContas:
    def test_criar_e_listar(self, repositorio) -> None:
        CriarConta(repositorio).executar("A", 10.0)
        CriarConta(repositorio).executar("B")

        nomes = [c["nome"] for c in ListarContas(repositorio).executar()]

        assert nomes == ["A", "B"]

    def test_criar_conta_sem_nome_e_erro(self, repositorio) -> None:
        with pytest.raises(ValueError):
            CriarConta(repositorio).executar("")

    def test_encerrar_conta_zerada(self, repositorio) -> None:
        conta = CriarConta(repositorio).executar("A")

        assert EncerrarConta(repositorio).executar(conta["id"])["ativa"] is False

    def test_encerrar_conta_com_saldo_e_erro(self, repositorio, conta_id) -> None:
        with pytest.raises(ValueError):
            EncerrarConta(repositorio).executar(conta_id)


class TestRegistrarLancamento:
    def test_atualiza_saldo_e_guarda_lancamento(
        self, registrar, repositorio, conta_id, hoje
    ) -> None:
        conta = registrar_debito(registrar, conta_id, hoje, 250.0)

        assert conta["saldo"] == 750.0
        assert repositorio.obter(conta_id).saldo == 750.0
        assert len(repositorio.listar_lancamentos(conta_id)) == 1

    def test_conta_inexistente(self, registrar, hoje) -> None:
        with pytest.raises(ContaNaoEncontrada):
            registrar_debito(registrar, "nao-existe", hoje)

    def test_saldo_insuficiente_nao_grava_nem_publica(
        self, registrar, repositorio, barramento, conta_id, hoje
    ) -> None:
        with pytest.raises(ValueError, match="Saldo insuficiente"):
            registrar_debito(registrar, conta_id, hoje, 5000.0)

        assert repositorio.obter(conta_id).saldo == 1000.0
        assert repositorio.listar_lancamentos(conta_id) == []
        assert barramento.publicados == []

    def test_regra_da_cadeia_recusa(self, registrar, conta_id, hoje) -> None:
        with pytest.raises(RegraViolada):
            registrar.executar(conta_id, "x", 10.0, hoje + timedelta(days=3), "G", "debito")

    def test_limite_diario_considera_o_que_ja_foi_gasto(
        self, registrar, repositorio, conta_id, hoje
    ) -> None:
        repositorio.salvar(Conta("Rica", 50_000.0, id=conta_id))
        registrar_debito(registrar, conta_id, hoje, 4_000.0)

        with pytest.raises(RegraViolada, match="diário"):
            registrar_debito(registrar, conta_id, hoje, 1_500.0)

    def test_publica_um_evento_com_identificadores(
        self, registrar, barramento, conta_id, hoje
    ) -> None:
        registrar_debito(registrar, conta_id, hoje, 100.0)

        (evento,) = barramento.publicados
        assert isinstance(evento, LancamentoRegistrado)
        assert evento.conta_id == conta_id
        assert evento.tipo == "debito"
        assert evento.valor == 100.0
        assert evento.saldo_apos == 900.0
        assert isinstance(evento.lancamento_id, str)


class TestAplicarAjuste:
    def test_aplica_estrategia_e_publica_evento(
        self, repositorio, barramento, conta_id
    ) -> None:
        caso = AplicarAjuste(repositorio, barramento)

        conta = caso.executar(conta_id, "rendimento", "percentual", 10.0)

        assert conta["saldo"] == 1100.0
        assert repositorio.obter(conta_id).saldo == 1100.0
        (evento,) = barramento.publicados
        assert isinstance(evento, SaldoAjustado)
        assert evento.ajuste == "rendimento"
        assert evento.valor_aplicado == 100.0

    def test_conta_sem_saldo_nao_rende(self, repositorio, barramento) -> None:
        vazia = CriarConta(repositorio).executar("Vazia")

        with pytest.raises(ValueError):
            AplicarAjuste(repositorio, barramento).executar(
                vazia["id"], "rendimento", "fixo", 1.0
            )

        assert barramento.publicados == []

    def test_expoe_as_opcoes_para_a_interface(self, repositorio, barramento) -> None:
        assert len(AplicarAjuste(repositorio, barramento).opcoes()) == 6


class TestExtrato:
    def test_totais_e_lancamentos(self, registrar, repositorio, conta_id, hoje) -> None:
        registrar_debito(registrar, conta_id, hoje, 100.0, "Mercado")
        registrar.executar(conta_id, "Salário", 500.0, hoje, "Renda", "credito")

        extrato = GerarExtrato(repositorio).executar(conta_id)

        assert extrato["total_debitos"] == 100.0
        assert extrato["total_creditos"] == 500.0
        assert [l["descricao"] for l in extrato["lancamentos"]] == ["Mercado", "Salário"]
        assert extrato["conta"]["saldo"] == 1400.0

    def test_extrato_sem_lancamentos(self, repositorio, conta_id) -> None:
        extrato = GerarExtrato(repositorio).executar(conta_id)

        assert extrato["lancamentos"] == []
        assert extrato["total_debitos"] == extrato["total_creditos"] == 0.0
