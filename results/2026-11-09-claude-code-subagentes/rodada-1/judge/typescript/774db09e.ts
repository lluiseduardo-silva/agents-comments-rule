export class QuantidadeInvalidaError extends Error {
  constructor(readonly quantidade: number) {
    super(`Quantidade invalida: ${quantidade}`);
    this.name = "QuantidadeInvalidaError";
  }
}

export class LimiteInvalidoError extends Error {
  constructor(readonly limitePorSku: number) {
    super(`limitePorSku deve ser um inteiro maior que zero: ${limitePorSku}`);
    this.name = "LimiteInvalidoError";
  }
}

export class LimiteExcedidoError extends Error {
  constructor(
    readonly sku: string,
    readonly saldoResultante: number,
    readonly limitePorSku: number,
  ) {
    super(`Saldo de ${sku} (${saldoResultante}) excede o limite de ${limitePorSku}`);
    this.name = "LimiteExcedidoError";
  }
}

export class EstoqueInsuficienteError extends Error {
  constructor(
    readonly sku: string,
    readonly solicitado: number,
    readonly disponivel: number,
  ) {
    super(`Estoque insuficiente para ${sku}: solicitado ${solicitado}, disponivel ${disponivel}`);
    this.name = "EstoqueInsuficienteError";
  }
}

export interface ItemReserva {
  sku: string;
  quantidade: number;
}

export interface Pedido {
  linhas: ItemReserva[];
}

function quantidadeValida(quantidade: number): boolean {
  // `!(x > 0)` tambem rejeita NaN.
  return quantidade > 0;
}

export class Estoque {
  private readonly saldos = new Map<string, number>();

  constructor(readonly limitePorSku: number) {
    if (!Number.isInteger(limitePorSku) || limitePorSku <= 0) {
      throw new LimiteInvalidoError(limitePorSku);
    }
  }

  repor(sku: string, quantidade: number): void {
    if (!quantidadeValida(quantidade)) {
      throw new QuantidadeInvalidaError(quantidade);
    }
    const saldoResultante = this.quantidade(sku) + quantidade;
    if (saldoResultante > this.limitePorSku) {
      throw new LimiteExcedidoError(sku, saldoResultante, this.limitePorSku);
    }
    this.saldos.set(sku, saldoResultante);
  }

  quantidade(sku: string): number {
    return this.saldos.get(sku) ?? 0;
  }

  /**
   * Reserva os itens na ordem. No primeiro erro a operacao para; itens
   * anteriores continuam debitados e presentes em `pedido.linhas`.
   */
  reservar(itens: readonly ItemReserva[], pedido: Pedido): void {
    for (const item of itens) {
      if (!quantidadeValida(item.quantidade)) {
        throw new QuantidadeInvalidaError(item.quantidade);
      }
      const disponivel = this.quantidade(item.sku);
      if (disponivel < item.quantidade) {
        throw new EstoqueInsuficienteError(item.sku, item.quantidade, disponivel);
      }
      this.saldos.set(item.sku, disponivel - item.quantidade);
      pedido.linhas.push(item);
    }
  }
}

/** Altera a lista no lugar e devolve quantos textos foram removidos. */
export function normalizarSkus(skus: string[]): number {
  let escrita = 0;
  for (const sku of skus) {
    const normalizado = sku.trim().toUpperCase();
    if (normalizado !== "") {
      skus[escrita++] = normalizado;
    }
  }
  const removidos = skus.length - escrita;
  skus.length = escrita;
  return removidos;
}
