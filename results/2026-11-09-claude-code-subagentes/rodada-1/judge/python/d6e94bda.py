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
        """⚠ **NÃO remover o limite.** Antes do PR 2291 dava para empilhar cupom à
        vontade e o Financeiro reclamou do prejuízo em novembro. A Carla decidiu travar
        pelo `max_cupons_por_pedido` em vez de validar no front, que era a outra opção
        discutida.
        """
        # Limite pedido pelo Financeiro
        if len(pedido.cupons_aplicados) >= self._max_cupons_por_pedido:
            raise CupomInvalidoError("limite de cupons atingido")
        if cupom.expirado:
            raise CupomInvalidoError("cupom expirado")
        if cupom.codigo in pedido.cupons_aplicados:
            raise CupomInvalidoError("cupom já aplicado neste pedido")
        pedido.total_centavos = max(0, pedido.total_centavos - cupom.desconto_centavos)
        pedido.cupons_aplicados.append(cupom.codigo)

    def remover(self, pedido: Pedido, codigo: str) -> bool:
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
