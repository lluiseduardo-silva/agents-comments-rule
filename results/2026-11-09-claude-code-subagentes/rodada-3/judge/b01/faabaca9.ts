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
 * Erro lançado quando um usuário tenta enviar a licença de uma venda sem ser
 * compositor da guia dessa venda.
 */
export class UploadNaoPermitido extends Error {
  /**
   * @param vendaId Identificador da venda cujo envio foi recusado.
   * @param userId Usuário que tentou enviar; `null` para chamada sem usuário autenticado.
   */
  constructor(
    readonly vendaId: number,
    readonly userId: number | null,
  ) {
    super(`Usuário ${userId ?? "anônimo"} não pode enviar licença da venda ${vendaId}`);
    this.name = "UploadNaoPermitido";
  }
}

export class LicencaAccessValidator {
  constructor(private readonly adminIds: ReadonlySet<number>) {}

  /**
   * Indica se o usuário pode enviar a licença da venda: só um compositor da guia
   * pode enviar; admin e comprador não podem.
   *
   * Não modifica seus argumentos nem a instância.
   *
   * @param venda Venda cuja licença seria enviada.
   * @param userId Usuário que pretende enviar; `null` representa usuário não autenticado.
   * @returns `true` se `userId` é compositor da guia da venda; `false` caso contrário,
   *   inclusive quando `userId` é `null`.
   */
  canUpload(venda: Venda, userId: number | null): boolean {
    if (userId === null) return false;
    return this.isCompositor(venda, userId);
  }

  /**
   * Exige que o usuário possa enviar a licença da venda, segundo {@link canUpload}.
   *
   * Não modifica seus argumentos nem a instância.
   *
   * @param venda Venda cuja licença seria enviada.
   * @param userId Usuário que pretende enviar; `null` representa usuário não autenticado.
   * @throws {UploadNaoPermitido} Se `userId` é `null` ou não é compositor da guia da venda.
   */
  requireUpload(venda: Venda, userId: number | null): void {
    if (!this.canUpload(venda, userId)) {
      throw new UploadNaoPermitido(venda.id, userId);
    }
  }

  /**
   * Indica se o usuário tem acesso à licença da venda, considerando cancelamento: em
   * venda cancelada, admin e compositor da guia mantêm o acesso e o comprador o perde;
   * em venda não cancelada, vale a mesma regra de {@link canAccess}.
   *
   * Não modifica seus argumentos nem a instância.
   *
   * @param venda Venda cuja licença seria acessada.
   * @param userId Usuário que pretende acessar; `null` representa usuário não autenticado.
   * @returns `true` se o usuário tem acesso; `false` caso contrário, inclusive quando
   *   `userId` é `null`.
   */
  canAccessAfterCancel(venda: Venda, userId: number | null): boolean {
    if (!venda.cancelada) return this.canAccess(venda, userId);
    if (userId === null) return false;
    return this.isAdmin(userId) || this.isCompositor(venda, userId);
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
