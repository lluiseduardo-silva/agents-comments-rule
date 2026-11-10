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
 * Erro que sinaliza a recusa do envio de uma licença: o usuário não é compositor da
 * guia da venda, ou não há usuário autenticado.
 *
 * Lançado por {@link LicencaAccessValidator.requireUpload}. A propriedade `name` vale
 * `"UploadNaoPermitido"`.
 */
export class UploadNaoPermitido extends Error {
  /** Id da venda para a qual o envio é recusado. */
  readonly vendaId: number;

  /** Id do usuário recusado; `null` quando não há usuário autenticado. */
  readonly userId: number | null;

  /**
   * Cria o erro com a venda e o usuário recusado e monta `message` a partir deles.
   *
   * @param vendaId - Id da venda para a qual o envio é recusado.
   * @param userId - Id do usuário recusado; `null` quando não há usuário autenticado.
   */
  constructor(vendaId: number, userId: number | null) {
    super(
      userId === null
        ? `Envio de licença não permitido na venda ${vendaId}: não há usuário autenticado.`
        : `Envio de licença não permitido na venda ${vendaId}: o usuário ${userId} não é compositor da guia.`,
    );
    this.name = "UploadNaoPermitido";
    this.vendaId = vendaId;
    this.userId = userId;
  }
}

/**
 * Decide quem pode enviar e quem pode acessar a licença de uma venda, conforme o papel
 * do usuário: administrador, comprador da venda ou compositor da guia.
 *
 * O único estado da instância é o conjunto de administradores recebido no construtor;
 * nenhum método o altera, nem altera a venda consultada.
 */
export class LicencaAccessValidator {
  /**
   * Cria o validador para um conjunto de administradores.
   *
   * @param adminIds - Ids dos usuários administradores; vazio significa que ninguém é
   *   administrador. O conjunto é guardado por referência, sem cópia: mudanças feitas
   *   nele depois da construção valem para as consultas seguintes.
   */
  constructor(private readonly adminIds: ReadonlySet<number>) {}

  /**
   * Indica se o usuário pode enviar a licença da venda: só um compositor da guia da
   * venda pode enviar.
   *
   * Administradores e o comprador não podem enviar, a menos que também sejam
   * compositores da guia. Não modifica `venda` nem o estado da instância.
   *
   * @param venda - Venda cuja licença seria enviada. `venda.guia.compositores` precisa
   *   estar completa: quem não consta nela é tratado como não compositor.
   * @param userId - Id do usuário que tenta enviar; `null` significa que não há
   *   usuário autenticado.
   * @returns `true` se `userId` for de um compositor da guia da venda; `false` nos
   *   demais casos, inclusive quando `userId` é `null`.
   */
  canUpload(venda: Venda, userId: number | null): boolean {
    if (userId === null) return false;
    return this.isCompositor(venda, userId);
  }

  /**
   * Exige que o usuário possa enviar a licença da venda, pela mesma regra de
   * {@link LicencaAccessValidator.canUpload}; retorna sem valor quando o envio é
   * permitido.
   *
   * Não modifica `venda` nem o estado da instância, inclusive quando lança.
   *
   * @param venda - Venda cuja licença seria enviada. `venda.guia.compositores` precisa
   *   estar completa: quem não consta nela é tratado como não compositor.
   * @param userId - Id do usuário que tenta enviar; `null` significa que não há
   *   usuário autenticado.
   * @throws {@link UploadNaoPermitido} Se `canUpload(venda, userId)` for `false`:
   *   `userId` é `null` ou não é de um compositor da guia da venda.
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
   * Indica se o usuário tem acesso à licença de uma venda cancelada: administradores
   * e compositores da guia mantêm o acesso; o comprador perde.
   *
   * O comprador só tem acesso se também for administrador ou compositor da guia. Não
   * consulta `venda.cancelada`: aplica a regra de venda cancelada qualquer que seja o
   * valor desse campo. Não modifica `venda` nem o estado da instância.
   *
   * @param venda - Venda avaliada. `venda.guia.compositores` precisa estar completa:
   *   quem não consta nela é tratado como não compositor.
   * @param userId - Id do usuário que pede acesso; `null` significa que não há usuário
   *   autenticado.
   * @returns `true` se `userId` for de um administrador ou de um compositor da guia da
   *   venda; `false` nos demais casos, inclusive para o comprador e quando `userId` é
   *   `null`.
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
