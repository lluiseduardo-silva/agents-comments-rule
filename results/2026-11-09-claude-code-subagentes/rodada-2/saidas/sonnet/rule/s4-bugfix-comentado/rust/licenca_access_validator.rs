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

/// Erro devolvido quando o usuário não tem permissão para enviar a licença da venda.
///
/// Não carrega dados; o construtor apenas cria o valor e não falha.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct UploadNaoPermitido;

impl std::fmt::Display for UploadNaoPermitido {
    /// Escreve a mensagem do erro em `f`. Não modifica a instância.
    ///
    /// # Errors
    /// Propaga o erro de escrita de `f`.
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

    /// Indica se o usuário pode enviar a licença da venda: somente compositor da guia.
    ///
    /// Administrador não envia licença. Não modifica os argumentos nem a instância.
    ///
    /// # Arguments
    /// * `venda` - Venda cuja guia define os compositores autorizados.
    /// * `user_id` - Id do usuário autenticado; `None` representa chamada anônima.
    ///
    /// # Returns
    /// `true` se `user_id` é compositor da guia da venda; `false` para anônimo,
    /// administrador que não seja compositor, comprador e demais usuários.
    pub fn can_upload(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        Self::is_compositor(venda, user_id)
    }

    /// Exige permissão de envio da licença, falhando quando `can_upload` é falso.
    ///
    /// Não modifica os argumentos nem a instância.
    ///
    /// # Arguments
    /// * `venda` - Venda cuja guia define os compositores autorizados.
    /// * `user_id` - Id do usuário autenticado; `None` representa chamada anônima.
    ///
    /// # Errors
    /// Retorna [`UploadNaoPermitido`] quando `can_upload(venda, user_id)` é `false`.
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

    /// Indica se o usuário mantém acesso à licença depois que a venda é cancelada:
    /// administrador e compositor da guia mantêm; o comprador perde.
    ///
    /// Se a venda não está cancelada, aplica as regras de `can_access`. Não modifica
    /// os argumentos nem a instância.
    ///
    /// # Arguments
    /// * `venda` - Venda cujo estado de cancelamento e guia são consultados.
    /// * `user_id` - Id do usuário autenticado; `None` representa chamada anônima.
    ///
    /// # Returns
    /// Para venda cancelada, `true` se `user_id` é administrador ou compositor da
    /// guia; `false` para anônimo, comprador e demais usuários. Para venda não
    /// cancelada, o resultado de `can_access`.
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
