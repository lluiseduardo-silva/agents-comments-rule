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
   * Aplica `cupom` a `pedido`: subtrai o desconto do total, que nunca fica abaixo de
   * zero, e registra o código do cupom no pedido.
   *
   * Modifica `pedido`: `totalCentavos` é reduzido em `cupom.descontoCentavos`, limitado
   * a zero, e `cupom.codigo` é acrescentado ao fim de `cuponsAplicados`. Não modifica
   * `cupom` nem a instância. Quando lança erro, `pedido` permanece inalterado.
   *
   * @param pedido - Pedido que recebe o desconto.
   * @param cupom - Cupom a aplicar. `descontoCentavos` é o desconto em centavos e não
   *   é validado: um valor negativo aumenta o total.
   * @throws {CupomInvalidoError} Se `cupom.expirado` for verdadeiro.
   * @throws {CupomInvalidoError} Se `cupom.codigo` já estiver em
   *   `pedido.cuponsAplicados`.
   * @throws {CupomInvalidoError} Se `pedido.cuponsAplicados` já tiver
   *   `maxCuponsPorPedido` códigos ou mais.
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
   * Remove `codigo` dos cupons aplicados a `pedido` e informa se ele estava lá.
   *
   * Modifica `pedido`: retira de `cuponsAplicados` a primeira ocorrência de `codigo`,
   * preservando a ordem dos demais códigos. Não altera `pedido.totalCentavos` (o
   * desconto do cupom removido não é devolvido ao total) nem a instância.
   *
   * @param pedido - Pedido de cuja lista de cupons o código é retirado.
   * @param codigo - Código do cupom a remover; a comparação é exata.
   * @returns `true` se o código estava em `cuponsAplicados` e foi retirado; `false`
   *   se não estava, caso em que `pedido` permanece inalterado.
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
