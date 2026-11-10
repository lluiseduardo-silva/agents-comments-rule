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
 * Erro que sinaliza a recusa do envio da licença de uma venda a um usuário sem
 * permissão de envio. A propriedade herdada `name` vale `"UploadNaoPermitido"`.
 */
export class UploadNaoPermitido extends Error {
  /** Id da venda cujo envio foi recusado. */
  readonly vendaId: number;

  /** Id do usuário recusado; `null` quando a tentativa não tinha usuário. */
  readonly userId: number | null;

  /**
   * @param vendaId - Id da venda cujo envio foi recusado.
   * @param userId - Id do usuário recusado; `null` quando a tentativa não tinha usuário.
   */
  constructor(vendaId: number, userId: number | null) {
    super(
      `Envio de licença não permitido na venda ${vendaId} (usuário: ${userId ?? "nenhum"}).`,
    );
    this.name = "UploadNaoPermitido";
    this.vendaId = vendaId;
    this.userId = userId;
  }
}

/**
 * Decide quem pode enviar e quem pode acessar a licença de uma venda.
 *
 * Cada decisão depende só dos argumentos da chamada e do conjunto de administradores
 * recebido na construção.
 */
export class LicencaAccessValidator {
  /**
   * @param adminIds - Ids dos usuários administradores. A instância guarda a referência
   *   sem copiar: alterações feitas depois no conjunto valem para as decisões seguintes.
   *   A instância nunca o modifica.
   */
  constructor(private readonly adminIds: ReadonlySet<number>) {}

  /**
   * Indica se o usuário pode enviar a licença da venda: só um compositor da guia da
   * venda pode. Ser administrador ou comprador não concede essa permissão.
   *
   * Não modifica os argumentos nem a instância.
   *
   * @param venda - Venda cuja licença seria enviada.
   * @param userId - Id do usuário que tenta o envio; `null` (nenhum usuário) é aceito e
   *   resulta em `false`.
   * @returns `true` se `userId` é o de um compositor de `venda.guia`; `false` nos demais
   *   casos, inclusive quando `userId` é `null`.
   */
  canUpload(venda: Venda, userId: number | null): boolean {
    if (userId === null) return false;
    return this.isCompositor(venda, userId);
  }

  /**
   * Exige que o usuário possa enviar a licença da venda, pela regra de
   * {@link LicencaAccessValidator.canUpload}; retorna sem valor quando o envio é
   * permitido.
   *
   * Não modifica os argumentos, a instância nem estado externo, inclusive quando falha.
   *
   * @param venda - Venda cuja licença seria enviada.
   * @param userId - Id do usuário que tenta o envio; `null` (nenhum usuário) é aceito e
   *   sempre produz o erro.
   * @throws {@link UploadNaoPermitido} Se `canUpload(venda, userId)` é `false`: `userId`
   *   é `null` ou não é o de um compositor de `venda.guia`.
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
   * Indica se o usuário tem acesso à licença de uma venda cancelada: administradores e
   * compositores da guia têm; o comprador perde o acesso quando a venda é cancelada.
   *
   * Não modifica os argumentos nem a instância.
   *
   * @param venda - Venda cancelada cuja licença seria acessada.
   * @param userId - Id do usuário que pede o acesso; `null` (nenhum usuário) é aceito e
   *   resulta em `false`.
   * @returns `true` se `userId` é o de um administrador ou o de um compositor de
   *   `venda.guia`; `false` nos demais casos, inclusive para o comprador que não é
   *   administrador nem compositor e quando `userId` é `null`.
   * @remarks Pré-condição: `venda` está cancelada. O método não consulta
   *   `venda.cancelada`; cabe ao chamador aplicá-lo só a vendas nesse estado.
   */
  canAccessAfterCancel(venda: Venda, userId: number | null): boolean {
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
