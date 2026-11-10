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
   * Aplica o desconto de um cupom ao pedido, respeitando o limite de cupons por pedido;
   * o total resultante nunca fica abaixo de zero.
   *
   * Modifica `pedido`: subtrai `cupom.descontoCentavos` de `pedido.totalCentavos`
   * (travando em zero) e acrescenta `cupom.codigo` ao fim de `pedido.cuponsAplicados`.
   * Todas as validações ocorrem antes de qualquer alteração, então quando lança erro o
   * pedido fica intacto. Não modifica `cupom` nem o estado da instância.
   *
   * @param pedido Pedido que recebe o desconto.
   * @param cupom Cupom a aplicar; `descontoCentavos` é um valor em centavos.
   * @throws CupomInvalidoError Se o cupom estiver expirado, se um cupom com o mesmo
   *   `codigo` já estiver em `pedido.cuponsAplicados`, ou se o pedido já tiver
   *   `maxCuponsPorPedido` cupons aplicados.
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
   * Remove um código de cupom da lista de cupons aplicados ao pedido.
   *
   * Modifica `pedido.cuponsAplicados`, retirando a ocorrência de `codigo` quando
   * presente. Não altera `pedido.totalCentavos`, não modifica o estado da instância e,
   * quando o código não está na lista, não altera nada.
   *
   * @param pedido Pedido de onde o cupom é removido.
   * @param codigo Código do cupom; a comparação é exata (sensível a maiúsculas).
   * @returns `true` se o código estava aplicado e foi removido; `false` se não estava.
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
