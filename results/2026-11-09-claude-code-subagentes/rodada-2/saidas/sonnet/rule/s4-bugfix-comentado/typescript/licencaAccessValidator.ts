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
 * Erro lançado quando um usuário sem permissão tenta enviar a licença de uma venda.
 *
 * @property vendaId Identificador da venda do envio recusado.
 * @property userId Identificador do usuário recusado; `null` se não autenticado.
 */
export class UploadNaoPermitido extends Error {
  /**
   * @param vendaId Identificador da venda do envio recusado.
   * @param userId Identificador do usuário recusado; `null` se não autenticado.
   */
  constructor(
    readonly vendaId: number,
    readonly userId: number | null,
  ) {
    super(`Usuário ${userId} não pode enviar licença da venda ${vendaId}`);
    this.name = "UploadNaoPermitido";
  }
}

export class LicencaAccessValidator {
  constructor(private readonly adminIds: ReadonlySet<number>) {}

  /**
   * Indica se o usuário pode enviar a licença da venda: somente compositor da guia pode;
   * administrador não envia licença.
   *
   * Não modifica seus argumentos nem a instância.
   *
   * @param venda Venda cuja guia define os compositores autorizados.
   * @param userId Identificador do usuário; `null` representa usuário não autenticado.
   * @returns `true` se o usuário é compositor da guia da venda; `false` caso contrário,
   * inclusive para `null` e para administradores que não sejam compositores.
   */
  canUpload(venda: Venda, userId: number | null): boolean {
    if (userId === null) return false;
    return this.isCompositor(venda, userId);
  }

  /**
   * Exige que o usuário possa enviar a licença da venda, nos mesmos termos de
   * {@link LicencaAccessValidator.canUpload}.
   *
   * Não modifica seus argumentos nem a instância.
   *
   * @param venda Venda cuja guia define os compositores autorizados.
   * @param userId Identificador do usuário; `null` representa usuário não autenticado.
   * @throws UploadNaoPermitido Se `canUpload` retornar `false` para a venda e o usuário.
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
   * Indica se o usuário mantém acesso à venda após ela ser cancelada: administrador e
   * compositor da guia mantêm; o comprador perde. Em venda não cancelada, o comprador
   * também tem acesso.
   *
   * Não modifica seus argumentos nem a instância.
   *
   * @param venda Venda a consultar.
   * @param userId Identificador do usuário; `null` representa usuário não autenticado.
   * @returns `true` se o usuário tem acesso; `false` caso contrário, inclusive para `null`
   * e para o comprador de venda cancelada.
   */
  canAccessAfterCancel(venda: Venda, userId: number | null): boolean {
    if (userId === null) return false;
    if (this.isAdmin(userId)) return true;
    if (this.isCompositor(venda, userId)) return true;
    return venda.compradorId === userId && !venda.cancelada;
  }

  private isAdmin(userId: number): boolean {
    return this.adminIds.has(userId);
  }

  private isCompositor(venda: Venda, userId: number): boolean {
    return venda.guia.compositores.some((c) => c.userId === userId);
  }
}
