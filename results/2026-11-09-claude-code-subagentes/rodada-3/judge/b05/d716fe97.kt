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
     * Aplica [cupom] a [pedido], abatendo o desconto do total sem deixá-lo abaixo de zero.
     *
     * Modifica [pedido]: subtrai [Cupom.descontoCentavos] de [Pedido.totalCentavos]
     * (travando em zero) e acrescenta [Cupom.codigo] a [Pedido.cuponsAplicados]. Quando
     * lança exceção, [pedido] não é alterado. Não modifica [cupom] nem o estado da
     * instância.
     *
     * @param pedido Pedido que recebe o desconto.
     * @param cupom Cupom a aplicar.
     * @throws CupomInvalidoException Se [cupom] estiver expirado, se o mesmo código já
     * estiver em [Pedido.cuponsAplicados] ou se o pedido já tiver `maxCuponsPorPedido`
     * cupons aplicados.
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
        pedido.totalCentavos = (pedido.totalCentavos - cupom.descontoCentavos).coerceAtLeast(0L)
        pedido.cuponsAplicados.add(cupom.codigo)
    }

    /**
     * Remove o código [codigo] dos cupons aplicados a [pedido].
     *
     * Modifica [Pedido.cuponsAplicados] de [pedido], retirando a primeira ocorrência de
     * [codigo]. Não altera [Pedido.totalCentavos] nem o estado da instância.
     *
     * @param pedido Pedido do qual o cupom é removido.
     * @param codigo Código do cupom a remover.
     * @return `true` se [codigo] estava aplicado e foi removido; `false` se não estava, caso
     * em que [pedido] não é alterado.
     */
    fun remover(pedido: Pedido, codigo: String): Boolean {
        return pedido.cuponsAplicados.remove(codigo)
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
