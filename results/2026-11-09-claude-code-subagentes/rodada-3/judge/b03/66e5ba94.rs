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

/// Erro de um usuário sem permissão para enviar a licença de uma venda.
///
/// # Fields
/// * `venda_id` - Identificador da venda para a qual o envio foi tentado.
/// * `user_id` - Usuário que tentou o envio; `None` quando a chamada era anônima.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UploadNaoPermitido {
    pub venda_id: u64,
    pub user_id: Option<u64>,
}

impl std::fmt::Display for UploadNaoPermitido {
    /// Escreve uma mensagem com o id da venda e o usuário.
    ///
    /// Modifica apenas o formatador `f`; não modifica a instância.
    ///
    /// # Errors
    /// Propaga o erro de escrita de `f`.
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "upload de licença não permitido: venda {}, usuário {:?}",
            self.venda_id, self.user_id
        )
    }
}

impl std::error::Error for UploadNaoPermitido {}

/// Decide quem pode enviar e quem pode acessar a licença de uma venda.
///
/// Guarda o conjunto de ids de administradores, que é imutável após a construção.
pub struct LicencaAccessValidator {
    admin_ids: HashSet<u64>,
}

impl LicencaAccessValidator {
    pub fn new(admin_ids: HashSet<u64>) -> Self {
        Self { admin_ids }
    }

    /// Indica se o usuário pode enviar a licença da venda: somente compositor da guia
    /// da venda pode; administrador e comprador não podem.
    ///
    /// Não modifica seus argumentos nem a instância.
    ///
    /// # Arguments
    /// * `venda` - Venda cuja guia é consultada.
    /// * `user_id` - Identificador do usuário autenticado; `None` representa chamada anônima.
    ///
    /// # Returns
    /// `true` se `user_id` é compositor da guia de `venda`; `false` caso contrário,
    /// inclusive quando `user_id` é `None`.
    pub fn can_upload(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        Self::is_compositor(venda, user_id)
    }

    /// Indica se o usuário mantém acesso à licença de uma venda cancelada: administrador
    /// e compositor da guia mantêm; o comprador perde.
    ///
    /// Para venda não cancelada aplica a mesma regra de [`Self::can_access`]. Não
    /// modifica seus argumentos nem a instância.
    ///
    /// # Arguments
    /// * `venda` - Venda cujo estado de cancelamento e cuja guia são consultados.
    /// * `user_id` - Identificador do usuário autenticado; `None` representa chamada anônima.
    ///
    /// # Returns
    /// `true` se o usuário tem acesso; `false` caso contrário, inclusive quando
    /// `user_id` é `None`.
    pub fn can_access_after_cancel(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        if !venda.cancelada {
            return self.can_access(venda, user_id);
        }
        let Some(user_id) = user_id else {
            return false;
        };
        self.is_admin(user_id) || Self::is_compositor(venda, user_id)
    }

    /// Garante que o usuário pode enviar a licença da venda, conforme [`Self::can_upload`].
    ///
    /// Não modifica seus argumentos nem a instância.
    ///
    /// # Arguments
    /// * `venda` - Venda cuja guia é consultada.
    /// * `user_id` - Identificador do usuário autenticado; `None` representa chamada anônima.
    ///
    /// # Errors
    /// Devolve [`UploadNaoPermitido`] quando `can_upload` é falso para os argumentos
    /// recebidos.
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
