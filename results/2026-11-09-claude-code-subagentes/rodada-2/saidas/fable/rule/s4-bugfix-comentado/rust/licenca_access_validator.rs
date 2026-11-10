use std::collections::HashSet;
use std::error::Error;
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

/// Recusa de envio de licença: o usuário informado não é compositor da guia da venda.
///
/// Ocorre quando [`LicencaAccessValidator::require_upload`] é chamado com um usuário
/// para o qual [`LicencaAccessValidator::can_upload`] devolve `false`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UploadNaoPermitido {
    /// Identificador da venda cuja licença o usuário tentou enviar.
    pub venda_id: u64,
    /// Identificador do usuário recusado; `None` quando não havia usuário autenticado.
    pub user_id: Option<u64>,
}

impl fmt::Display for UploadNaoPermitido {
    /// Escreve em `f` a mensagem do erro, com a venda e, quando presente, o usuário
    /// recusado.
    ///
    /// Modifica apenas `f`, acrescentando o texto; não modifica `self`. Se a escrita
    /// falhar no meio, parte da mensagem pode já ter sido escrita em `f`.
    ///
    /// # Arguments
    ///
    /// * `f` - Destino da mensagem formatada.
    ///
    /// # Errors
    ///
    /// Devolve [`fmt::Error`] quando a escrita em `f` falha.
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self.user_id {
            Some(user_id) => write!(
                f,
                "usuário {} não pode enviar a licença da venda {}",
                user_id, self.venda_id
            ),
            None => write!(
                f,
                "usuário não autenticado não pode enviar a licença da venda {}",
                self.venda_id
            ),
        }
    }
}

impl Error for UploadNaoPermitido {}

pub struct LicencaAccessValidator {
    admin_ids: HashSet<u64>,
}

impl LicencaAccessValidator {
    pub fn new(admin_ids: HashSet<u64>) -> Self {
        Self { admin_ids }
    }

    /// Indica se `user_id` pode enviar a licença de `venda`: somente um compositor da
    /// guia da venda pode enviar; ser administrador ou comprador não concede esse
    /// direito.
    ///
    /// Não modifica seus argumentos nem a instância.
    ///
    /// # Arguments
    ///
    /// * `venda` - Venda cuja licença seria enviada; os compositores considerados são
    ///   os de `venda.guia`.
    /// * `user_id` - Identificador do usuário que pede o envio; `None` significa que
    ///   não há usuário autenticado.
    ///
    /// # Returns
    ///
    /// `true` quando `user_id` é o identificador de algum compositor de `venda.guia`;
    /// `false` nos demais casos, inclusive quando `user_id` é `None` ou a guia não tem
    /// compositores.
    pub fn can_upload(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        Self::is_compositor(venda, user_id)
    }

    /// Exige que `user_id` possa enviar a licença de `venda`, pela regra de
    /// [`Self::can_upload`].
    ///
    /// Não modifica seus argumentos nem a instância.
    ///
    /// # Arguments
    ///
    /// * `venda` - Venda cuja licença seria enviada.
    /// * `user_id` - Identificador do usuário que pede o envio; `None` significa que
    ///   não há usuário autenticado e sempre resulta em erro.
    ///
    /// # Returns
    ///
    /// `Ok(())` quando o envio é permitido.
    ///
    /// # Errors
    ///
    /// Devolve [`UploadNaoPermitido`], com `venda.id` e o `user_id` recebido, quando
    /// [`Self::can_upload`] devolve `false` para os mesmos argumentos.
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

    /// Indica se `user_id` mantém o acesso à licença de uma venda cancelada:
    /// administradores e compositores da guia mantêm o acesso; o comprador o perde
    /// quando a venda é cancelada.
    ///
    /// Não modifica seus argumentos nem a instância.
    ///
    /// # Arguments
    ///
    /// * `venda` - Venda cancelada cujo acesso está sendo decidido; os compositores
    ///   considerados são os de `venda.guia`.
    /// * `user_id` - Identificador do usuário que pede o acesso; `None` significa que
    ///   não há usuário autenticado.
    ///
    /// # Returns
    ///
    /// `true` quando `user_id` é administrador ou compositor de `venda.guia`; `false`
    /// nos demais casos, inclusive quando `user_id` é `None` ou é apenas o comprador
    /// da venda.
    ///
    /// # Pré-condições
    ///
    /// `venda.cancelada` deve ser `true`. A função não consulta esse campo, então
    /// devolve o mesmo resultado para uma venda não cancelada; para essas, a regra de
    /// acesso é a de [`Self::can_access`].
    pub fn can_access_after_cancel(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        self.is_admin(user_id) || Self::is_compositor(venda, user_id)
    }

    fn is_admin(&self, user_id: u64) -> bool {
        self.admin_ids.contains(&user_id)
    }

    fn is_compositor(venda: &Venda, user_id: u64) -> bool {
        venda.guia.compositores.iter().any(|c| c.user_id == user_id)
    }
}
