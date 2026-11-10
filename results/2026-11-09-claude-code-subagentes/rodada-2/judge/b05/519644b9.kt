/**
 * Item de uma reserva: a quantidade pedida de um sku.
 *
 * @property sku Identificador do produto.
 * @property quantidade Quantidade pedida; só é validada em [Estoque.reservar].
 */
data class ItemReserva(val sku: String, val quantidade: Int)

/**
 * Pedido em construção, acumulando as linhas reservadas no estoque.
 *
 * @property linhas Itens já reservados, na ordem em que foram reservados.
 */
class Pedido {
    val linhas: MutableList<ItemReserva> = mutableListOf()
}

/**
 * Erro de [Estoque.reservar] quando a quantidade de um item é menor ou igual a zero.
 *
 * @constructor Cria o erro com a mensagem descrevendo o item inválido.
 */
class QuantidadeInvalidaException(mensagem: String) : IllegalArgumentException(mensagem)

/**
 * Erro de [Estoque.reservar] quando o saldo de um sku é menor que a quantidade pedida.
 *
 * @constructor Cria o erro com a mensagem descrevendo o sku e os valores envolvidos.
 */
class EstoqueInsuficienteException(mensagem: String) : IllegalStateException(mensagem)

/**
 * Controle de estoque em memória, com saldo por sku limitado a [limitePorSku].
 *
 * Não é seguro para uso concorrente: o acesso por várias threads exige sincronização
 * externa.
 *
 * @property limitePorSku Saldo máximo permitido para cada sku; sempre maior que zero.
 * @constructor Cria um estoque vazio.
 * @throws IllegalArgumentException Se [limitePorSku] for menor ou igual a zero.
 */
class Estoque(val limitePorSku: Int) {

    private val saldos: MutableMap<String, Int> = mutableMapOf()

    init {
        require(limitePorSku > 0) { "limitePorSku deve ser maior que zero: $limitePorSku" }
    }

    /**
     * Soma [quantidade] ao saldo de [sku].
     *
     * Modifica o saldo de [sku] nesta instância; se falhar, nenhum saldo é alterado.
     *
     * @param sku Identificador do produto; criado com saldo zero se ainda não existir.
     * @param quantidade Quantidade a somar; deve ser maior que zero.
     * @throws IllegalArgumentException Se [quantidade] for menor ou igual a zero.
     * @throws IllegalStateException Se o saldo resultante ultrapassar [limitePorSku].
     */
    fun repor(sku: String, quantidade: Int) {
        require(quantidade > 0) { "quantidade deve ser maior que zero: $quantidade" }
        val novoSaldo = quantidade(sku).toLong() + quantidade
        check(novoSaldo <= limitePorSku) {
            "saldo de $sku ultrapassaria o limite $limitePorSku: $novoSaldo"
        }
        saldos[sku] = novoSaldo.toInt()
    }

    /**
     * Devolve o saldo atual de [sku].
     *
     * Não modifica seus argumentos nem a instância.
     *
     * @param sku Identificador do produto.
     * @return Saldo de [sku]; zero se o sku não existir.
     */
    fun quantidade(sku: String): Int = saldos[sku] ?: 0

    /**
     * Reserva cada item de [itens], na ordem, debitando o saldo e registrando-o em
     * [pedido].
     *
     * Modifica o saldo desta instância e [pedido]`.linhas`; não modifica [itens]. A
     * operação para no primeiro erro, e os itens anteriores permanecem debitados e
     * presentes em [pedido]`.linhas`; o item que falhou não é debitado nem acrescentado.
     *
     * @param itens Itens a reservar, processados na ordem da lista.
     * @param pedido Pedido que recebe uma linha por item reservado.
     * @throws QuantidadeInvalidaException Se a quantidade de um item for menor ou igual a
     * zero.
     * @throws EstoqueInsuficienteException Se o saldo do sku de um item for menor que a
     * quantidade pedida.
     */
    fun reservar(itens: List<ItemReserva>, pedido: Pedido) {
        for (item in itens) {
            if (item.quantidade <= 0) {
                throw QuantidadeInvalidaException(
                    "quantidade inválida para ${item.sku}: ${item.quantidade}"
                )
            }
            val saldo = quantidade(item.sku)
            if (saldo < item.quantidade) {
                throw EstoqueInsuficienteException(
                    "estoque insuficiente para ${item.sku}: saldo $saldo, pedido ${item.quantidade}"
                )
            }
            saldos[item.sku] = saldo - item.quantidade
            pedido.linhas.add(item)
        }
    }

    /**
     * Normaliza [skus] no lugar: remove espaços das pontas, converte para maiúsculas e
     * descarta os textos que ficarem vazios.
     *
     * Modifica [skus] in-place, preservando a ordem dos que restam. Não modifica o
     * estoque.
     *
     * @param skus Lista mutável de textos a normalizar.
     * @return Quantidade de elementos removidos por ficarem vazios.
     */
    fun normalizarSkus(skus: MutableList<String>): Int {
        val normalizados = skus.map { it.trim().uppercase() }.filter { it.isNotEmpty() }
        val removidos = skus.size - normalizados.size
        skus.clear()
        skus.addAll(normalizados)
        return removidos
    }
}
