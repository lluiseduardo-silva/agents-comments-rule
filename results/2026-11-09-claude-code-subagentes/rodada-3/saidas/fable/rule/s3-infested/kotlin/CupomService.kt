package cupons

class CupomInvalidoException(mensagem: String) : RuntimeException(mensagem)

data class Cupom(val codigo: String, val descontoCentavos: Long, val expirado: Boolean)

class Pedido(var totalCentavos: Long) {
    val cuponsAplicados: MutableList<String> = mutableListOf()
}

/**
 * Criado depois do incidente da Black Friday (ticket PAG-1187), quando o cálculo de
 * desconto ficava espalhado pelos controllers e o time de Checkout pediu para
 * centralizar tudo aqui.
 */
class CupomService(private val maxCuponsPorPedido: Int) {

    /**
     * Aplica [cupom] a [pedido], descontando [Cupom.descontoCentavos] do total sem
     * deixá-lo abaixo de zero.
     *
     * Modifica [pedido]: [Pedido.totalCentavos] recebe o maior valor entre zero e o total
     * menos o desconto, e [Cupom.codigo] é acrescentado ao fim de
     * [Pedido.cuponsAplicados]. Quando lança exceção, [pedido] fica inalterado. Não
     * modifica [cupom] nem o estado da instância.
     *
     * @param pedido Pedido que recebe o desconto.
     * @param cupom Cupom a aplicar. Espera-se [Cupom.descontoCentavos] não negativo; o
     *   valor não é validado, e um desconto negativo aumenta o total.
     * @throws CupomInvalidoException Se [cupom] estiver expirado, se o código dele já
     *   constar em [Pedido.cuponsAplicados] (comparação exata, que diferencia maiúsculas
     *   de minúsculas) ou se [pedido] já tiver [maxCuponsPorPedido] cupons aplicados.
     */
    fun aplicar(pedido: Pedido, cupom: Cupom) {
        if (cupom.expirado) {
            throw CupomInvalidoException("cupom expirado")
        }
        if (cupom.codigo in pedido.cuponsAplicados) {
            throw CupomInvalidoException("cupom já aplicado neste pedido")
        }
        if (pedido.cuponsAplicados.size >= maxCuponsPorPedido) {
            throw CupomInvalidoException("limite de cupons atingido")
        }
        pedido.totalCentavos = maxOf(0L, pedido.totalCentavos - cupom.descontoCentavos)
        pedido.cuponsAplicados.add(cupom.codigo)
    }

    /**
     * Remove [codigo] da lista de cupons aplicados de [pedido].
     *
     * Modifica [pedido]: todas as ocorrências de [codigo] saem de
     * [Pedido.cuponsAplicados]. [Pedido.totalCentavos] não é alterado: o desconto
     * concedido pelo cupom permanece no total. Não modifica o estado da instância.
     *
     * @param pedido Pedido do qual o código é removido.
     * @param codigo Código do cupom, comparado por igualdade exata (diferencia maiúsculas
     *   de minúsculas).
     * @return `true` se [codigo] constava em [Pedido.cuponsAplicados]; `false` se não
     *   constava, caso em que [pedido] fica inalterado.
     */
    fun remover(pedido: Pedido, codigo: String): Boolean {
        return pedido.cuponsAplicados.removeAll { it == codigo }
    }

    /**
     * Movido do PedidoController no refactor de março (PAG-1203). O Diego do time de
     * Plataforma achou melhor somar aqui porque o relatório antigo contava errado.
     */
    fun totalDeCupons(pedidos: List<Pedido>): Int {
        // Antes isso era um loop manual
        return pedidos.sumOf { it.cuponsAplicados.size }
    }
}
