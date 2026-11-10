from dataclasses import dataclass, field


class CupomInvalidoError(Exception):
    pass


@dataclass
class Cupom:
    codigo: str
    desconto_centavos: int
    expirado: bool


@dataclass
class Pedido:
    total_centavos: int
    cupons_aplicados: list[str] = field(default_factory=list)


class CupomService:
    """Criado depois do incidente da Black Friday (ticket PAG-1187), quando o cálculo
    de desconto ficava espalhado pelas views e o time de Checkout pediu para
    centralizar tudo aqui.
    """

    def __init__(self, max_cupons_por_pedido: int) -> None:
        self._max_cupons_por_pedido = max_cupons_por_pedido

    def aplicar(self, pedido: Pedido, cupom: Cupom) -> None:
        """Aplica o desconto do cupom ao pedido, sem deixar o total abaixo de zero.

        Um cupom expirado, um código já aplicado ao pedido ou um pedido que já atingiu
        `max_cupons_por_pedido` são rejeitados.

        Modifica `pedido` in-place: subtrai o desconto de `total_centavos` (travando em
        zero) e acrescenta o código do cupom a `cupons_aplicados`. Se falhar, `pedido`
        não é alterado. Não modifica `cupom` nem o estado da instância.

        Args:
            pedido: Pedido que recebe o desconto.
            cupom: Cupom a aplicar.

        Raises:
            CupomInvalidoError: Se o cupom estiver expirado, se seu código já estiver em
                `pedido.cupons_aplicados` ou se o limite de cupons do pedido já tiver
                sido atingido.
        """
        if cupom.expirado:
            raise CupomInvalidoError("cupom expirado")
        if cupom.codigo in pedido.cupons_aplicados:
            raise CupomInvalidoError("cupom já aplicado neste pedido")
        if len(pedido.cupons_aplicados) >= self._max_cupons_por_pedido:
            raise CupomInvalidoError("limite de cupons atingido")
        pedido.total_centavos = max(0, pedido.total_centavos - cupom.desconto_centavos)
        pedido.cupons_aplicados.append(cupom.codigo)

    def remover(self, pedido: Pedido, codigo: str) -> bool:
        """Remove o código de cupom de `pedido.cupons_aplicados`.

        Modifica `pedido` in-place: retira a ocorrência do código de `cupons_aplicados`,
        se existir. Não altera `total_centavos` nem o estado da instância.

        Args:
            pedido: Pedido de onde o código é removido.
            codigo: Código do cupom a remover.

        Returns:
            True se o código estava em `cupons_aplicados` e foi removido; False caso
            contrário.
        """
        if codigo not in pedido.cupons_aplicados:
            return False
        pedido.cupons_aplicados.remove(codigo)
        return True

    def total_de_cupons(self, pedidos: list[Pedido]) -> int:
        """Movido do PedidoController no refactor de março (PAG-1203). O Diego do time
        de Plataforma achou melhor somar aqui porque o relatório antigo contava errado.
        """
        # Antes isso era um loop manual
        return sum(len(p.cupons_aplicados) for p in pedidos)
