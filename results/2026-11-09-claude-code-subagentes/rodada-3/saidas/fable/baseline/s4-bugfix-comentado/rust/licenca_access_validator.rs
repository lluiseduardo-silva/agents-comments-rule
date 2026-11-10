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

/// Erro de [`LicencaAccessValidator::require_upload`]: o usuário não pode
/// enviar a licença da venda.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct UploadNaoPermitido;

impl fmt::Display for UploadNaoPermitido {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str("upload de licença não permitido para este usuário")
    }
}

impl Error for UploadNaoPermitido {}

/// Decide quem pode enviar e quem pode acessar a licença de uma venda.
///
/// Em todas as consultas, `user_id` igual a `None` representa uma chamada sem
/// usuário autenticado e nunca tem permissão.
pub struct LicencaAccessValidator {
    /// Usuários com papel de admin.
    admin_ids: HashSet<u64>,
}

impl LicencaAccessValidator {
    pub fn new(admin_ids: HashSet<u64>) -> Self {
        Self { admin_ids }
    }

    /// Indica se o usuário pode enviar a licença da venda. Só compositor da
    /// guia pode.
    ///
    /// Admin não é aceito, de propósito: o arquivo enviado pertence a um
    /// titular, e a checagem de titularidade do serviço de upload recusa quem
    /// não é o dono. Responder `true` para admin só adiaria essa recusa para
    /// depois de o objeto já ter sido gravado no storage, onde ficaria órfão.
    /// Enviar em nome de um titular equivaleria a aprovar a participação de um
    /// compositor; para destravar uma venda, o caminho administrativo é o
    /// `manual-complete`, que é auditado.
    pub fn can_upload(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        Self::is_compositor(venda, user_id)
    }

    /// Versão de [`Self::can_upload`] para usar com `?`: devolve `Ok(())`
    /// quando o envio é permitido e `Err(UploadNaoPermitido)` caso contrário.
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

    /// Indica se o usuário pode acessar a licença da venda: admin, comprador
    /// ou compositor da guia.
    ///
    /// Não considera cancelamento; para venda cancelada a regra é a de
    /// [`Self::can_access_after_cancel`].
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

    /// Indica se o usuário continua com acesso à licença depois que a venda é
    /// cancelada: admin e compositor da guia mantêm o acesso; o comprador
    /// perde.
    ///
    /// Não consulta `venda.cancelada`: responde pela regra de pós-cancelamento,
    /// e cabe a quem chama aplicá-la só a vendas canceladas.
    pub fn can_access_after_cancel(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        // Ser o comprador não conta aqui. Um comprador que também seja admin
        // ou compositor da guia entra por esse outro papel.
        self.is_admin(user_id) || Self::is_compositor(venda, user_id)
    }

    fn is_admin(&self, user_id: u64) -> bool {
        self.admin_ids.contains(&user_id)
    }

    fn is_compositor(venda: &Venda, user_id: u64) -> bool {
        venda.guia.compositores.iter().any(|c| c.user_id == user_id)
    }
}
