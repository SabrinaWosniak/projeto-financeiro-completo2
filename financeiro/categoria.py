class Categoria:

    def __init__(self, nome: str) -> None:
        if not nome:
            raise ValueError("Nome da categoria é obrigatório")

        self._nome = nome

    @property
    def nome(self) -> str:
        return self._nome

    # recebe o nome da categoria quando é criada e verifica se esse nome foi informado. Se estiver vazio, o sistema gera um erro. Caso esteja correto, o nome é armazenado no objeto.