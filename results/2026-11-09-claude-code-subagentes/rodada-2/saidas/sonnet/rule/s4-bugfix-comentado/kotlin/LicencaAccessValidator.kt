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
 * Indica que o usuário não pode enviar a licença da venda.
 *
 * @constructor Cria o erro com a [mensagem] informada.
 * @param mensagem Descrição da recusa.
 */
class UploadNaoPermitido(mensagem: String) : RuntimeException(mensagem)

/**
 * Decide quem pode enviar e quem pode acessar a licença de uma [Venda].
 *
 * Só compositor da guia envia licença; administrador não envia.
 *
 * @property adminIds Identificadores dos usuários administradores.
 * @constructor Cria o validador com o conjunto de administradores informado.
 */
class LicencaAccessValidator(private val adminIds: Set<Long>) {

    /**
     * Indica se o usuário pode enviar a licença da venda: somente compositor da guia.
     *
     * Não modifica seus argumentos nem a instância.
     *
     * @param venda Venda cuja licença seria enviada.
     * @param userId Identificador do usuário; `null` representa usuário não autenticado.
     * @return `true` se [userId] é compositor da guia da [venda]; `false` se é `null`,
     * administrador sem ser compositor, comprador ou estranho à venda.
     */
    fun canUpload(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isCompositor(venda, userId)
    }

    /**
     * Exige que o usuário possa enviar a licença da venda.
     *
     * Não modifica seus argumentos nem a instância.
     *
     * @param venda Venda cuja licença seria enviada.
     * @param userId Identificador do usuário; `null` representa usuário não autenticado.
     * @throws UploadNaoPermitido Se [canUpload] for falso para [venda] e [userId].
     */
    fun requireUpload(venda: Venda, userId: Long?) {
        if (!canUpload(venda, userId)) {
            throw UploadNaoPermitido("Usuário não pode enviar a licença da venda ${venda.id}")
        }
    }

    /**
     * Indica se o usuário mantém acesso à licença depois que a venda é cancelada.
     *
     * Em venda cancelada, administrador e compositor da guia mantêm o acesso e o
     * comprador o perde. Em venda não cancelada, o resultado é o de [canAccess].
     * Não modifica seus argumentos nem a instância.
     *
     * @param venda Venda cuja licença seria acessada.
     * @param userId Identificador do usuário; `null` representa usuário não autenticado.
     * @return `true` se o acesso é mantido; `false` se [userId] é `null`, ou se a venda
     * está cancelada e o usuário não é administrador nem compositor da guia.
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
