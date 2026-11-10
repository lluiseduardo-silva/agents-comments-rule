package licencas

data class Compositor(val userId: Long)

data class Guia(val compositores: List<Compositor>)

data class Venda(
    val id: Long,
    val compradorId: Long,
    val guia: Guia,
    val cancelada: Boolean,
)

/**
 * Falha lançada quando um usuário tenta enviar a licença de uma venda sem ser
 * compositor da guia dessa venda.
 *
 * @property vendaId Identificador da venda cujo envio foi recusado.
 * @property userId Usuário que tentou enviar; null quando a chamada não é autenticada.
 * @constructor Cria a falha para a venda [vendaId] e o usuário [userId].
 */
class UploadNaoPermitido(
    val vendaId: Long,
    val userId: Long?,
) : RuntimeException("Usuário $userId não pode enviar a licença da venda $vendaId")

/**
 * Decide quem pode enviar e acessar a licença de uma venda.
 *
 * Instâncias são imutáveis e podem ser compartilhadas entre threads.
 *
 * @constructor Cria o validador com o conjunto de administradores.
 * @param adminIds Identificadores dos usuários administradores. Não é copiado: o
 * chamador não deve alterá-lo depois de construir o validador.
 */
class LicencaAccessValidator(private val adminIds: Set<Long>) {

    /**
     * Indica se [userId] pode enviar a licença de [venda]: só compositores da guia
     * da venda podem; administradores, comprador e demais usuários não.
     *
     * Não modifica seus argumentos nem a instância.
     *
     * @param venda Venda cuja licença seria enviada.
     * @param userId Usuário que tenta enviar; null representa chamada não autenticada.
     * @return true se [userId] é compositor da guia de [venda]; false caso contrário,
     * inclusive quando [userId] é null.
     */
    fun canUpload(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isCompositor(venda, userId)
    }

    /**
     * Exige que [userId] possa enviar a licença de [venda], segundo [canUpload].
     *
     * Não modifica seus argumentos nem a instância.
     *
     * @param venda Venda cuja licença será enviada.
     * @param userId Usuário que tenta enviar; null representa chamada não autenticada.
     * @throws UploadNaoPermitido Se [canUpload] devolver false para [venda] e [userId].
     */
    fun requireUpload(venda: Venda, userId: Long?) {
        if (!canUpload(venda, userId)) throw UploadNaoPermitido(venda.id, userId)
    }

    /**
     * Indica se [userId] pode acessar a licença de [venda], considerando o
     * cancelamento: em venda cancelada, administradores e compositores da guia
     * mantêm o acesso e o comprador o perde; em venda não cancelada, vale a regra
     * de [canAccess].
     *
     * Não modifica seus argumentos nem a instância.
     *
     * @param venda Venda cuja licença seria acessada.
     * @param userId Usuário que tenta acessar; null representa chamada não autenticada.
     * @return true se o acesso é permitido; false caso contrário, inclusive quando
     * [userId] é null.
     */
    fun canAccessAfterCancel(venda: Venda, userId: Long?): Boolean {
        if (!venda.cancelada) return canAccess(venda, userId)
        if (userId == null) return false
        if (isAdmin(userId)) return true
        return isCompositor(venda, userId)
    }

    fun canAccess(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        if (isAdmin(userId)) return true
        if (venda.compradorId == userId) return true
        return isCompositor(venda, userId)
    }

    private fun isAdmin(userId: Long): Boolean = userId in adminIds

    private fun isCompositor(venda: Venda, userId: Long): Boolean =
        venda.guia.compositores.any { it.userId == userId }
}
