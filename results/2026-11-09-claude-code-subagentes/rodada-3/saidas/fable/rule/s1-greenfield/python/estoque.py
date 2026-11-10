"""Controle de estoque em memória."""

from dataclasses import dataclass, field


class EstoqueError(Exception):
    """Base de todos os erros levantados por este módulo."""


class LimiteInvalidoError(EstoqueError):
    """Ocorre ao criar um `Estoque` com limite por SKU menor ou igual a zero."""


class QuantidadeInvalidaError(EstoqueError):
    """Ocorre quando a quantidade a repor ou a reservar é menor ou igual a zero."""


class LimiteExcedidoError(EstoqueError):
    """Ocorre quando uma reposição deixaria o saldo do SKU acima do limite por SKU."""


class EstoqueInsuficienteError(EstoqueError):
    """Ocorre quando a quantidade a reservar de um SKU é maior que o saldo dele."""


@dataclass(frozen=True)
class Item:
    """Quantidade de um SKU a reservar; imutável depois de criado.

    Attributes:
        sku: Identificador do produto. A comparação entre SKUs é exata:
            diferencia maiúsculas de minúsculas e considera espaços.
        quantidade: Unidades do SKU. O valor não é validado na criação do
            item; a validação acontece em `Estoque.reservar`.
    """

    sku: str
    quantidade: int


@dataclass
class Pedido:
    """Pedido que acumula os itens reservados para ele.

    Attributes:
        linhas: Itens reservados, na ordem em que foram reservados. Vazia
            quando não informada na criação; quando informada, a própria
            lista recebida é usada, sem cópia.
    """

    linhas: list[Item] = field(default_factory=list)


class Estoque:
    """Estoque em memória: um saldo inteiro por SKU, com o mesmo teto para todos.

    O saldo de cada SKU fica sempre entre zero e o limite por SKU informado na
    criação. Um SKU que nunca foi reposto tem saldo zero. Os SKUs são
    comparados de forma exata, sem normalização. Os saldos existem só na
    instância: nada é persistido, e não há sincronização entre threads.
    """

    def __init__(self, limite_por_sku: int) -> None:
        """Cria um estoque vazio.

        Args:
            limite_por_sku: Saldo máximo, em unidades, que cada SKU pode
                atingir. Deve ser maior que zero.

        Raises:
            LimiteInvalidoError: Se `limite_por_sku` for menor ou igual a zero.
        """
        if limite_por_sku <= 0:
            raise LimiteInvalidoError(
                f"limite por SKU deve ser maior que zero: {limite_por_sku}"
            )
        self._limite_por_sku = limite_por_sku
        self._saldos: dict[str, int] = {}

    def repor(self, sku: str, quantidade: int) -> None:
        """Soma `quantidade` ao saldo de `sku`.

        Modifica apenas o saldo de `sku` neste estoque. Quando levanta
        exceção, o saldo fica como estava.

        Args:
            sku: SKU a repor. Não precisa ter saldo anterior.
            quantidade: Unidades a somar. Deve ser maior que zero.

        Raises:
            QuantidadeInvalidaError: Se `quantidade` for menor ou igual a zero.
            LimiteExcedidoError: Se o saldo resultante ficar acima do limite
                por SKU deste estoque.
        """
        if quantidade <= 0:
            raise QuantidadeInvalidaError(
                f"quantidade a repor de {sku!r} deve ser maior que zero: {quantidade}"
            )
        novo_saldo = self._saldos.get(sku, 0) + quantidade
        if novo_saldo > self._limite_por_sku:
            raise LimiteExcedidoError(
                f"saldo de {sku!r} iria a {novo_saldo}, "
                f"acima do limite de {self._limite_por_sku}"
            )
        self._saldos[sku] = novo_saldo

    def quantidade(self, sku: str) -> int:
        """Devolve o saldo atual de `sku`.

        Não modifica o estoque nem o argumento; consultar um SKU sem saldo
        não o registra.

        Args:
            sku: SKU a consultar.

        Returns:
            Saldo do SKU em unidades; zero se o SKU não tiver saldo neste
            estoque, inclusive quando nunca foi reposto.
        """
        return self._saldos.get(sku, 0)

    def reservar(self, itens: list[Item], pedido: Pedido) -> None:
        """Debita do estoque cada item de `itens` e o acrescenta a `pedido`.

        Processa os itens na ordem da lista. Para cada um, debita
        `item.quantidade` do saldo de `item.sku` neste estoque e acrescenta o
        próprio objeto ao fim de `pedido.linhas`. Não modifica `itens`.

        A operação não é atômica: ao levantar exceção, para no item que
        falhou. Os itens anteriores a ele continuam debitados e continuam em
        `pedido.linhas`; o item que falhou e os seguintes não alteram o
        estoque nem o pedido.

        Args:
            itens: Itens a reservar, na ordem de processamento. Lista vazia é
                aceita e não altera nada. O mesmo SKU pode aparecer em mais de
                um item; cada ocorrência é debitada separadamente.
            pedido: Pedido que recebe os itens reservados em `linhas`.

        Raises:
            QuantidadeInvalidaError: Se a quantidade de um item for menor ou
                igual a zero.
            EstoqueInsuficienteError: Se a quantidade de um item for maior que
                o saldo do SKU no momento em que o item é processado.
        """
        for item in itens:
            if item.quantidade <= 0:
                raise QuantidadeInvalidaError(
                    f"quantidade a reservar de {item.sku!r} deve ser maior "
                    f"que zero: {item.quantidade}"
                )
            saldo = self._saldos.get(item.sku, 0)
            if item.quantidade > saldo:
                raise EstoqueInsuficienteError(
                    f"saldo de {item.sku!r} é {saldo}, "
                    f"insuficiente para reservar {item.quantidade}"
                )
            self._saldos[item.sku] = saldo - item.quantidade
            pedido.linhas.append(item)

    @staticmethod
    def normalizar_skus(skus: list[str]) -> int:
        """Normaliza os textos de `skus` e remove os que ficarem vazios.

        Modifica `skus` no lugar: cada texto perde os espaços em branco das
        pontas (os caracteres que `str.strip` remove) e é convertido para
        maiúsculas, e os que resultarem vazios são removidos da lista. A ordem
        dos textos restantes é mantida e duplicatas não são removidas. Não lê
        nem modifica o saldo de nenhum estoque: o método não depende de
        instância.

        Args:
            skus: Lista mutável de textos a normalizar. Lista vazia é aceita.

        Returns:
            Quantidade de textos removidos da lista; zero se nenhum ficou
            vazio.
        """
        tamanho_original = len(skus)
        normalizados = (texto.strip().upper() for texto in skus)
        skus[:] = [sku for sku in normalizados if sku]
        return tamanho_original - len(skus)
