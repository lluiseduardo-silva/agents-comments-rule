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

/// Erro de upload recusado: o usuario nao e compositor da guia da venda.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct UploadNaoPermitido;

impl std::fmt::Display for UploadNaoPermitido {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "upload de licenca nao permitido para este usuario")
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

    /// Indica se o usuario pode enviar a licenca da venda.
    ///
    /// LIC-482 (PR9, passo D2): somente compositor da guia envia. O admin
    /// deixou de ser aceito porque `LicenseUploadService.assertUploadAllowed`
    /// ja rejeitava o admin com 403 em `assertFileOwner` (o arquivo pertence ao
    /// titular), deixando um objeto orfao no S3 a cada tentativa (incidente de
    /// 14/10). Habilitar de verdade exigiria um `onBehalfOfUserId` no confirm,
    /// dando ao admin o poder de aprovar a participacao de um compositor.
    /// Para destravar uma venda, o admin usa `manual-complete`, que e auditado.
    pub fn can_upload(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        Self::is_compositor(venda, user_id)
    }

    /// Falha com `UploadNaoPermitido` quando `can_upload` for falso.
    /// Nao devolve valor: o chamador usa `?` e so segue se o envio for permitido.
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

    /// Acesso a uma venda considerando o cancelamento.
    ///
    /// Venda cancelada: admin e compositor da guia mantem o acesso; o comprador
    /// perde. Venda nao cancelada: vale a regra normal de `can_access`.
    pub fn can_access_after_cancel(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        if !venda.cancelada {
            return self.can_access(venda, user_id);
        }
        let Some(user_id) = user_id else {
            return false;
        };
        // Comprador nao e verificado aqui de proposito: apos o cancelamento ele
        // so teria acesso se tambem fosse admin ou compositor da guia.
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
