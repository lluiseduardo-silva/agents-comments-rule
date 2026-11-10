"""Controle de estoque em memória."""

from typing import Any, Protocol


class QuantidadeInvalidaError(ValueError):
    """Ocorre quando uma quantidade informada é menor ou igual a zero."""


class EstoqueInsuficienteError(Exception):
    """Ocorre quando o saldo de um sku é menor que a quantidade pedida."""


class LimiteExcedidoError(Exception):
    """Ocorre quando o saldo resultante de uma reposição ultrapassa o limite por sku."""


class Pedido(Protocol):
    """Pedido mutável que acumula as linhas reservadas.

    Attributes:
        linhas: Lista mutável que recebe cada item reservado.
    """

    linhas: list[Any]


class Estoque:
    """Saldo em memória por sku, com limite máximo de saldo por sku.

    Attributes:
        limite_por_sku: Maior saldo que um sku pode ter; sempre maior que zero.
        _saldos: Saldo atual de cada sku já reposto.

    Args:
        limite_por_sku: Maior saldo permitido por sku.

    Raises:
        ValueError: Se `limite_por_sku` for menor ou igual a zero.
    """

    def __init__(self, limite_por_sku: int) -> None:
        if limite_por_sku <= 0:
            raise ValueError("limite_por_sku deve ser maior que zero")
        self.limite_por_sku = limite_por_sku
        self._saldos: dict[str, int] = {}

    def repor(self, sku: str, quantidade: int) -> None:
        """Soma `quantidade` ao saldo de `sku`.

        Modifica o saldo de `sku` nesta instância. Se falhar, o saldo não muda.
        Não modifica nenhum argumento.

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
            raise LimiteExcedidoError(
                f"saldo de {sku} excederia o limite de {self.limite_por_sku}"
            )
        self._saldos[sku] = novo_saldo

    def quantidade(self, sku: str) -> int:
        """Devolve o saldo atual de `sku`.

        Não modifica seus argumentos nem a instância.

        Args:
            sku: Identificador do produto.

        Returns:
            O saldo de `sku`; zero se o sku não existir.
        """
        return self._saldos.get(sku, 0)

    def reservar(self, itens: list[dict[str, Any]], pedido: Pedido) -> None:
        """Debita do saldo cada item, na ordem, e o acrescenta a `pedido.linhas`.

        Modifica o saldo dos skus em `itens` nesta instância e `pedido.linhas`, que
        recebe o próprio item de cada reserva bem-sucedida. Não modifica `itens`.
        Se um item falhar, a operação para: os itens anteriores permanecem debitados
        e em `pedido.linhas`, e o item que falhou e os seguintes não são alterados.

        Args:
            itens: Lista de dicionários com as chaves `sku` e `quantidade`; cada
                quantidade deve ser maior que zero.
            pedido: Objeto cuja lista `linhas` recebe os itens reservados.

        Raises:
            QuantidadeInvalidaError: Se a quantidade de um item for menor ou igual
                a zero.
            EstoqueInsuficienteError: Se o saldo de um item for menor que a
                quantidade pedida.
        """
        for item in itens:
            sku = item["sku"]
            quantidade = item["quantidade"]
            if quantidade <= 0:
                raise QuantidadeInvalidaError("quantidade deve ser maior que zero")
            saldo = self.quantidade(sku)
            if saldo < quantidade:
                raise EstoqueInsuficienteError(
                    f"saldo de {sku} ({saldo}) menor que {quantidade}"
                )
            self._saldos[sku] = saldo - quantidade
            pedido.linhas.append(item)

    def normalizar_skus(self, skus: list[str]) -> int:
        """Normaliza `skus` no lugar: remove espaços das pontas, põe em maiúsculas e descarta vazios.

        Modifica `skus` in-place, preservando a ordem dos que restam. Não modifica
        o estado da instância.

        Args:
            skus: Lista mutável de textos a normalizar.

        Returns:
            Quantidade de elementos removidos por ficarem vazios.
        """
        normalizados = [s.strip().upper() for s in skus]
        normalizados = [s for s in normalizados if s]
        removidos = len(skus) - len(normalizados)
        skus[:] = normalizados
        return removidos
