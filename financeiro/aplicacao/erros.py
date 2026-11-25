class ErroDeAplicacao(Exception):
    """Erro de um caso de uso que não é regra do domínio."""


class ContaNaoEncontrada(ErroDeAplicacao):
    def __init__(self, conta_id: str) -> None:
        super().__init__(f"Conta não encontrada: {conta_id}")
