use std::collections::HashMap;

/// Erros possíveis nas operações de estoque.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ErroEstoque {
    /// O limite por sku informado na criação é menor ou igual a zero.
    LimiteInvalido,
    /// A quantidade informada é menor ou igual a zero.
    QuantidadeInvalida,
    /// A reposição levaria o saldo do sku acima do limite por sku.
    LimiteExcedido,
    /// O saldo do sku é menor que a quantidade pedida.
    EstoqueInsuficiente,
}

/// Item de uma reserva ou linha de um pedido: um sku e a quantidade dele.
///
/// Campos: `sku` é o identificador do produto; `quantidade` é o número de unidades.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Item {
    pub sku: String,
    pub quantidade: i64,
}

/// Pedido que acumula as linhas reservadas.
///
/// Campos: `linhas` contém os itens já reservados, na ordem da reserva.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Pedido {
    pub linhas: Vec<Item>,
}

/// Controle de estoque em memória, com saldo por sku limitado a um máximo.
///
/// Invariante: o saldo de cada sku nunca é negativo nem ultrapassa `limite_por_sku`.
/// Campos privados: `limite_por_sku` é o saldo máximo por sku; `saldos` guarda o saldo
/// de cada sku já movimentado.
#[derive(Debug, Clone)]
pub struct Estoque {
    limite_por_sku: i64,
    saldos: HashMap<String, i64>,
}

impl Estoque {
    /// Cria um estoque vazio com o limite de saldo por sku informado.
    ///
    /// Não modifica estado externo.
    ///
    /// # Arguments
    /// * `limite_por_sku` - Saldo máximo permitido para cada sku; deve ser maior que zero.
    ///
    /// # Returns
    /// O estoque criado, sem nenhum sku.
    ///
    /// # Errors
    /// * `ErroEstoque::LimiteInvalido` - Se `limite_por_sku` for menor ou igual a zero.
    pub fn novo(limite_por_sku: i64) -> Result<Estoque, ErroEstoque> {
        if limite_por_sku <= 0 {
            return Err(ErroEstoque::LimiteInvalido);
        }
        Ok(Estoque {
            limite_por_sku,
            saldos: HashMap::new(),
        })
    }

    /// Soma `quantidade` ao saldo do sku.
    ///
    /// Modifica o saldo do sku na instância (cria o sku se não existir). Em caso de
    /// erro, nada é alterado.
    ///
    /// # Arguments
    /// * `sku` - Identificador do produto.
    /// * `quantidade` - Unidades a adicionar; deve ser maior que zero.
    ///
    /// # Errors
    /// * `ErroEstoque::QuantidadeInvalida` - Se `quantidade` for menor ou igual a zero.
    /// * `ErroEstoque::LimiteExcedido` - Se o saldo resultante ficar acima do limite por sku.
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

    /// Devolve o saldo atual do sku.
    ///
    /// Não modifica seus argumentos nem a instância.
    ///
    /// # Arguments
    /// * `sku` - Identificador do produto.
    ///
    /// # Returns
    /// O saldo do sku; zero se o sku não existir.
    pub fn quantidade(&self, sku: &str) -> i64 {
        self.saldos.get(sku).copied().unwrap_or(0)
    }

    /// Reserva os itens, na ordem, debitando o estoque e acrescentando-os ao pedido.
    ///
    /// Modifica o saldo dos skus na instância e `pedido.linhas`; não modifica `itens`.
    /// A operação para no primeiro erro: os itens anteriores permanecem debitados e
    /// permanecem em `pedido.linhas`, e o item que falhou não altera nenhum dos dois.
    ///
    /// # Arguments
    /// * `itens` - Itens a reservar, processados na ordem da fatia.
    /// * `pedido` - Pedido que recebe uma linha para cada item reservado.
    ///
    /// # Errors
    /// * `ErroEstoque::QuantidadeInvalida` - Se a quantidade de um item for menor ou igual a zero.
    /// * `ErroEstoque::EstoqueInsuficiente` - Se o saldo do sku de um item for menor que a quantidade.
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

/// Normaliza os skus da lista: remove espaços das pontas, converte para maiúsculas e
/// descarta os que ficarem vazios.
///
/// Modifica `skus` no lugar, preservando a ordem dos que restam. Não modifica estado externo.
///
/// # Arguments
/// * `skus` - Lista mutável de textos a normalizar.
///
/// # Returns
/// Quantos elementos foram removidos por ficarem vazios.
pub fn normalizar_skus(skus: &mut Vec<String>) -> usize {
    let antes = skus.len();
    for sku in skus.iter_mut() {
        *sku = sku.trim().to_uppercase();
    }
    skus.retain(|sku| !sku.is_empty());
    antes - skus.len()
}
