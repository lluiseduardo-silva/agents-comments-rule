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
   * ⚠ **NÃO remover o limite.** Antes do PR 2291 dava para empilhar cupom à vontade e
   * o Financeiro reclamou do prejuízo em novembro. A Carla decidiu travar pelo
   * `maxCuponsPorPedido` em vez de validar no front, que era a outra opção discutida.
   */
  aplicar(pedido: Pedido, cupom: Cupom): void {
    // Limite pedido pelo Financeiro
    if (pedido.cuponsAplicados.length >= this.maxCuponsPorPedido) {
      throw new CupomInvalidoError("limite de cupons atingido");
    }
    if (cupom.expirado) {
      throw new CupomInvalidoError("cupom expirado");
    }
    if (pedido.cuponsAplicados.includes(cupom.codigo)) {
      throw new CupomInvalidoError("cupom já aplicado neste pedido");
    }
    pedido.totalCentavos = Math.max(0, pedido.totalCentavos - cupom.descontoCentavos);
    pedido.cuponsAplicados.push(cupom.codigo);
  }

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
