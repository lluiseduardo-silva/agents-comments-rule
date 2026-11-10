use std::collections::HashSet;
use std::fmt;

/// Erro de `require_upload`: o usuário não pode enviar a licença desta venda.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UploadNaoPermitido {
    pub venda_id: u64,
    /// `None` quando a chamada não estava autenticada.
    pub user_id: Option<u64>,
}

impl fmt::Display for UploadNaoPermitido {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self.user_id {
            Some(id) => write!(
                f,
                "usuário {id} não pode enviar licença da venda {}",
                self.venda_id
            ),
            None => write!(
                f,
                "usuário não autenticado não pode enviar licença da venda {}",
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

    /// Só um compositor da guia pode enviar a licença.
    ///
    /// Admin não é aceito de propósito: o arquivo enviado pertence a um
    /// titular, e o serviço de upload exige que quem confirma seja o dono do
    /// arquivo. Liberar o admin aqui não habilita nada; a confirmação falha
    /// depois e o objeto já gravado no storage fica órfão. Permitir upload
    /// em nome de outro usuário daria ao admin o poder de aprovar a
    /// participação de um compositor. Para destravar uma venda, o caminho
    /// administrativo é o `manual-complete`, que é auditado.
    pub fn can_upload(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        Self::is_compositor(venda, user_id)
    }

    /// Versão de `can_upload` que falha em vez de devolver `false`, para quem
    /// precisa barrar a operação antes de gravar qualquer coisa no storage.
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

    /// Acesso a uma venda cancelada: admin e compositores da guia mantêm o
    /// acesso; o comprador perde.
    ///
    /// Se a venda não estiver cancelada, vale a regra normal de `can_access`.
    pub fn can_access_after_cancel(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        if !venda.cancelada {
            return self.can_access(venda, user_id);
        }
        let Some(user_id) = user_id else {
            return false;
        };
        // Testado antes do comprador: um admin ou compositor que também seja
        // o comprador continua com acesso pelo outro papel.
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
