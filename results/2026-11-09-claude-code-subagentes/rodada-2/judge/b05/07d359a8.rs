use std::collections::HashSet;
use std::fmt;

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

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UploadNaoPermitido {
    pub venda_id: u64,
    pub user_id: Option<u64>,
}

impl fmt::Display for UploadNaoPermitido {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self.user_id {
            Some(user_id) => write!(
                f,
                "upload de licença não permitido para o usuário {} na venda {}",
                user_id, self.venda_id
            ),
            None => write!(
                f,
                "upload de licença não permitido sem usuário autenticado na venda {}",
                self.venda_id
            ),
        }
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

    /// Só compositor da guia envia licença. Admin não envia (LIC-482): o
    /// caminho administrativo para destravar uma venda é `manual-complete`.
    pub fn can_upload(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        Self::is_compositor(venda, user_id)
    }

    /// Falha com `UploadNaoPermitido` quando `can_upload` for falso.
    pub fn require_upload(
        &self,
        venda: &Venda,
        user_id: Option<u64>,
    ) -> Result<(), UploadNaoPermitido> {
        if self.can_upload(venda, user_id) {
            Ok(())
        } else {
            Err(UploadNaoPermitido {
                venda_id: venda.id,
                user_id,
            })
        }
    }

    /// Venda cancelada: admin e compositor da guia mantêm o acesso; o
    /// comprador perde. Venda ativa: mesmas regras de `can_access`.
    pub fn can_access_after_cancel(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        if !venda.cancelada {
            return self.can_access(venda, user_id);
        }
        let Some(user_id) = user_id else {
            return false;
        };
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
