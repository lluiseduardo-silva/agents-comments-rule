/// Motivos pelos quais um cupom não pode ser aplicado a um pedido.
#[derive(Debug, PartialEq)]
pub enum ErroCupom {
    /// O pedido já tem `max_cupons_por_pedido` cupons aplicados.
    LimiteAtingido,
    /// O cupom está expirado.
    Expirado,
    /// O código do cupom já consta em `cupons_aplicados` do pedido.
    JaAplicado,
}

pub struct Cupom {
    pub codigo: String,
    pub desconto_centavos: i64,
    pub expirado: bool,
}

pub struct Pedido {
    pub total_centavos: i64,
    pub cupons_aplicados: Vec<String>,
}

/// Criado depois do incidente da Black Friday (ticket PAG-1187), quando o cálculo de
/// desconto ficava espalhado pelos handlers e o time de Checkout pediu para
/// centralizar tudo aqui.
pub struct CupomService {
    max_cupons_por_pedido: usize,
}

impl CupomService {
    pub fn new(max_cupons_por_pedido: usize) -> Self {
        Self { max_cupons_por_pedido }
    }

    /// Aplica o cupom ao pedido: subtrai o desconto do total, sem deixá-lo abaixo de zero,
    /// e registra o código em `cupons_aplicados`.
    ///
    /// Modifica `pedido` (`total_centavos` e `cupons_aplicados`) somente em caso de
    /// sucesso; em caso de erro, `pedido` permanece intacto. Não modifica `cupom` nem a
    /// instância.
    ///
    /// # Arguments
    /// * `pedido` - Pedido que recebe o desconto.
    /// * `cupom` - Cupom a aplicar; `desconto_centavos` em centavos.
    ///
    /// # Returns
    /// `Ok(())` quando o cupom foi aplicado.
    ///
    /// # Errors
    /// * [`ErroCupom::Expirado`] se `cupom.expirado` for verdadeiro.
    /// * [`ErroCupom::JaAplicado`] se o código já estiver em `pedido.cupons_aplicados`.
    /// * [`ErroCupom::LimiteAtingido`] se o pedido já tiver `max_cupons_por_pedido` cupons.
    pub fn aplicar(&self, pedido: &mut Pedido, cupom: &Cupom) -> Result<(), ErroCupom> {
        if cupom.expirado {
            return Err(ErroCupom::Expirado);
        }
        if pedido.cupons_aplicados.contains(&cupom.codigo) {
            return Err(ErroCupom::JaAplicado);
        }
        if pedido.cupons_aplicados.len() >= self.max_cupons_por_pedido {
            return Err(ErroCupom::LimiteAtingido);
        }
        pedido.total_centavos = (pedido.total_centavos - cupom.desconto_centavos).max(0);
        pedido.cupons_aplicados.push(cupom.codigo.clone());
        Ok(())
    }

    /// Remove o código de cupom de `cupons_aplicados` do pedido.
    ///
    /// Modifica `pedido.cupons_aplicados` quando o código está presente; não altera
    /// `total_centavos` nem a instância.
    ///
    /// # Arguments
    /// * `pedido` - Pedido de onde o código é removido.
    /// * `codigo` - Código do cupom a remover.
    ///
    /// # Returns
    /// `true` se o código estava em `cupons_aplicados` e foi removido; `false` caso
    /// contrário.
    pub fn remover(&self, pedido: &mut Pedido, codigo: &str) -> bool {
        match pedido.cupons_aplicados.iter().position(|c| c == codigo) {
            Some(indice) => {
                pedido.cupons_aplicados.remove(indice);
                true
            }
            None => false,
        }
    }

    /// Movido do PedidoController no refactor de março (PAG-1203). O Diego do time de
    /// Plataforma achou melhor somar aqui porque o relatório antigo contava errado.
    pub fn total_de_cupons(&self, pedidos: &[Pedido]) -> usize {
        // Antes isso era um loop manual
        pedidos.iter().map(|p| p.cupons_aplicados.len()).sum()
    }
}
