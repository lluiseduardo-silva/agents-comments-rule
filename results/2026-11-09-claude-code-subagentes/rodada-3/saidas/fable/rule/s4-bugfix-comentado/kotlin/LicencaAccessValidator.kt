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
 * Erro que indica que um usuário não tem permissão para enviar a licença de uma venda.
 *
 * @property vendaId Identificador da venda cujo envio foi recusado.
 * @property userId Identificador do usuário recusado; `null` quando o envio foi
 *   tentado sem usuário identificado.
 */
class UploadNaoPermitido(val vendaId: Long, val userId: Long?) :
    RuntimeException("Envio de licença não permitido: venda=$vendaId, usuário=$userId")

/**
 * Decide quem pode enviar a licença de uma [Venda] e quem tem acesso à venda.
 *
 * @param adminIds Identificadores dos usuários com papel de administrador; vazio
 *   significa que não há administradores. O conjunto é guardado por referência, sem
 *   cópia.
 */
class LicencaAccessValidator(private val adminIds: Set<Long>) {

    /**
     * Indica se [userId] pode enviar a licença de [venda]: somente compositores da guia
     * da venda podem, e o papel de administrador não concede essa permissão.
     *
     * Não modifica os argumentos nem o estado da instância e não tem efeitos externos.
     *
     * @param venda Venda cuja guia define os compositores autorizados a enviar.
     * @param userId Identificador do usuário que pretende enviar; `null` é aceito e
     *   indica ausência de usuário identificado.
     * @return `true` se [userId] for compositor da guia de [venda]; `false` nos demais
     *   casos, inclusive para administrador que não seja compositor da guia e quando
     *   [userId] é `null`.
     */
    fun canUpload(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isCompositor(venda, userId)
    }

    /**
     * Garante que [userId] pode enviar a licença de [venda], pela regra de [canUpload];
     * retorna sem valor quando o envio é permitido.
     *
     * Não modifica os argumentos nem o estado da instância e não tem efeitos externos;
     * quando falha, nada fica alterado.
     *
     * @param venda Venda cuja guia define os compositores autorizados a enviar.
     * @param userId Identificador do usuário que pretende enviar; `null` é aceito e
     *   sempre resulta em falha.
     * @throws UploadNaoPermitido Se [canUpload] devolver `false` para [venda] e [userId].
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

    /**
     * Indica se [userId] tem acesso a [venda] depois de cancelada: administradores e
     * compositores da guia mantêm o acesso; o comprador o perde.
     *
     * Não modifica os argumentos nem o estado da instância e não tem efeitos externos.
     *
     * @param venda Venda cancelada. A função não consulta [Venda.cancelada]: cabe ao
     *   chamador garantir esse estado, e a regra é aplicada a qualquer venda recebida.
     * @param userId Identificador do usuário que pede acesso; `null` é aceito e indica
     *   ausência de usuário identificado.
     * @return `true` se [userId] for administrador ou compositor da guia de [venda];
     *   `false` nos demais casos, inclusive para o comprador que não seja administrador
     *   nem compositor da guia e quando [userId] é `null`.
     */
    fun canAccessAfterCancel(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        if (isAdmin(userId)) return true
        return isCompositor(venda, userId)
    }

    private fun isAdmin(userId: Long): Boolean = userId in adminIds

    private fun isCompositor(venda: Venda, userId: Long): Boolean =
        venda.guia.compositores.any { it.userId == userId }
}
