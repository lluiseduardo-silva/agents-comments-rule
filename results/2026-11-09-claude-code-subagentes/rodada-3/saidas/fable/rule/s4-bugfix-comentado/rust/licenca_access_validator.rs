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

/// Erro que indica que um usuário não tem permissão para enviar a licença de uma venda.
///
/// Ocorre quando não há usuário identificado ou quando o usuário não é compositor da
/// guia da venda.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UploadNaoPermitido {
    /// Identificador da venda cuja licença não pôde ser enviada.
    pub venda_id: u64,
    /// Usuário que teve o envio recusado; `None` quando não havia usuário identificado.
    pub user_id: Option<u64>,
}

impl fmt::Display for UploadNaoPermitido {
    /// Escreve em `f` a mensagem do erro, que cita a venda e, quando identificado, o
    /// usuário.
    ///
    /// Modifica apenas `f`, que recebe o texto. Não modifica a instância.
    ///
    /// # Arguments
    ///
    /// * `f` - Destino da mensagem formatada.
    ///
    /// # Errors
    ///
    /// Devolve [`fmt::Error`] quando a escrita em `f` falha; nesse caso `f` pode ter
    /// recebido parte da mensagem.
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self.user_id {
            Some(user_id) => write!(
                f,
                "usuário {} não pode enviar a licença da venda {}",
                user_id, self.venda_id
            ),
            None => write!(
                f,
                "usuário não identificado não pode enviar a licença da venda {}",
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

    /// Indica se `user_id` pode enviar a licença de `venda`: somente um compositor da guia
    /// da venda pode enviar.
    ///
    /// Ser administrador não concede o envio; um administrador só é aceito quando também é
    /// compositor da guia.
    ///
    /// Não modifica os argumentos nem a instância.
    ///
    /// # Arguments
    ///
    /// * `venda` - Venda cuja licença seria enviada; a decisão usa os compositores de
    ///   `venda.guia`.
    /// * `user_id` - Usuário que tenta o envio; `None` significa que não há usuário
    ///   identificado.
    ///
    /// # Returns
    ///
    /// `true` quando `user_id` é compositor da guia da venda; `false` nos demais casos,
    /// inclusive quando `user_id` é `None`.
    pub fn can_upload(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        Self::is_compositor(venda, user_id)
    }

    /// Exige que `user_id` possa enviar a licença de `venda`, pela regra de
    /// [`Self::can_upload`].
    ///
    /// Não modifica os argumentos nem a instância.
    ///
    /// # Arguments
    ///
    /// * `venda` - Venda cuja licença seria enviada.
    /// * `user_id` - Usuário que tenta o envio; `None` significa que não há usuário
    ///   identificado e sempre é recusado.
    ///
    /// # Returns
    ///
    /// `Ok(())` quando o envio é permitido.
    ///
    /// # Errors
    ///
    /// Devolve [`UploadNaoPermitido`], com o identificador da venda e o `user_id` recebido,
    /// quando [`Self::can_upload`] é falso: usuário ausente ou que não é compositor da guia
    /// da venda.
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

    /// Indica se `user_id` tem acesso à licença de `venda` depois do cancelamento da venda:
    /// administradores e compositores da guia mantêm o acesso, e o comprador o perde.
    ///
    /// O comprador só é aceito quando também é administrador ou compositor da guia. A regra
    /// é aplicada a qualquer `venda` recebida, sem consultar `venda.cancelada`; o chamador
    /// deve usar esta função apenas para venda cancelada e [`Self::can_access`] para as
    /// demais.
    ///
    /// Não modifica os argumentos nem a instância.
    ///
    /// # Arguments
    ///
    /// * `venda` - Venda cancelada cujo acesso é avaliado; a decisão usa os compositores de
    ///   `venda.guia`.
    /// * `user_id` - Usuário que pede o acesso; `None` significa que não há usuário
    ///   identificado.
    ///
    /// # Returns
    ///
    /// `true` quando `user_id` é administrador ou compositor da guia da venda; `false` nos
    /// demais casos, inclusive para o comprador que não é nenhum dos dois e quando
    /// `user_id` é `None`.
    pub fn can_access_after_cancel(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        if self.is_admin(user_id) {
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
