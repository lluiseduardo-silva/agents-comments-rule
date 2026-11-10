use std::collections::HashSet;
use std::fmt;

/// Erro de um envio de licença recusado porque o usuário não é compositor da guia
/// da venda.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UploadNaoPermitido {
    /// Identificador da venda cujo envio foi recusado.
    pub venda_id: u64,
}

impl fmt::Display for UploadNaoPermitido {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "envio de licença não permitido para a venda {}", self.venda_id)
    }
}

impl std::error::Error for UploadNaoPermitido {}

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

pub struct LicencaAccessValidator {
    admin_ids: HashSet<u64>,
}

impl LicencaAccessValidator {
    pub fn new(admin_ids: HashSet<u64>) -> Self {
        Self { admin_ids }
    }

    /// Informa se o usuário pode enviar a licença da venda: só um compositor da guia
    /// da venda pode; admin, comprador e qualquer outro usuário não podem.
    ///
    /// Não modifica os argumentos nem a instância.
    ///
    /// # Arguments
    ///
    /// * `venda` - Venda cuja licença seria enviada.
    /// * `user_id` - Usuário que tenta enviar; `None` representa um usuário não
    ///   autenticado.
    ///
    /// # Returns
    ///
    /// `true` se `user_id` for o de um compositor da guia de `venda`; `false` caso
    /// contrário, inclusive quando `user_id` é `None`.
    pub fn can_upload(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        Self::is_compositor(venda, user_id)
    }

    /// Exige que o usuário possa enviar a licença da venda, pela mesma regra de
    /// [`Self::can_upload`].
    ///
    /// Não modifica os argumentos nem a instância.
    ///
    /// # Arguments
    ///
    /// * `venda` - Venda cuja licença seria enviada.
    /// * `user_id` - Usuário que tenta enviar; `None` representa um usuário não
    ///   autenticado.
    ///
    /// # Errors
    ///
    /// Devolve [`UploadNaoPermitido`] quando [`Self::can_upload`] é `false` para
    /// `venda` e `user_id`.
    pub fn require_upload(
        &self,
        venda: &Venda,
        user_id: Option<u64>,
    ) -> Result<(), UploadNaoPermitido> {
        if self.can_upload(venda, user_id) {
            Ok(())
        } else {
            Err(UploadNaoPermitido { venda_id: venda.id })
        }
    }

    /// Informa se o usuário mantém acesso à licença da venda, considerando o
    /// cancelamento: em venda cancelada, admin e compositor da guia mantêm o acesso e
    /// o comprador perde; em venda não cancelada, vale a regra de
    /// [`Self::can_access`].
    ///
    /// Não modifica os argumentos nem a instância.
    ///
    /// # Arguments
    ///
    /// * `venda` - Venda cuja licença seria acessada.
    /// * `user_id` - Usuário que tenta acessar; `None` representa um usuário não
    ///   autenticado.
    ///
    /// # Returns
    ///
    /// `true` se o usuário tem acesso segundo a regra acima; `false` caso contrário,
    /// inclusive quando `user_id` é `None`.
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
