use std::collections::HashMap;
use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Item {
    pub sku: String,
    pub quantidade: i64,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Pedido {
    pub linhas: Vec<Item>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ErroEstoque {
    LimiteInvalido,
    QuantidadeInvalida,
    LimiteExcedido,
    EstoqueInsuficiente,
}

impl fmt::Display for ErroEstoque {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let msg = match self {
            ErroEstoque::LimiteInvalido => "limite por sku deve ser maior que zero",
            ErroEstoque::QuantidadeInvalida => "quantidade deve ser maior que zero",
            ErroEstoque::LimiteExcedido => "saldo resultante excede o limite por sku",
            ErroEstoque::EstoqueInsuficiente => "estoque insuficiente",
        };
        f.write_str(msg)
    }
}

impl std::error::Error for ErroEstoque {}

#[derive(Debug)]
pub struct Estoque {
    limite_por_sku: i64,
    saldos: HashMap<String, i64>,
}

impl Estoque {
    pub fn new(limite_por_sku: i64) -> Result<Self, ErroEstoque> {
        if limite_por_sku <= 0 {
            return Err(ErroEstoque::LimiteInvalido);
        }
        Ok(Self {
            limite_por_sku,
            saldos: HashMap::new(),
        })
    }

    pub fn repor(&mut self, sku: &str, quantidade: i64) -> Result<(), ErroEstoque> {
        if quantidade <= 0 {
            return Err(ErroEstoque::QuantidadeInvalida);
        }
        let novo_saldo = self
            .quantidade(sku)
            .checked_add(quantidade)
            .filter(|saldo| *saldo <= self.limite_por_sku)
            .ok_or(ErroEstoque::LimiteExcedido)?;
        self.saldos.insert(sku.to_string(), novo_saldo);
        Ok(())
    }

    pub fn quantidade(&self, sku: &str) -> i64 {
        self.saldos.get(sku).copied().unwrap_or(0)
    }

    /// Processa os itens em ordem. No primeiro erro, para; os itens anteriores
    /// permanecem debitados e presentes em `pedido.linhas`.
    pub fn reservar(&mut self, itens: &[Item], pedido: &mut Pedido) -> Result<(), ErroEstoque> {
        for item in itens {
            if item.quantidade <= 0 {
                return Err(ErroEstoque::QuantidadeInvalida);
            }
            let saldo = self.quantidade(&item.sku);
            if saldo < item.quantidade {
                return Err(ErroEstoque::EstoqueInsuficiente);
            }
            self.saldos.insert(item.sku.clone(), saldo - item.quantidade);
            pedido.linhas.push(item.clone());
        }
        Ok(())
    }
}

/// Altera a lista no lugar: apara espaços, converte para maiúsculas e remove
/// os vazios. Devolve quantos foram removidos.
pub fn normalizar_skus(skus: &mut Vec<String>) -> usize {
    let antes = skus.len();
    for sku in skus.iter_mut() {
        *sku = sku.trim().to_uppercase();
    }
    skus.retain(|sku| !sku.is_empty());
    antes - skus.len()
}
