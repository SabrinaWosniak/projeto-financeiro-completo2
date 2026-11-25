from financeiro.aplicacao.portas import Notificador


class NotificadorTerminal(Notificador):
    def avisar(self, mensagem: str) -> None:
        print(f"  [aviso] {mensagem}")
