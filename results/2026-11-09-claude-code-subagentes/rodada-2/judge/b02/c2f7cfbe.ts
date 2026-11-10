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
 * Erro lançado quando um usuário tenta enviar a licença de uma venda sem ter
 * permissão de upload, ou seja, quando não é compositor da guia da venda.
 *
 * @property vendaId Identificador da venda cujo upload foi recusado.
 * @property userId Usuário que tentou o upload; `null` quando não há usuário autenticado.
 */
export class UploadNaoPermitido extends Error {
  /**
   * @param vendaId Identificador da venda cujo upload foi recusado.
   * @param userId Usuário que tentou o upload; `null` quando não há usuário autenticado.
   */
  constructor(
    readonly vendaId: number,
    readonly userId: number | null,
  ) {
    super(`Usuário ${userId ?? "anônimo"} não pode enviar licença da venda ${vendaId}.`);
    this.name = "UploadNaoPermitido";
  }
}

/**
 * Decide quem pode enviar e acessar a licença de uma venda, com base nos
 * administradores informados e nos papéis do usuário na venda (comprador ou
 * compositor da guia).
 *
 * @constructor
 * @param adminIds Identificadores dos usuários administradores. O conjunto é
 *   apenas lido; o validador não o modifica.
 */
export class LicencaAccessValidator {
  constructor(private readonly adminIds: ReadonlySet<number>) {}

  /**
   * Informa se o usuário pode enviar a licença da venda: só um compositor da
   * guia da venda pode enviar; administradores e o comprador não podem.
   *
   * Não modifica seus argumentos nem o estado da instância.
   *
   * @param venda Venda cuja licença seria enviada.
   * @param userId Usuário que pretende enviar; `null` representa ausência de
   *   usuário autenticado.
   * @returns `true` se `userId` é compositor da guia da venda; `false` caso
   *   contrário, inclusive quando `userId` é `null`.
   */
  canUpload(venda: Venda, userId: number | null): boolean {
    if (userId === null) return false;
    return this.isCompositor(venda, userId);
  }

  /**
   * Exige que o usuário possa enviar a licença da venda, segundo a mesma regra
   * de {@link LicencaAccessValidator.canUpload}.
   *
   * Não modifica seus argumentos nem o estado da instância.
   *
   * @param venda Venda cuja licença seria enviada.
   * @param userId Usuário que pretende enviar; `null` representa ausência de
   *   usuário autenticado e é sempre recusado.
   * @throws {UploadNaoPermitido} Quando `canUpload(venda, userId)` é `false`.
   */
  requireUpload(venda: Venda, userId: number | null): void {
    if (!this.canUpload(venda, userId)) {
      throw new UploadNaoPermitido(venda.id, userId);
    }
  }

  canAccess(venda: Venda, userId: number | null): boolean {
    if (userId === null) return false;
    if (this.isAdmin(userId)) return true;
    if (venda.compradorId === userId) return true;
    return this.isCompositor(venda, userId);
  }

  /**
   * Informa se o usuário pode acessar a licença da venda, considerando o
   * cancelamento: em venda cancelada, administradores e compositores da guia
   * mantêm o acesso e o comprador o perde. Em venda não cancelada, a regra é a
   * de {@link LicencaAccessValidator.canAccess}.
   *
   * Não modifica seus argumentos nem o estado da instância.
   *
   * @param venda Venda cuja licença seria acessada; `venda.cancelada` decide
   *   qual regra se aplica.
   * @param userId Usuário que pretende acessar; `null` representa ausência de
   *   usuário autenticado.
   * @returns `true` se o usuário tem acesso; `false` caso contrário, inclusive
   *   quando `userId` é `null`. Um usuário que é ao mesmo tempo comprador e
   *   compositor (ou administrador) mantém o acesso em venda cancelada.
   */
  canAccessAfterCancel(venda: Venda, userId: number | null): boolean {
    if (!venda.cancelada) return this.canAccess(venda, userId);
    if (userId === null) return false;
    if (this.isAdmin(userId)) return true;
    return this.isCompositor(venda, userId);
  }

  private isAdmin(userId: number): boolean {
    return this.adminIds.has(userId);
  }

  private isCompositor(venda: Venda, userId: number): boolean {
    return venda.guia.compositores.some((c) => c.userId === userId);
  }
}
