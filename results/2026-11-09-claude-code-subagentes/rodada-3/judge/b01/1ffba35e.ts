export class CupomInvalidoError extends Error {}

export interface Cupom {
  codigo: string;
  descontoCentavos: number;
  expirado: boolean;
}

export class Pedido {
  readonly cuponsAplicados: string[] = [];

  constructor(public totalCentavos: number) {}
}

/**
 * Criado depois do incidente da Black Friday (ticket PAG-1187), quando o cálculo de
 * desconto ficava espalhado pelos controllers e o time de Checkout pediu para
 * centralizar tudo aqui.
 */
export class CupomService {
  constructor(private readonly maxCuponsPorPedido: number) {}

  /**
   * Aplica o desconto do cupom ao pedido; o total nunca fica abaixo de zero.
   *
   * Modifica [pedido] in-place: subtrai o desconto de `totalCentavos` (travando em zero)
   * e acrescenta o código a `cuponsAplicados`. Se falhar, o pedido não é alterado. Não
   * modifica [cupom] nem o estado da instância.
   *
   * @param pedido Pedido que recebe o desconto.
   * @param cupom Cupom a aplicar.
   * @throws CupomInvalidoError Se o cupom estiver expirado, se o mesmo código já constar
   * em `cuponsAplicados` ou se `cuponsAplicados` já tiver `maxCuponsPorPedido` itens.
   */
  aplicar(pedido: Pedido, cupom: Cupom): void {
    if (cupom.expirado) {
      throw new CupomInvalidoError("cupom expirado");
    }
    if (pedido.cuponsAplicados.includes(cupom.codigo)) {
      throw new CupomInvalidoError("cupom já aplicado neste pedido");
    }
    if (pedido.cuponsAplicados.length >= this.maxCuponsPorPedido) {
      throw new CupomInvalidoError("limite de cupons atingido");
    }
    pedido.totalCentavos = Math.max(0, pedido.totalCentavos - cupom.descontoCentavos);
    pedido.cuponsAplicados.push(cupom.codigo);
  }

  /**
   * Remove o código de cupom da lista de cupons aplicados do pedido.
   *
   * Modifica [pedido] in-place: retira o código de `cuponsAplicados`; `totalCentavos` não
   * é alterado. Não modifica o estado da instância.
   *
   * @param pedido Pedido de onde o código é removido.
   * @param codigo Código do cupom a remover.
   * @returns `true` se o código estava em `cuponsAplicados` e foi removido; `false` caso
   * contrário.
   */
  remover(pedido: Pedido, codigo: string): boolean {
    const indice = pedido.cuponsAplicados.indexOf(codigo);
    if (indice === -1) {
      return false;
    }
    pedido.cuponsAplicados.splice(indice, 1);
    return true;
  }

  /**
   * Movido do PedidoController no refactor de março (PAG-1203). O Diego do time de
   * Plataforma achou melhor somar aqui porque o relatório antigo contava errado.
   */
  totalDeCupons(pedidos: readonly Pedido[]): number {
    // Antes isso era um loop manual
    return pedidos.reduce((soma, p) => soma + p.cuponsAplicados.length, 0);
  }
}
