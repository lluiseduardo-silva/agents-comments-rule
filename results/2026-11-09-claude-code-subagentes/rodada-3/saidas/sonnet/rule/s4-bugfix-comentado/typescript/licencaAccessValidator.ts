export interface Compositor {
  userId: number;
}

export interface Guia {
  compositores: Compositor[];
}

export interface Venda {
  id: number;
  compradorId: number;
  guia: Guia;
  cancelada: boolean;
}

/**
 * Erro lançado quando o usuário não pode enviar a licença de uma venda.
 *
 * @property vendaId Identificador da venda cujo envio foi recusado.
 */
export class UploadNaoPermitido extends Error {
  /**
   * @param vendaId Identificador da venda cujo envio foi recusado.
   */
  constructor(readonly vendaId: number) {
    super(`Usuário não pode enviar a licença da venda ${vendaId}`);
    this.name = "UploadNaoPermitido";
  }
}

export class LicencaAccessValidator {
  constructor(private readonly adminIds: ReadonlySet<number>) {}

  /**
   * Indica se o usuário pode enviar a licença da venda: somente compositor da guia.
   *
   * Não modifica seus argumentos nem a instância.
   *
   * @param venda Venda cuja licença seria enviada.
   * @param userId Identificador do usuário; `null` representa usuário não autenticado.
   * @returns `true` se o usuário é compositor da guia da venda; `false` para
   * administrador, comprador, não compositor ou `userId` nulo.
   */
  canUpload(venda: Venda, userId: number | null): boolean {
    if (userId === null) return false;
    return this.isCompositor(venda, userId);
  }

  /**
   * Indica se o usuário mantém acesso a uma venda cancelada: administrador e compositor
   * da guia mantêm; o comprador perde. Para venda não cancelada, o resultado é o de
   * {@link canAccess}.
   *
   * Não modifica seus argumentos nem a instância.
   *
   * @param venda Venda a ser consultada.
   * @param userId Identificador do usuário; `null` representa usuário não autenticado.
   * @returns `true` se o acesso é permitido; `false` caso contrário, inclusive para
   * `userId` nulo e para o comprador de venda cancelada que não seja também
   * administrador ou compositor.
   */
  canAccessAfterCancel(venda: Venda, userId: number | null): boolean {
    if (userId === null) return false;
    if (!venda.cancelada) return this.canAccess(venda, userId);
    return this.isAdmin(userId) || this.isCompositor(venda, userId);
  }

  /**
   * Garante que o usuário pode enviar a licença da venda.
   *
   * Não modifica seus argumentos nem a instância.
   *
   * @param venda Venda cuja licença seria enviada.
   * @param userId Identificador do usuário; `null` representa usuário não autenticado.
   * @throws UploadNaoPermitido Se {@link canUpload} for `false` para a venda e o usuário.
   */
  requireUpload(venda: Venda, userId: number | null): void {
    if (!this.canUpload(venda, userId)) {
      throw new UploadNaoPermitido(venda.id);
    }
  }

  canAccess(venda: Venda, userId: number | null): boolean {
    if (userId === null) return false;
    if (this.isAdmin(userId)) return true;
    if (venda.compradorId === userId) return true;
    return this.isCompositor(venda, userId);
  }

  private isAdmin(userId: number): boolean {
    return this.adminIds.has(userId);
  }

  private isCompositor(venda: Venda, userId: number): boolean {
    return venda.guia.compositores.some((c) => c.userId === userId);
  }
}
