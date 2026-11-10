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
     * ⚠ **NÃO remover o limite.** Antes do PR 2291 dava para empilhar cupom à vontade e
     * o Financeiro reclamou do prejuízo em novembro. A Carla decidiu travar pelo
     * `maxCuponsPorPedido` em vez de validar no front, que era a outra opção discutida.
     */
    fun aplicar(pedido: Pedido, cupom: Cupom) {
        // Limite pedido pelo Financeiro
        if (pedido.cuponsAplicados.size >= maxCuponsPorPedido) {
            throw CupomInvalidoException("limite de cupons atingido")
        }
        if (cupom.expirado) {
            throw CupomInvalidoException("cupom expirado")
        }
        if (cupom.codigo in pedido.cuponsAplicados) {
            throw CupomInvalidoException("cupom já aplicado neste pedido")
        }
        pedido.totalCentavos = maxOf(0L, pedido.totalCentavos - cupom.descontoCentavos)
        pedido.cuponsAplicados.add(cupom.codigo)
    }

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
