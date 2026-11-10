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
     * Aplica [cupom] a [pedido]: um cupom expirado, repetido no pedido ou além do limite
     * de cupons por pedido é rejeitado, e o total nunca fica abaixo de zero.
     *
     * Modifica [pedido]: subtrai o desconto de `totalCentavos` (travando em zero) e
     * acrescenta o código a `cuponsAplicados`. Não modifica [cupom] nem o estado da
     * instância. Se lançar exceção, [pedido] permanece inalterado. Não é seguro para
     * chamadas concorrentes sobre o mesmo pedido.
     *
     * @param pedido Pedido que recebe o cupom.
     * @param cupom Cupom a aplicar; `descontoCentavos` em centavos.
     * @throws CupomInvalidoException Se o cupom estiver expirado, se o código já estiver
     * em `cuponsAplicados` ou se `cuponsAplicados` já tiver `maxCuponsPorPedido` itens.
     */
    fun aplicar(pedido: Pedido, cupom: Cupom) {
        if (cupom.expirado) {
            throw CupomInvalidoException("cupom expirado")
        }
        if (cupom.codigo in pedido.cuponsAplicados) {
            throw CupomInvalidoException("cupom já aplicado ao pedido")
        }
        if (pedido.cuponsAplicados.size >= maxCuponsPorPedido) {
            throw CupomInvalidoException("limite de cupons atingido")
        }
        pedido.totalCentavos = maxOf(0L, pedido.totalCentavos - cupom.descontoCentavos)
        pedido.cuponsAplicados.add(cupom.codigo)
    }

    /**
     * Remove [codigo] dos cupons aplicados a [pedido] e informa se ele estava presente.
     *
     * Modifica [pedido]: retira o código de `cuponsAplicados`; não altera
     * `totalCentavos`. Não modifica o estado da instância.
     *
     * @param pedido Pedido de onde o cupom é removido.
     * @param codigo Código do cupom a remover.
     * @return `true` se o código estava em `cuponsAplicados` e foi removido; `false` se
     * não estava (nada é alterado).
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
