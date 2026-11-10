use std::collections::HashSet;
use std::fmt;

/// Erro devolvido por [`LicencaAccessValidator::require_upload`] quando o usuário não
/// pode enviar a licença da venda.
///
/// Ocorre quando não há usuário identificado ou quando o usuário não é compositor da
/// guia da venda.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UploadNaoPermitido {
    /// Identificador da venda cujo envio foi recusado.
    pub venda_id: u64,
    /// Usuário que tentou o envio; `None` quando não havia usuário identificado.
    pub user_id: Option<u64>,
}

impl fmt::Display for UploadNaoPermitido {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self.user_id {
            Some(user_id) => write!(
                f,
                "usuário {} não pode enviar licença da venda {}",
                user_id, self.venda_id
            ),
            None => write!(
                f,
                "usuário não identificado não pode enviar licença da venda {}",
                self.venda_id
            ),
        }
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

    /// Indica se o usuário pode enviar a licença da venda: só um compositor da guia da
    /// venda pode enviar; administradores e o comprador não podem.
    ///
    /// Não modifica seus argumentos nem a instância.
    ///
    /// # Arguments
    ///
    /// * `venda` - Venda cuja licença seria enviada.
    /// * `user_id` - Usuário que pretende enviar; `None` representa ausência de usuário
    ///   identificado e nunca recebe permissão.
    ///
    /// # Returns
    ///
    /// `true` se `user_id` for um compositor da guia de `venda`; `false` caso contrário,
    /// inclusive quando `user_id` é `None`.
    pub fn can_upload(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        Self::is_compositor(venda, user_id)
    }

    /// Exige que o usuário possa enviar a licença da venda, segundo
    /// [`can_upload`](Self::can_upload).
    ///
    /// Não modifica seus argumentos nem a instância.
    ///
    /// # Arguments
    ///
    /// * `venda` - Venda cuja licença seria enviada.
    /// * `user_id` - Usuário que pretende enviar; `None` representa ausência de usuário
    ///   identificado.
    ///
    /// # Returns
    ///
    /// `Ok(())` quando o envio é permitido.
    ///
    /// # Errors
    ///
    /// Devolve [`UploadNaoPermitido`], com o id da venda e o `user_id` recebido, quando
    /// [`can_upload`](Self::can_upload) devolve `false`.
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

    /// Indica se o usuário mantém acesso à licença considerando o cancelamento da venda:
    /// em venda cancelada, administradores e compositores da guia mantêm o acesso e o
    /// comprador o perde; em venda não cancelada vale a mesma regra de
    /// [`can_access`](Self::can_access).
    ///
    /// Não modifica seus argumentos nem a instância.
    ///
    /// # Arguments
    ///
    /// * `venda` - Venda cuja licença seria acessada; `venda.cancelada` decide qual regra
    ///   se aplica.
    /// * `user_id` - Usuário que pretende acessar; `None` representa ausência de usuário
    ///   identificado e nunca recebe acesso.
    ///
    /// # Returns
    ///
    /// Para venda cancelada, `true` se `user_id` for administrador ou compositor da guia.
    /// Para venda não cancelada, o resultado de [`can_access`](Self::can_access). `false`
    /// quando `user_id` é `None`.
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
