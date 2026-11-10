"""Controle de estoque em memória."""

from typing import Any


class QuantidadeInvalidaError(ValueError):
    """Quantidade menor ou igual a zero em uma operação de estoque."""


class EstoqueInsuficienteError(ValueError):
    """O saldo do sku é menor que a quantidade pedida."""


class LimiteExcedidoError(ValueError):
    """O saldo resultante ultrapassaria o limite por sku."""


class Estoque:
    """Saldos de estoque por sku, mantidos em memória.

    Attributes:
        limite_por_sku: Saldo máximo permitido para cada sku; sempre maior que zero.
        saldos: Mapa de sku para saldo atual; skus sem movimentação não aparecem.
    """

    def __init__(self, limite_por_sku: int) -> None:
        """Cria um estoque vazio.

        Args:
            limite_por_sku: Saldo máximo permitido para cada sku; deve ser maior que zero.

        Raises:
            ValueError: Se `limite_por_sku` for menor ou igual a zero.
        """
        if limite_por_sku <= 0:
            raise ValueError("limite_por_sku deve ser maior que zero")
        self.limite_por_sku = limite_por_sku
        self.saldos: dict[str, int] = {}

    def repor(self, sku: str, quantidade: int) -> None:
        """Soma `quantidade` ao saldo do sku.

        Modifica o saldo do sku nesta instância. Se algum erro ocorrer, o saldo
        permanece inalterado.

        Args:
            sku: Identificador do produto.
            quantidade: Quantidade a somar; deve ser maior que zero.

        Raises:
            QuantidadeInvalidaError: Se `quantidade` for menor ou igual a zero.
            LimiteExcedidoError: Se o saldo resultante ultrapassar `limite_por_sku`.
        """
        if quantidade <= 0:
            raise QuantidadeInvalidaError("quantidade deve ser maior que zero")
        novo_saldo = self.quantidade(sku) + quantidade
        if novo_saldo > self.limite_por_sku:
            raise LimiteExcedidoError("saldo acima do limite por sku")
        self.saldos[sku] = novo_saldo

    def quantidade(self, sku: str) -> int:
        """Devolve o saldo atual do sku.

        Não modifica a instância nem seus argumentos.

        Args:
            sku: Identificador do produto.

        Returns:
            O saldo do sku; zero se o sku não existir.
        """
        return self.saldos.get(sku, 0)

    def reservar(self, itens: list[dict[str, Any]], pedido: Any) -> None:
        """Debita do saldo cada item, na ordem, e o acrescenta a `pedido.linhas`.

        Modifica o saldo de cada sku desta instância e a lista `pedido.linhas`, que
        recebe o próprio dicionário de cada item; `itens` não é alterada. A operação
        para no primeiro erro: os itens anteriores continuam debitados e continuam em
        `pedido.linhas`, e o item com erro não altera saldo nem linhas.

        Args:
            itens: Lista de dicionários com as chaves "sku" (texto) e "quantidade"
                (inteiro maior que zero).
            pedido: Objeto mutável cujo atributo `linhas` é uma lista.

        Raises:
            QuantidadeInvalidaError: Se a quantidade de algum item for menor ou igual
                a zero.
            EstoqueInsuficienteError: Se o saldo de algum sku for menor que a
                quantidade do item.
            KeyError: Se algum item não tiver as chaves "sku" e "quantidade".
        """
        for item in itens:
            sku = item["sku"]
            quantidade = item["quantidade"]
            if quantidade <= 0:
                raise QuantidadeInvalidaError("quantidade deve ser maior que zero")
            saldo = self.quantidade(sku)
            if saldo < quantidade:
                raise EstoqueInsuficienteError("estoque insuficiente")
            self.saldos[sku] = saldo - quantidade
            pedido.linhas.append(item)

    def normalizar_skus(self, skus: list[str]) -> int:
        """Normaliza `skus` no lugar: remove espaços das pontas, converte para
        maiúsculas e remove os textos que ficarem vazios.

        Modifica `skus` in-place, preservando a ordem dos que restam. Não modifica o
        estado da instância.

        Args:
            skus: Lista mutável de textos a normalizar.

        Returns:
            A quantidade de textos removidos por ficarem vazios.
        """
        normalizados = [s.strip().upper() for s in skus]
        restantes = [s for s in normalizados if s]
        skus[:] = restantes
        return len(normalizados) - len(restantes)
