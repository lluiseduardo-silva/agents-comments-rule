data class ItemEstoque(val sku: String, val quantidade: Int)

class Pedido {
    val linhas: MutableList<ItemEstoque> = mutableListOf()
}

class QuantidadeInvalidaException(val quantidade: Int) :
    IllegalArgumentException("Quantidade invalida: $quantidade")

class EstoqueInsuficienteException(val sku: String, val solicitado: Int, val disponivel: Int) :
    IllegalStateException("Estoque insuficiente para $sku: solicitado $solicitado, disponivel $disponivel")

class LimiteExcedidoException(val sku: String, val saldoResultante: Int, val limite: Int) :
    IllegalStateException("Saldo de $sku ($saldoResultante) excede o limite por sku ($limite)")

class Estoque(private val limitePorSku: Int) {
    private val saldos = mutableMapOf<String, Int>()

    // Todas as operacoes sao "ler, decidir, gravar"; um unico lock cobre as tres etapas.
    private val trava = Any()

    init {
        require(limitePorSku > 0) { "limitePorSku deve ser maior que zero: $limitePorSku" }
    }

    fun repor(sku: String, quantidade: Int) {
        if (quantidade <= 0) throw QuantidadeInvalidaException(quantidade)
        synchronized(trava) {
            // Long evita overflow na soma; o saldo so e gravado depois da validacao.
            val novoSaldo = (saldos[sku] ?: 0).toLong() + quantidade
            if (novoSaldo > limitePorSku) {
                throw LimiteExcedidoException(sku, novoSaldo.coerceAtMost(Int.MAX_VALUE.toLong()).toInt(), limitePorSku)
            }
            saldos[sku] = novoSaldo.toInt()
        }
    }

    fun quantidade(sku: String): Int = synchronized(trava) { saldos[sku] ?: 0 }

    /**
     * Reserva os itens em ordem. No primeiro erro a operacao para; os itens
     * anteriores continuam debitados e continuam em [pedido].linhas.
     */
    fun reservar(itens: List<ItemEstoque>, pedido: Pedido) {
        synchronized(trava) {
            for (item in itens) {
                if (item.quantidade <= 0) throw QuantidadeInvalidaException(item.quantidade)
                val saldo = saldos[item.sku] ?: 0
                if (saldo < item.quantidade) {
                    throw EstoqueInsuficienteException(item.sku, item.quantidade, saldo)
                }
                saldos[item.sku] = saldo - item.quantidade
                pedido.linhas.add(item)
            }
        }
    }

    /** Altera [skus] no lugar e devolve quantos itens vazios foram removidos. */
    fun normalizarSkus(skus: MutableList<String>): Int {
        val tamanhoOriginal = skus.size
        val normalizados = skus.map { it.trim().uppercase() }.filter { it.isNotEmpty() }
        skus.clear()
        skus.addAll(normalizados)
        return tamanhoOriginal - skus.size
    }
}
