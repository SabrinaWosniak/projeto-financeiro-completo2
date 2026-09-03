import pytest

from financeiro.categoria import Categoria


class TestCategoria:
    def test_criar_categoria(self) -> None:
        categoria = Categoria("Alimentação")

        assert categoria.nome == "Alimentação"

    def test_categoria_sem_nome(self) -> None:
        with pytest.raises(ValueError):
            Categoria("")

#O primeiro teste verifica se uma categoria pode ser criada corretamente e se o nome é armazenado. O segundo verifica a validação, tentando criar uma categoria sem nome e confirmando que o sistema gera um ValueError.