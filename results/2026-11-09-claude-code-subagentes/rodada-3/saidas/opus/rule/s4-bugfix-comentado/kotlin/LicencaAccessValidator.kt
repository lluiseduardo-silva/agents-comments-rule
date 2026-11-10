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
 * Erro lançado quando um usuário tenta enviar a licença de uma venda sem ter permissão.
 *
 * @property vendaId Identificador da venda cujo envio foi recusado.
 * @property userId Usuário que tentou enviar; `null` quando a chamada não tem usuário
 *   autenticado.
 * @constructor Cria o erro para a venda [vendaId] e o usuário [userId].
 */
class UploadNaoPermitido(
    val vendaId: Long,
    val userId: Long?,
) : RuntimeException("Usuário $userId não pode enviar a licença da venda $vendaId")

class LicencaAccessValidator(private val adminIds: Set<Long>) {

    /**
     * Informa se [userId] pode enviar a licença de [venda]: só um compositor da guia da
     * venda pode enviar. Administradores e o comprador não podem.
     *
     * Não modifica seus argumentos nem o estado da instância.
     *
     * @param venda Venda cuja licença seria enviada.
     * @param userId Usuário que pretende enviar; `null` representa ausência de usuário
     *   autenticado.
     * @return `true` se [userId] é compositor da guia de [venda]; `false` caso contrário,
     *   inclusive quando [userId] é `null`.
     */
    fun canUpload(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isCompositor(venda, userId)
    }

    /**
     * Garante que [userId] pode enviar a licença de [venda], seguindo a mesma regra de
     * [canUpload].
     *
     * Não modifica seus argumentos nem o estado da instância.
     *
     * @param venda Venda cuja licença seria enviada.
     * @param userId Usuário que pretende enviar; `null` representa ausência de usuário
     *   autenticado e sempre é recusado.
     * @throws UploadNaoPermitido Se [canUpload] devolver `false` para [venda] e [userId].
     */
    fun requireUpload(venda: Venda, userId: Long?) {
        if (!canUpload(venda, userId)) throw UploadNaoPermitido(venda.id, userId)
    }

    /**
     * Informa se [userId] tem acesso à licença de [venda], considerando o cancelamento:
     * em venda cancelada, administradores e compositores da guia mantêm o acesso e o
     * comprador o perde. Em venda não cancelada, vale a regra de [canAccess].
     *
     * Não modifica seus argumentos nem o estado da instância.
     *
     * @param venda Venda cuja licença seria acessada.
     * @param userId Usuário que pretende acessar; `null` representa ausência de usuário
     *   autenticado.
     * @return `true` se [userId] tem acesso segundo a regra acima; `false` caso contrário,
     *   inclusive quando [userId] é `null`. Um comprador que também é compositor da guia
     *   mantém o acesso em venda cancelada.
     */
    fun canAccessAfterCancel(venda: Venda, userId: Long?): Boolean {
        if (!venda.cancelada) return canAccess(venda, userId)
        if (userId == null) return false
        return isAdmin(userId) || isCompositor(venda, userId)
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
