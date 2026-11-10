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

export class UploadNaoPermitido extends Error {
  constructor(
    readonly vendaId: number,
    readonly userId: number | null,
  ) {
    super(`Upload de licença não permitido (venda ${vendaId})`);
    this.name = "UploadNaoPermitido";
  }
}

export class LicencaAccessValidator {
  constructor(private readonly adminIds: ReadonlySet<number>) {}

  canUpload(venda: Venda, userId: number | null): boolean {
    if (userId === null) return false;
    return this.isCompositor(venda, userId);
  }

  requireUpload(venda: Venda, userId: number | null): void {
    if (!this.canUpload(venda, userId)) {
      throw new UploadNaoPermitido(venda.id, userId);
    }
  }

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
