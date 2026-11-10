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

/// Recusa de upload de licença, devolvida por [`LicencaAccessValidator::require_upload`].
///
/// A regra que decide a recusa está em [`LicencaAccessValidator::can_upload`]; este tipo
/// só a sinaliza. Não carrega dados: quem chama já tem a venda e o usuário em mãos para
/// montar a resposta e o log.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct UploadNaoPermitido;

impl fmt::Display for UploadNaoPermitido {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str("upload de licença não permitido para este usuário")
    }
}

impl Error for UploadNaoPermitido {}

/// Decide quem pode enviar e quem pode acessar a licença de uma venda.
pub struct LicencaAccessValidator {
    admin_ids: HashSet<u64>,
}

impl LicencaAccessValidator {
    pub fn new(admin_ids: HashSet<u64>) -> Self {
        Self { admin_ids }
    }

    /// Diz se `user_id` pode enviar o arquivo de licença da venda.
    ///
    /// Só compositor da guia envia; chamada anônima (`None`) nunca envia. Admin não tem
    /// atalho aqui, e isso é intencional:
    ///
    /// - o arquivo pertence a um titular, e o serviço de licença externa recusa quem não
    ///   é titular. Responder `true` para admin seria prometer um upload que falha logo
    ///   adiante, deixando um objeto órfão no storage;
    /// - para o admin enviar de verdade, a confirmação teria de aceitar o compositor como
    ///   parâmetro, o que daria ao admin o poder de aprovar a participação de um
    ///   compositor;
    /// - o caminho administrativo para destravar uma venda é o `manual-complete`, que
    ///   é auditado.
    ///
    /// O que conta é o papel na guia: um admin que também seja compositor dela envia
    /// como compositor.
    pub fn can_upload(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        Self::is_compositor(venda, user_id)
    }

    /// Guarda de entrada do upload: `Ok(())` se `user_id` pode enviar a licença da venda,
    /// `Err(UploadNaoPermitido)` caso contrário.
    ///
    /// A decisão é a de [`Self::can_upload`], sem regra própria, para que o predicado e a
    /// guarda nunca divirjam. Chame antes de qualquer efeito colateral do upload (gravar
    /// o arquivo no storage, por exemplo): recusar depois disso deixa objeto órfão.
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

    /// Regra geral de acesso à licença: admin, comprador da venda ou compositor da guia.
    ///
    /// Não olha o estado da venda. Para venda cancelada a regra é a de
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

    /// Diz se `user_id` continua acessando a licença depois que a venda morreu
    /// (cancelada).
    ///
    /// Admin e compositor da guia mantêm o acesso; o comprador perde. O que conta é o
    /// papel: um comprador que também seja admin ou compositor da guia continua entrando
    /// por esse outro papel. Chamada anônima (`None`) nunca acessa.
    ///
    /// Esta função não consulta `venda.cancelada`: ela responde pela regra da venda
    /// morta, e cabe a quem chama escolher entre ela e [`Self::can_access`] conforme o
    /// estado da venda.
    pub fn can_access_after_cancel(&self, venda: &Venda, user_id: Option<u64>) -> bool {
        let Some(user_id) = user_id else {
            return false;
        };
        // `venda.comprador_id` fica de fora de propósito: é a única diferença em relação
        // a `can_access`.
        self.is_admin(user_id) || Self::is_compositor(venda, user_id)
    }

    fn is_admin(&self, user_id: u64) -> bool {
        self.admin_ids.contains(&user_id)
    }

    fn is_compositor(venda: &Venda, user_id: u64) -> bool {
        venda.guia.compositores.iter().any(|c| c.user_id == user_id)
    }
}
