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
 * Recusa de envio de licença, lançada por [LicencaAccessValidator.requireUpload].
 *
 * Leva a venda e o usuário para que quem trata o erro não precise reconstruir o contexto.
 * `userId` nulo indica chamada sem usuário autenticado.
 */
class UploadNaoPermitidoException(
    val vendaId: Long,
    val userId: Long?,
) : RuntimeException("Upload de licença não permitido: venda=$vendaId, usuário=$userId")

/**
 * Decide quem pode enviar e quem pode acessar a licença de uma [Venda].
 *
 * Em todas as regras, `userId` nulo (chamada sem usuário autenticado) é negado.
 */
class LicencaAccessValidator(private val adminIds: Set<Long>) {

    /**
     * Só compositor da guia envia licença.
     *
     * Admin fica de fora de propósito: o arquivo pertence a um titular, e o admin não é titular.
     * Aceitá-lo exigiria informar em nome de qual compositor ele envia, o que lhe daria o poder
     * de aprovar a participação de um compositor. O caminho administrativo para destravar uma
     * venda é o `manual-complete`, que é auditado.
     *
     * Esta regra não pode ser mais permissiva que a checagem de titular feita em
     * `LicenseUploadService.assertUploadAllowed`: um `true` aqui para quem não é titular
     * termina em 403 lá e deixa um objeto órfão no storage.
     */
    fun canUpload(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isCompositor(venda, userId)
    }

    /**
     * Forma de [canUpload] para a entrada da operação de envio: retorna sem valor quando o envio
     * é permitido e lança [UploadNaoPermitidoException] quando não é.
     *
     * Chame antes de qualquer efeito do upload, porque uma recusa depois de gravar o arquivo
     * deixa objeto órfão no storage. A regra mora só em [canUpload]; prefira `canUpload` quando
     * a recusa for um resultado esperado, e não um erro.
     */
    fun requireUpload(venda: Venda, userId: Long?) {
        if (!canUpload(venda, userId)) throw UploadNaoPermitidoException(venda.id, userId)
    }

    /**
     * Acesso à licença: admin, comprador e compositor da guia.
     *
     * Não consulta [Venda.cancelada]. A regra para venda cancelada está em
     * [canAccessAfterCancel].
     */
    fun canAccess(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        if (isAdmin(userId)) return true
        if (venda.compradorId == userId) return true
        return isCompositor(venda, userId)
    }

    /**
     * Acesso à licença de uma venda morta (cancelada): admin e compositor da guia mantêm o
     * acesso; o comprador perde.
     *
     * Também não consulta [Venda.cancelada]: responde quem continua com acesso uma vez que a
     * venda esteja cancelada. Cabe a quem chama aplicar esta regra só a vendas canceladas.
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
