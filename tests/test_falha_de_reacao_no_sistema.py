"""Teste ponta a ponta: uma reação quebra e o lançamento continua valendo."""
from financeiro.aplicacao.casos_de_uso import CriarConta, RegistrarLancamento
from financeiro.aplicacao.manipuladores import NotificarLancamento
from financeiro.dominio.eventos import LancamentoRegistrado
from financeiro.infraestrutura.barramento_memoria import BarramentoEmMemoria
from financeiro.infraestrutura.repositorio_memoria import RepositorioContasEmMemoria
from tests.conftest import NotificadorFalso, cadeia_padrao


class NotificadorQuebrado(NotificadorFalso):
    def avisar(self, mensagem: str) -> None:
        raise ConnectionError("servidor de avisos fora do ar")


def test_reacao_que_falha_nao_desfaz_o_lancamento(hoje) -> None:
    repositorio = RepositorioContasEmMemoria()
    avisos_do_sistema = NotificadorFalso()
    barramento = BarramentoEmMemoria(ao_falhar=avisos_do_sistema.avisar)

    # a 1ª reação quebra, a 2ª está saudável
    barramento.assinar(LancamentoRegistrado, NotificarLancamento(NotificadorQuebrado()))
    saudavel = NotificadorFalso()
    barramento.assinar(LancamentoRegistrado, NotificarLancamento(saudavel))

    conta = CriarConta(repositorio).executar("Corrente", 1000.0)
    registrar = RegistrarLancamento(repositorio, barramento, cadeia_padrao())

    resultado = registrar.executar(conta["id"], "Mercado", 100.0, hoje, "Geral", "debito")

    # 1. o caso de uso terminou normalmente e o dado está gravado
    assert resultado["saldo"] == 900.0
    assert repositorio.obter(conta["id"]).saldo == 900.0
    assert len(repositorio.listar_lancamentos(conta["id"])) == 1
    # 2. a reação saudável rodou mesmo assim
    assert len(saudavel.mensagens) == 1
    # 3. a falha ficou visível (registrada e avisada)
    assert len(barramento.falhas) == 1
    assert "servidor de avisos fora do ar" in avisos_do_sistema.mensagens[0]
