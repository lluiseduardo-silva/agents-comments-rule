use std::collections::HashSet;

pub struct Compositor {
    pub user_id: u64,
}

pub struct Guia {
    pub compositores: Vec<Compositor>,
}

pub struct Venda {
    pub id: u64,
    pub comprador_id: u64,
    pub guia: Guia,
    pub cancelada: bool,
}

/// Erro de `require_upload`: o usuário não pode enviar a licença desta venda.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct UploadNaoPermitido;

impl std::fmt::Display for UploadNaoPermitido {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "upload de licença não permitido para este usuário")
    }
}

impl std::error::Error for UploadNaoPermitido {}

pub struct LicencaAccessValidator {
    admin_ids: HashSet<u64>,
}

impl LicencaAccessValidator {
    pub fn new(admin_ids: HashSet<u64>) -> Self {
        Self { admin_ids }
    }

    /// Indica se o usuário pode enviar a licença da venda.
    ///
    /// Somente compositor da guia pode enviar. Admin NÃO envia (LIC-482, D2):
    /// o `LicenseUploadService.assertUploadAllowed` já rejeitava admin com 403
    /// em `assertFileOwner`, então aceitar admin aqui só prometia um upload que
    /// falhava depois e deixava objeto órfão no S3. Habilitar de verdade exigiria
    /// aceitar um `onBehalfOfUserId` explícito no confirm, dando ao admin o poder de
    /// aprovar a participação de um compositor. O caminho administrativo para
    /// destravar a venda é o `manual-complete`, que é auditado.
    pub fn can_upload(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        Self::is_compositor(venda, user_id)
    }

    /// Variante de `can_upload` que falha em vez de devolver `bool`.
    ///
    /// Use na fronteira da operação, antes de qualquer efeito colateral (como
    /// gravar objeto no S3), para rejeitar cedo e de forma explícita.
    pub fn require_upload(
        &self,
        venda: &Venda,
        user_id: Option<u64>,
    ) -> Result<(), UploadNaoPermitido> {
        if self.can_upload(venda, user_id) {
            Ok(())
        } else {
            Err(UploadNaoPermitido)
        }
    }

    /// Acesso à licença depois que a venda morreu (cancelada).
    ///
    /// Admin e compositor da guia mantêm o acesso; o comprador o perde.
    /// Venda não cancelada não é tratada aqui: use `can_access`. Sem usuário
    /// identificado, o acesso é negado.
    pub fn can_access_after_cancel(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        if !venda.cancelada {
            return false;
        }
        self.is_admin(user_id) || Self::is_compositor(venda, user_id)
    }

    pub fn can_access(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        if self.is_admin(user_id) {
            return true;
        }
        if venda.comprador_id == user_id {
            return true;
        }
        Self::is_compositor(venda, user_id)
    }

    fn is_admin(&self, user_id: u64) -> bool {
        self.admin_ids.contains(&user_id)
    }

    fn is_compositor(venda: &Venda, user_id: u64) -> bool {
        venda.guia.compositores.iter().any(|c| c.user_id == user_id)
    }
}
