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

/// Erro devolvido por [`LicencaAccessValidator::require_upload`] quando o
/// usuário não pode enviar a licença da venda.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct UploadNaoPermitido;

impl fmt::Display for UploadNaoPermitido {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str("upload de licença não permitido: apenas compositores da guia podem enviar")
    }
}

impl std::error::Error for UploadNaoPermitido {}

/// Regras de quem pode enviar e acessar a licença de uma venda.
pub struct LicencaAccessValidator {
    admin_ids: HashSet<u64>,
}

impl LicencaAccessValidator {
    pub fn new(admin_ids: HashSet<u64>) -> Self {
        Self { admin_ids }
    }

    /// Só um compositor da guia da venda pode enviar a licença.
    ///
    /// Admin não é aceito de propósito: o arquivo pertence a um titular, e a
    /// etapa seguinte do fluxo de upload exige que quem envia seja titular.
    /// Aceitar admin aqui só adiaria a recusa para depois de o arquivo já
    /// ter sido gravado, deixando um objeto órfão no storage. Para destravar
    /// uma venda, o admin usa o caminho administrativo auditado
    /// (`manual-complete`), não o upload.
    pub fn can_upload(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        // Usuário anônimo nunca envia.
        let Some(user_id) = user_id else {
            return false;
        };
        Self::is_compositor(venda, user_id)
    }

    /// Versão impositiva de [`Self::can_upload`]: não devolve nada quando o
    /// upload é permitido e falha com [`UploadNaoPermitido`] caso contrário.
    /// Deve ser chamada antes de qualquer gravação do arquivo, para que uma
    /// recusa não deixe efeitos colaterais.
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

    /// Acesso à licença enquanto a venda está ativa: admin, comprador ou
    /// compositor da guia.
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

    /// Acesso à licença considerando o cancelamento da venda.
    ///
    /// - Venda ativa: mesmas regras de [`Self::can_access`].
    /// - Venda cancelada: admin e compositor da guia mantêm o acesso; o
    ///   comprador perde, porque a compra que lhe dava direito à licença
    ///   deixou de existir.
    pub fn can_access_after_cancel(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        if !venda.cancelada {
            return self.can_access(venda, user_id);
        }
        let Some(user_id) = user_id else {
            return false;
        };
        // O comprador não aparece aqui de propósito. Se ele também for admin
        // ou compositor da guia, o acesso vem desse outro papel.
        self.is_admin(user_id) || Self::is_compositor(venda, user_id)
    }

    fn is_admin(&self, user_id: u64) -> bool {
        self.admin_ids.contains(&user_id)
    }

    fn is_compositor(venda: &Venda, user_id: u64) -> bool {
        venda.guia.compositores.iter().any(|c| c.user_id == user_id)
    }
}
