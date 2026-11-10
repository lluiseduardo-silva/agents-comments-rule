/**
 * Item de uma reserva: um sku e a quantidade pedida dele.
 *
 * @property sku Identificador do produto.
 * @property quantidade Quantidade pedida; a validação (deve ser maior que zero) ocorre em [Estoque.reservar].
 * @constructor Cria o item sem validar os valores; não modifica nenhum estado externo.
 */
data class ItemReserva(val sku: String, val quantidade: Int)

/**
 * Pedido mutável que acumula as linhas reservadas no [Estoque].
 *
 * @property linhas Itens já reservados para o pedido, na ordem em que foram reservados.
 * @constructor Cria o pedido com a lista de linhas informada (vazia por padrão); não modifica nenhum estado externo.
 */
class Pedido(val linhas: MutableList<ItemReserva> = mutableListOf())

/**
 * Erro de uma reserva cujo item tem quantidade menor ou igual a zero.
 *
 * @constructor Cria o erro com a [message] informada.
 */
class QuantidadeInvalidaException(message: String) : RuntimeException(message)

/**
 * Erro de uma reserva cujo item pede mais do que o saldo disponível do sku.
 *
 * @constructor Cria o erro com a [message] informada.
 */
class EstoqueInsuficienteException(message: String) : RuntimeException(message)

/**
 * Controle de estoque em memória, com saldo por sku limitado a [limitePorSku].
 *
 * Os saldos vivem apenas na instância. Os métodos que leem ou alteram saldos são
 * sincronizados na instância, então a verificação e a alteração de cada operação são
 * atômicas entre threads.
 *
 * @property limitePorSku Maior saldo que um sku pode ter; sempre maior que zero.
 * @constructor Cria um estoque vazio; não modifica nenhum estado externo.
 * @throws IllegalArgumentException Se [limitePorSku] for menor ou igual a zero.
 */
class Estoque(val limitePorSku: Int) {

    private val saldos = mutableMapOf<String, Int>()

    init {
        require(limitePorSku > 0) { "limitePorSku deve ser maior que zero: $limitePorSku" }
    }

    /**
     * Soma [quantidade] ao saldo de [sku].
     *
     * Modifica o saldo de [sku] nesta instância. Se falhar, nenhum saldo é alterado.
     *
     * @param sku Identificador do produto; se ainda não existir, parte de saldo zero.
     * @param quantidade Quantidade a somar; deve ser maior que zero.
     * @throws IllegalArgumentException Se [quantidade] for menor ou igual a zero.
     * @throws IllegalStateException Se o saldo resultante ultrapassar [limitePorSku].
     */
    @Synchronized
    fun repor(sku: String, quantidade: Int) {
        require(quantidade > 0) { "quantidade deve ser maior que zero: $quantidade" }
        val novoSaldo = (saldos[sku] ?: 0).toLong() + quantidade
        check(novoSaldo <= limitePorSku) {
            "saldo de $sku ($novoSaldo) ultrapassa o limite por sku ($limitePorSku)"
        }
        saldos[sku] = novoSaldo.toInt()
    }

    /**
     * Devolve o saldo atual de [sku].
     *
     * Não modifica seus argumentos nem a instância.
     *
     * @param sku Identificador do produto.
     * @return Saldo de [sku]; zero se o sku nunca recebeu reposição.
     */
    @Synchronized
    fun quantidade(sku: String): Int = saldos[sku] ?: 0

    /**
     * Reserva cada item de [itens], na ordem, debitando o saldo e registrando-o em [pedido].
     *
     * Modifica o saldo dos skus reservados nesta instância e acrescenta os itens ao final
     * de `pedido.linhas`; não modifica [itens]. A operação para no primeiro erro: os itens
     * anteriores continuam debitados e continuam em `pedido.linhas`, e o item que falhou
     * e os seguintes não alteram saldo nem pedido.
     *
     * @param itens Itens a reservar, processados na ordem da lista.
     * @param pedido Pedido que recebe uma linha por item reservado.
     * @throws QuantidadeInvalidaException Se a quantidade de algum item for menor ou igual a zero.
     * @throws EstoqueInsuficienteException Se o saldo de algum item for menor que a quantidade pedida.
     */
    @Synchronized
    fun reservar(itens: List<ItemReserva>, pedido: Pedido) {
        for (item in itens) {
            if (item.quantidade <= 0) {
                throw QuantidadeInvalidaException(
                    "quantidade inválida para ${item.sku}: ${item.quantidade}"
                )
            }
            val saldo = saldos[item.sku] ?: 0
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
     * remove os textos que ficarem vazios.
     *
     * Modifica [skus] in-place: os elementos são sobrescritos e os vazios removidos, mantendo
     * a ordem dos demais. Não modifica o estado da instância.
     *
     * @param skus Lista mutável de textos a normalizar.
     * @return Quantidade de elementos removidos por ficarem vazios.
     */
    fun normalizarSkus(skus: MutableList<String>): Int {
        val tamanhoOriginal = skus.size
        for (i in skus.indices) {
            skus[i] = skus[i].trim().uppercase()
        }
        skus.removeAll { it.isEmpty() }
        return tamanhoOriginal - skus.size
    }
}
