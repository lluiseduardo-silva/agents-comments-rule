#[derive(Debug, PartialEq)]
pub enum ErroCupom {
    LimiteAtingido,
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

    /// ⚠ **NÃO remover o limite.** Antes do PR 2291 dava para empilhar cupom à vontade e
    /// o Financeiro reclamou do prejuízo em novembro. A Carla decidiu travar pelo
    /// `max_cupons_por_pedido` em vez de validar no front, que era a outra opção discutida.
    pub fn aplicar(&self, pedido: &mut Pedido, cupom: &Cupom) -> Result<(), ErroCupom> {
        // Limite pedido pelo Financeiro
        if pedido.cupons_aplicados.len() >= self.max_cupons_por_pedido {
            return Err(ErroCupom::LimiteAtingido);
        }
        pedido.total_centavos -= cupom.desconto_centavos;
        pedido.cupons_aplicados.push(cupom.codigo.clone());
        Ok(())
    }

    /// Movido do PedidoController no refactor de março (PAG-1203). O Diego do time de
    /// Plataforma achou melhor somar aqui porque o relatório antigo contava errado.
    pub fn total_de_cupons(&self, pedidos: &[Pedido]) -> usize {
        // Antes isso era um loop manual
        pedidos.iter().map(|p| p.cupons_aplicados.len()).sum()
    }
}
