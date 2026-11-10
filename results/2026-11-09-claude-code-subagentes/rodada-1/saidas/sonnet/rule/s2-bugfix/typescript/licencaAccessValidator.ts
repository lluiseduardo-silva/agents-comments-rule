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
 * Estende `Error` e não possui estado além da mensagem.
 */
export class UploadNaoPermitido extends Error {
  /**
   * Cria o erro com a mensagem padrão.
   *
   * Não modifica nenhum estado externo.
   */
  constructor() {
    super("Usuário não tem permissão para enviar a licença desta venda.");
    this.name = "UploadNaoPermitido";
  }
}

export class LicencaAccessValidator {
  constructor(private readonly adminIds: ReadonlySet<number>) {}

  /**
   * Indica se o usuário pode enviar a licença da venda: somente compositor da guia pode.
   *
   * Não modifica seus argumentos nem a instância.
   *
   * @param venda Venda cuja licença seria enviada.
   * @param userId Identificador do usuário; `null` representa usuário não autenticado.
   * @returns `true` se o usuário é compositor da guia da venda; `false` caso contrário,
   * inclusive para `null` e para administradores que não sejam compositores.
   */
  canUpload(venda: Venda, userId: number | null): boolean {
    if (userId === null) return false;
    return this.isCompositor(venda, userId);
  }

  /**
   * Exige que o usuário possa enviar a licença da venda.
   *
   * Não modifica seus argumentos nem a instância.
   *
   * @param venda Venda cuja licença seria enviada.
   * @param userId Identificador do usuário; `null` representa usuário não autenticado.
   * @throws UploadNaoPermitido Se `canUpload` for `false` para a venda e o usuário.
   */
  requireUpload(venda: Venda, userId: number | null): void {
    if (!this.canUpload(venda, userId)) throw new UploadNaoPermitido();
  }

  /**
   * Indica se o usuário mantém acesso à licença de uma venda cancelada: administrador e
   * compositor da guia mantêm; o comprador perde.
   *
   * Não modifica seus argumentos nem a instância. O resultado não depende de
   * `venda.cancelada`.
   *
   * @param venda Venda cancelada.
   * @param userId Identificador do usuário; `null` representa usuário não autenticado.
   * @returns `true` se o usuário é administrador ou compositor da guia; `false` caso
   * contrário, inclusive para `null` e para o comprador.
   */
  canAccessAfterCancel(venda: Venda, userId: number | null): boolean {
    if (userId === null) return false;
    if (this.isAdmin(userId)) return true;
    return this.isCompositor(venda, userId);
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
