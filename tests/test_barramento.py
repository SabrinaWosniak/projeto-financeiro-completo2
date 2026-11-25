from dataclasses import dataclass

from financeiro.infraestrutura.barramento_memoria import BarramentoEmMemoria


@dataclass(frozen=True)
class EventoA:
    n: int


@dataclass(frozen=True)
class EventoB:
    n: int


def test_entrega_so_aos_manipuladores_do_tipo() -> None:
    barramento = BarramentoEmMemoria()
    recebidos_a, recebidos_b = [], []
    barramento.assinar(EventoA, recebidos_a.append)
    barramento.assinar(EventoB, recebidos_b.append)

    barramento.publicar(EventoA(1))

    assert recebidos_a == [EventoA(1)]
    assert recebidos_b == []


def test_varios_manipuladores_recebem_o_mesmo_evento() -> None:
    barramento = BarramentoEmMemoria()
    primeiro, segundo = [], []
    barramento.assinar(EventoA, primeiro.append)
    barramento.assinar(EventoA, segundo.append)

    barramento.publicar(EventoA(7))

    assert primeiro == segundo == [EventoA(7)]


def test_evento_sem_manipuladores_nao_da_erro() -> None:
    BarramentoEmMemoria().publicar(EventoA(1))


class TestFalhaDeReacao:
    def test_falha_de_um_manipulador_nao_impede_os_outros(self) -> None:
        barramento = BarramentoEmMemoria()
        executados = []

        def quebrado(evento):
            raise RuntimeError("deu ruim")

        barramento.assinar(EventoA, executados.append)
        barramento.assinar(EventoA, quebrado)
        barramento.assinar(EventoA, lambda e: executados.append("depois"))

        barramento.publicar(EventoA(1))  # não levanta

        assert executados == [EventoA(1), "depois"]

    def test_falha_fica_registrada(self) -> None:
        barramento = BarramentoEmMemoria()

        def quebrado(evento):
            raise RuntimeError("deu ruim")

        barramento.assinar(EventoA, quebrado)
        barramento.publicar(EventoA(1))

        ((evento, erro),) = barramento.falhas
        assert evento == EventoA(1)
        assert str(erro) == "deu ruim"

    def test_falha_e_comunicada_a_quem_usa(self) -> None:
        avisos = []
        barramento = BarramentoEmMemoria(ao_falhar=avisos.append)

        def quebrado(evento):
            raise RuntimeError("deu ruim")

        barramento.assinar(EventoA, quebrado)
        barramento.publicar(EventoA(1))

        assert len(avisos) == 1
        assert "deu ruim" in avisos[0]
