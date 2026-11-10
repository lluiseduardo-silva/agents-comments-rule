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

/// Erro devolvido quando o usuário não tem permissão para enviar a licença de uma venda.
///
/// Não possui campos; é construído diretamente e não pode falhar.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct UploadNaoPermitido;

impl std::fmt::Display for UploadNaoPermitido {
    /// Escreve a mensagem do erro no formatador.
    ///
    /// Modifica apenas `f`; não modifica a instância.
    ///
    /// # Errors
    /// Propaga o erro de escrita de `f`.
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "usuário não pode enviar a licença desta venda")
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

    /// Indica se o usuário pode enviar a licença da venda: somente compositores da guia
    /// têm essa permissão; administradores e o comprador não.
    ///
    /// Não modifica seus argumentos nem a instância.
    ///
    /// # Arguments
    /// * `venda` - Venda cuja guia é consultada.
    /// * `user_id` - Usuário que tenta enviar; `None` representa uma chamada sem
    ///   usuário autenticado.
    ///
    /// # Returns
    /// `true` se `user_id` é compositor da guia da venda; `false` caso contrário,
    /// inclusive quando `user_id` é `None`.
    pub fn can_upload(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        Self::is_compositor(venda, user_id)
    }

    /// Indica se o usuário mantém acesso à licença de uma venda cancelada: administradores
    /// e compositores da guia mantêm o acesso; o comprador o perde.
    ///
    /// Não modifica seus argumentos nem a instância.
    ///
    /// # Arguments
    /// * `venda` - Venda consultada.
    /// * `user_id` - Usuário que tenta acessar; `None` representa uma chamada sem
    ///   usuário autenticado.
    ///
    /// # Returns
    /// `true` se `user_id` é administrador ou compositor da guia; `false` caso contrário,
    /// inclusive para o comprador e quando `user_id` é `None`. Se a venda não está
    /// cancelada, o resultado é o de [`Self::can_access`].
    pub fn can_access_after_cancel(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        if !venda.cancelada {
            return self.can_access(venda, user_id);
        }
        let Some(user_id) = user_id else {
            return false;
        };
        self.is_admin(user_id) || Self::is_compositor(venda, user_id)
    }

    /// Exige que o usuário possa enviar a licença da venda, conforme [`Self::can_upload`].
    ///
    /// Não modifica seus argumentos nem a instância.
    ///
    /// # Arguments
    /// * `venda` - Venda cuja guia é consultada.
    /// * `user_id` - Usuário que tenta enviar; `None` representa uma chamada sem
    ///   usuário autenticado.
    ///
    /// # Errors
    /// Devolve [`UploadNaoPermitido`] quando [`Self::can_upload`] é `false` para
    /// `venda` e `user_id`.
    pub fn require_upload(&self, venda: &Venda, user_id: Option<u64>) -> Result<(), UploadNaoPermitido> {
        if self.can_upload(venda, user_id) {
            Ok(())
        } else {
            Err(UploadNaoPermitido)
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
