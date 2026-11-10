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
 * Erro de envio de licença por usuário que não é compositor da guia da venda.
 *
 * @property vendaId Identificador da venda cujo envio foi negado.
 * @property userId Identificador do usuário negado; `null` para usuário anônimo.
 * @constructor Cria o erro com a mensagem derivada de [vendaId] e [userId].
 */
class UploadNaoPermitido(val vendaId: Long, val userId: Long?) :
    RuntimeException("Usuário $userId não pode enviar licença da venda $vendaId")

class LicencaAccessValidator(private val adminIds: Set<Long>) {

    /**
     * Indica se o usuário pode enviar a licença da [venda]: somente compositor da guia da venda.
     * Administrador e comprador não podem enviar.
     *
     * Não modifica seus argumentos nem o estado da instância.
     *
     * @param venda Venda cuja licença seria enviada.
     * @param userId Identificador do usuário autenticado; `null` representa usuário anônimo.
     * @return `true` se [userId] é compositor da guia da [venda]; `false` se for `null`,
     * administrador sem ser compositor, comprador ou qualquer outro usuário.
     */
    fun canUpload(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isCompositor(venda, userId)
    }

    /**
     * Indica se o usuário mantém acesso à [venda] depois de cancelada: administrador e
     * compositor da guia mantêm; o comprador perde o acesso. Para venda não cancelada, o
     * resultado é o de [canAccess].
     *
     * Não modifica seus argumentos nem o estado da instância.
     *
     * @param venda Venda a ser acessada.
     * @param userId Identificador do usuário autenticado; `null` representa usuário anônimo.
     * @return `true` se o acesso é permitido; `false` se [userId] for `null`, for o comprador
     * de uma venda cancelada (sem ser administrador ou compositor) ou não tiver relação com a venda.
     */
    fun canAccessAfterCancel(venda: Venda, userId: Long?): Boolean {
        if (!venda.cancelada) return canAccess(venda, userId)
        if (userId == null) return false
        return isAdmin(userId) || isCompositor(venda, userId)
    }

    /**
     * Exige que o usuário possa enviar a licença da [venda], conforme [canUpload].
     *
     * Não modifica seus argumentos nem o estado da instância.
     *
     * @param venda Venda cuja licença seria enviada.
     * @param userId Identificador do usuário autenticado; `null` representa usuário anônimo.
     * @throws UploadNaoPermitido Se [canUpload] for `false` para [venda] e [userId].
     */
    fun requireUpload(venda: Venda, userId: Long?) {
        if (!canUpload(venda, userId)) throw UploadNaoPermitido(venda.id, userId)
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
