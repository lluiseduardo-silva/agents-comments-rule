/**
 * Item de uma reserva: um sku e a quantidade desejada.
 *
 * @property sku Identificador do produto.
 * @property quantidade Quantidade do item; deve ser positiva para ser aceita por `reservar`.
 */
export interface ItemReserva {
  sku: string;
  quantidade: number;
}

/**
 * Pedido que acumula as linhas reservadas.
 *
 * @property linhas Lista mutável de itens já reservados para o pedido.
 */
export interface Pedido {
  linhas: ItemReserva[];
}

/**
 * Erro lançado quando um valor numérico informado não é válido (limite ou quantidade
 * menor ou igual a zero).
 */
export class QuantidadeInvalidaError extends Error {
  constructor(mensagem: string) {
    super(mensagem);
    this.name = "QuantidadeInvalidaError";
  }
}

/**
 * Erro lançado quando o saldo de um sku não cobre a quantidade debitada.
 */
export class EstoqueInsuficienteError extends Error {
  constructor(mensagem: string) {
    super(mensagem);
    this.name = "EstoqueInsuficienteError";
  }
}

/**
 * Erro lançado quando uma reposição levaria o saldo de um sku acima do limite por sku.
 */
export class LimiteExcedidoError extends Error {
  constructor(mensagem: string) {
    super(mensagem);
    this.name = "LimiteExcedidoError";
  }
}

/**
 * Controle de estoque em memória, com saldo por sku e um limite de saldo igual para
 * todos os skus.
 *
 * O estado vive apenas na instância; nada é persistido.
 */
export class Estoque {
  private readonly saldos = new Map<string, number>();
  private readonly limitePorSku: number;

  /**
   * Cria um estoque vazio.
   *
   * Não modifica nenhum estado externo.
   *
   * @param limitePorSku Saldo máximo permitido por sku; inteiro maior que zero.
   * @throws QuantidadeInvalidaError Se `limitePorSku` não for inteiro ou for menor ou
   * igual a zero.
   */
  constructor(limitePorSku: number) {
    if (!Number.isInteger(limitePorSku) || limitePorSku <= 0) {
      throw new QuantidadeInvalidaError(
        `limitePorSku deve ser um inteiro maior que zero: ${limitePorSku}`,
      );
    }
    this.limitePorSku = limitePorSku;
  }

  /**
   * Soma `quantidade` ao saldo de `sku`.
   *
   * Modifica o saldo de `sku` na instância. Se falhar, o saldo não muda.
   *
   * @param sku Identificador do produto.
   * @param quantidade Quantidade a somar; inteiro maior que zero.
   * @throws QuantidadeInvalidaError Se `quantidade` não for inteiro ou for menor ou
   * igual a zero.
   * @throws LimiteExcedidoError Se o saldo resultante ultrapassar `limitePorSku`.
   */
  repor(sku: string, quantidade: number): void {
    validarQuantidade(quantidade);
    const novoSaldo = this.quantidade(sku) + quantidade;
    if (novoSaldo > this.limitePorSku) {
      throw new LimiteExcedidoError(
        `saldo de ${sku} ultrapassaria o limite de ${this.limitePorSku}: ${novoSaldo}`,
      );
    }
    this.saldos.set(sku, novoSaldo);
  }

  /**
   * Devolve o saldo atual de `sku`.
   *
   * Não modifica seus argumentos nem a instância.
   *
   * @param sku Identificador do produto.
   * @returns Saldo de `sku`; zero se o sku nunca recebeu reposição.
   */
  quantidade(sku: string): number {
    return this.saldos.get(sku) ?? 0;
  }

  /**
   * Debita do saldo cada item de `itens`, na ordem, e acrescenta uma cópia de cada um
   * em `pedido.linhas`.
   *
   * Modifica os saldos da instância e `pedido.linhas`; não modifica `itens`. A operação
   * não é atômica: no primeiro erro ela para, e os itens anteriores permanecem debitados
   * e presentes em `pedido.linhas`.
   *
   * @param itens Itens a reservar, processados na ordem da lista.
   * @param pedido Pedido que recebe as linhas reservadas.
   * @throws QuantidadeInvalidaError Se a quantidade de um item não for inteiro ou for
   * menor ou igual a zero.
   * @throws EstoqueInsuficienteError Se o saldo de um item for menor que a quantidade
   * pedida.
   */
  reservar(itens: readonly ItemReserva[], pedido: Pedido): void {
    for (const { sku, quantidade } of itens) {
      validarQuantidade(quantidade);
      const saldo = this.quantidade(sku);
      if (saldo < quantidade) {
        throw new EstoqueInsuficienteError(
          `saldo de ${sku} é ${saldo}, insuficiente para ${quantidade}`,
        );
      }
      this.saldos.set(sku, saldo - quantidade);
      pedido.linhas.push({ sku, quantidade });
    }
  }
}

/**
 * Normaliza `skus` no lugar: remove espaços das pontas, converte para maiúsculas e
 * descarta os textos que ficarem vazios.
 *
 * Modifica `skus` in-place, preservando a ordem dos que permanecem. Não modifica nenhum
 * outro estado.
 *
 * @param skus Lista mutável de textos a normalizar.
 * @returns Quantidade de elementos removidos por ficarem vazios.
 */
export function normalizarSkus(skus: string[]): number {
  const normalizados = skus
    .map((sku) => sku.trim().toUpperCase())
    .filter((sku) => sku.length > 0);
  const removidos = skus.length - normalizados.length;
  skus.splice(0, skus.length, ...normalizados);
  return removidos;
}

/**
 * Valida que `quantidade` é um inteiro maior que zero.
 *
 * Não modifica nenhum estado.
 *
 * @param quantidade Valor a validar.
 * @throws QuantidadeInvalidaError Se `quantidade` não for inteiro ou for menor ou igual
 * a zero.
 */
function validarQuantidade(quantidade: number): void {
  if (!Number.isInteger(quantidade) || quantidade <= 0) {
    throw new QuantidadeInvalidaError(
      `quantidade deve ser um inteiro maior que zero: ${quantidade}`,
    );
  }
}
