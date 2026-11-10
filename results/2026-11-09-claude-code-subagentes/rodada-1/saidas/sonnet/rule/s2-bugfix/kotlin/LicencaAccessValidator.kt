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
 * Erro de upload de licença negado ao usuário para a venda informada.
 *
 * Não modifica nenhum estado além da própria instância.
 *
 * @property vendaId Identificador da venda cujo upload foi negado.
 * @property userId Identificador do usuário que tentou o upload; null quando não autenticado.
 * @constructor Cria o erro com a mensagem derivada de [vendaId] e [userId].
 */
class UploadNaoPermitido(
    val vendaId: Long,
    val userId: Long?,
) : RuntimeException("Upload de licença não permitido: venda=$vendaId, usuário=$userId")

/**
 * Regras de acesso às licenças de uma [Venda].
 *
 * Não mantém estado mutável: as funções só leem seus argumentos e [adminIds].
 *
 * @property adminIds Identificadores dos usuários administradores.
 * @constructor Cria o validador com o conjunto de administradores informado.
 */
class LicencaAccessValidator(private val adminIds: Set<Long>) {

    /**
     * Indica se o usuário pode enviar licença para a venda: só compositor da guia pode.
     *
     * Não modifica seus argumentos nem a instância.
     *
     * @param venda Venda alvo do upload.
     * @param userId Identificador do usuário; null significa não autenticado.
     * @return true se [userId] é compositor da guia de [venda]; false se for null,
     * administrador sem ser compositor, comprador ou qualquer outro usuário.
     */
    fun canUpload(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isCompositor(venda, userId)
    }

    /**
     * Indica se o usuário mantém acesso a uma venda cancelada: administrador e compositor
     * da guia mantêm, o comprador perde.
     *
     * Não modifica seus argumentos nem a instância. Não verifica [Venda.cancelada]; o
     * chamador aplica esta regra apenas a vendas canceladas.
     *
     * @param venda Venda cancelada cujo acesso é avaliado.
     * @param userId Identificador do usuário; null significa não autenticado.
     * @return true se [userId] é administrador ou compositor da guia de [venda]; false se
     * for null, comprador sem outro papel ou qualquer outro usuário.
     */
    fun canAccessAfterCancel(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        if (isAdmin(userId)) return true
        return isCompositor(venda, userId)
    }

    /**
     * Exige que o usuário possa enviar licença para a venda.
     *
     * Não modifica seus argumentos nem a instância.
     *
     * @param venda Venda alvo do upload.
     * @param userId Identificador do usuário; null significa não autenticado.
     * @throws UploadNaoPermitido Se [canUpload] devolver false para [venda] e [userId].
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
