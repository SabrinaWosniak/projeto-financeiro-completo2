"""Interface de terminal. Só conversa com os casos de uso."""
from datetime import date, datetime
from typing import Callable

from financeiro.aplicacao.casos_de_uso import CasosDeUso
from financeiro.aplicacao.erros import ErroDeAplicacao


def reais(valor: float) -> str:
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


class MenuTerminal:
    def __init__(
        self,
        casos: CasosDeUso,
        entrada: Callable[[str], str] = input,
        saida: Callable[[str], None] = print,
    ) -> None:
        self._casos = casos
        self._entrada = entrada
        self._saida = saida
        self._acoes = {
            "1": self._criar_conta,
            "2": self._listar_contas,
            "3": self._registrar_lancamento,
            "4": self._aplicar_ajuste,
            "5": self._ver_extrato,
            "6": self._encerrar_conta,
        }

    # ---------- laço principal ----------
    def executar(self) -> None:
        while True:
            self._mostrar_menu()

            try:
                opcao = self._entrada("Escolha uma opção: ").strip()
            except EOFError:
                return

            if opcao == "0":
                self._saida("Até logo!")
                return

            acao = self._acoes.get(opcao)

            if acao is None:
                self._saida("Opção inválida.")
                continue

            try:
                acao()
            except (ValueError, ErroDeAplicacao) as erro:
                # erros do domínio/aplicação viram mensagem para o usuário
                self._saida(f"Erro: {erro}")
            except EOFError:
                return

    def _mostrar_menu(self) -> None:
        self._saida("")
        self._saida("===== Controle Financeiro =====")
        self._saida("1. Criar conta")
        self._saida("2. Listar contas")
        self._saida("3. Registrar lançamento")
        self._saida("4. Aplicar rendimento / juros / correção")
        self._saida("5. Ver extrato")
        self._saida("6. Encerrar conta")
        self._saida("0. Sair")

    # ---------- leitura de dados ----------
    @staticmethod
    def _converter_numero(texto: str) -> float:
        try:
            return float(texto.strip().replace(",", "."))
        except ValueError:
            raise ValueError("Número inválido") from None

    def _ler_numero(self, pergunta: str) -> float:
        return self._converter_numero(self._entrada(pergunta))

    def _ler_data(self) -> date:
        texto = self._entrada("Data (dd/mm/aaaa, Enter = hoje): ").strip()

        if not texto:
            return date.today()

        try:
            return datetime.strptime(texto, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Data inválida (use dd/mm/aaaa)") from None

    def _escolher(self, pergunta: str, quantidade: int) -> int:
        texto = self._entrada(pergunta).strip()

        if not texto.isdigit() or not 1 <= int(texto) <= quantidade:
            raise ValueError("Escolha inválida")

        return int(texto) - 1

    def _escolher_conta(self) -> str:
        contas = self._casos.listar_contas.executar()

        if not contas:
            raise ValueError("Nenhuma conta cadastrada")

        self._imprimir_contas(contas)
        return contas[self._escolher("Número da conta: ", len(contas))]["id"]

    def _imprimir_contas(self, contas: list[dict]) -> None:
        for numero, conta in enumerate(contas, start=1):
            situacao = "" if conta["ativa"] else " (encerrada)"
            self._saida(
                f"  {numero}. {conta['nome']} - {reais(conta['saldo'])}{situacao}"
            )

    # ---------- ações ----------
    def _criar_conta(self) -> None:
        nome = self._entrada("Nome da conta: ").strip()
        texto = self._entrada("Saldo inicial (Enter = 0): ").strip()
        saldo = self._converter_numero(texto) if texto else 0.0
        conta = self._casos.criar_conta.executar(nome, saldo)
        self._saida(f"Conta '{conta['nome']}' criada com {reais(conta['saldo'])}.")

    def _listar_contas(self) -> None:
        contas = self._casos.listar_contas.executar()

        if not contas:
            self._saida("Nenhuma conta cadastrada.")
            return

        self._imprimir_contas(contas)

    def _registrar_lancamento(self) -> None:
        conta_id = self._escolher_conta()
        tipo = ["debito", "credito"][
            self._escolher("Tipo (1 = débito, 2 = crédito): ", 2)
        ]
        descricao = self._entrada("Descrição: ").strip()
        valor = self._ler_numero("Valor: ")
        categoria = self._entrada("Categoria: ").strip()
        data = self._ler_data()

        self._casos.registrar_lancamento.executar(
            conta_id, descricao, valor, data, categoria, tipo
        )

    def _aplicar_ajuste(self) -> None:
        conta_id = self._escolher_conta()
        opcoes = self._casos.aplicar_ajuste.opcoes()

        self._saida("Qual ajuste aplicar?")
        for numero, o in enumerate(opcoes, start=1):
            self._saida(f"  {numero}. {o['familia']} {o['modalidade']} ({o['unidade']})")

        escolhida = opcoes[self._escolher("Opção: ", len(opcoes))]
        valor = self._ler_numero(f"Valor em {escolhida['unidade']}: ")

        self._casos.aplicar_ajuste.executar(
            conta_id, escolhida["familia"], escolhida["modalidade"], valor
        )

    def _ver_extrato(self) -> None:
        extrato = self._casos.gerar_extrato.executar(self._escolher_conta())
        conta = extrato["conta"]

        self._saida(f"--- Extrato: {conta['nome']} ---")

        if not extrato["lancamentos"]:
            self._saida("  (sem lançamentos)")

        for l in extrato["lancamentos"]:
            sinal = "-" if l["tipo"] == "debito" else "+"
            self._saida(
                f"  {l['data']:%d/%m/%Y}  {l['descricao']:<20} "
                f"{l['categoria']:<12} {sinal} {reais(l['valor'])}"
            )

        self._saida(f"Total de créditos: {reais(extrato['total_creditos'])}")
        self._saida(f"Total de débitos:  {reais(extrato['total_debitos'])}")
        self._saida(f"Saldo atual:       {reais(conta['saldo'])}")

    def _encerrar_conta(self) -> None:
        conta = self._casos.encerrar_conta.executar(self._escolher_conta())
        self._saida(f"Conta '{conta['nome']}' encerrada.")
