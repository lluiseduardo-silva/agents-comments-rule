"""Controle de estoque em memória, com saldo por SKU e limite máximo por SKU."""

from typing import List, Mapping, Protocol


class QuantidadeInvalidaError(ValueError):
    """Lançada quando uma quantidade informada é menor ou igual a zero."""


class LimiteExcedidoError(ValueError):
    """Lançada quando uma reposição deixaria o saldo de um SKU acima do limite."""


class EstoqueInsuficienteError(Exception):
    """Lançada quando o saldo de um SKU é menor que a quantidade a debitar."""


class Pedido(Protocol):
    """Qualquer objeto que exponha uma lista mutável de linhas de pedido.

    Attributes:
        linhas: Lista onde cada item reservado é acrescentado, no formato
            ``{"sku": str, "quantidade": int}``.
    """

    linhas: List[Mapping[str, object]]


class Estoque:
    """Saldo em memória por SKU, com teto de unidades por SKU.

    Um SKU que nunca recebeu reposição tem saldo zero.

    Attributes:
        limite_por_sku: Saldo máximo permitido para cada SKU.

    Args:
        limite_por_sku: Saldo máximo por SKU; deve ser maior que zero.

    Raises:
        ValueError: Se ``limite_por_sku`` for menor ou igual a zero.
    """

    def __init__(self, limite_por_sku: int) -> None:
        if limite_por_sku <= 0:
            raise ValueError("limite_por_sku deve ser maior que zero")
        self.limite_por_sku = limite_por_sku
        self._saldos: dict[str, int] = {}

    def repor(self, sku: str, quantidade: int) -> None:
        """Soma ``quantidade`` ao saldo de ``sku``.

        Altera o saldo de ``sku`` na instância. Em caso de erro, o saldo não muda.

        Args:
            sku: Identificador do item; um SKU sem saldo começa em zero.
            quantidade: Unidades a somar; deve ser maior que zero.

        Raises:
            QuantidadeInvalidaError: Se ``quantidade`` for menor ou igual a zero.
            LimiteExcedidoError: Se o saldo resultante ultrapassar
                ``limite_por_sku``.
        """
        if quantidade <= 0:
            raise QuantidadeInvalidaError(
                f"quantidade inválida para {sku!r}: {quantidade}"
            )
        novo_saldo = self.quantidade(sku) + quantidade
        if novo_saldo > self.limite_por_sku:
            raise LimiteExcedidoError(
                f"saldo de {sku!r} ficaria {novo_saldo}, "
                f"acima do limite {self.limite_por_sku}"
            )
        self._saldos[sku] = novo_saldo

    def quantidade(self, sku: str) -> int:
        """Informa o saldo atual de ``sku``.

        Não modifica a instância.

        Args:
            sku: Identificador do item.

        Returns:
            O saldo atual; zero se o SKU nunca recebeu reposição.
        """
        return self._saldos.get(sku, 0)

    def reservar(self, itens: List[Mapping[str, object]], pedido: Pedido) -> None:
        """Debita cada item do estoque e o registra no pedido, na ordem recebida.

        Para cada item, debita a quantidade do saldo do SKU na instância e
        acrescenta o próprio item ao fim de ``pedido.linhas``. A operação para no
        primeiro erro: os itens anteriores permanecem debitados e em
        ``pedido.linhas``; o item com erro e os seguintes não alteram nada. Não
        modifica ``itens``.

        Args:
            itens: Itens no formato ``{"sku": str, "quantidade": int}``. Uma lista
                vazia não altera nada.
            pedido: Pedido cuja lista ``linhas`` recebe os itens reservados.

        Raises:
            QuantidadeInvalidaError: Se a quantidade de um item for menor ou igual
                a zero.
            EstoqueInsuficienteError: Se o saldo do SKU de um item for menor que a
                quantidade pedida.
            KeyError: Se um item não tiver a chave ``"sku"`` ou ``"quantidade"``.
        """
        for item in itens:
            sku = item["sku"]
            quantidade = item["quantidade"]
            if quantidade <= 0:
                raise QuantidadeInvalidaError(
                    f"quantidade inválida para {sku!r}: {quantidade}"
                )
            saldo = self.quantidade(sku)
            if saldo < quantidade:
                raise EstoqueInsuficienteError(
                    f"saldo de {sku!r} é {saldo}, pedido {quantidade}"
                )
            self._saldos[sku] = saldo - quantidade
            pedido.linhas.append(item)


def normalizar_skus(skus: List[str]) -> int:
    """Padroniza uma lista de SKUs e descarta os vazios.

    Modifica ``skus`` no lugar: cada texto perde os espaços das pontas e passa a
    maiúsculas, e os que ficam vazios são removidos, mantendo a ordem dos demais.

    Args:
        skus: Lista de textos a normalizar.

    Returns:
        Quantos elementos foram removidos por ficarem vazios.
    """
    normalizados = [s.strip().upper() for s in skus]
    restantes = [s for s in normalizados if s]
    removidos = len(normalizados) - len(restantes)
    skus[:] = restantes
    return removidos
