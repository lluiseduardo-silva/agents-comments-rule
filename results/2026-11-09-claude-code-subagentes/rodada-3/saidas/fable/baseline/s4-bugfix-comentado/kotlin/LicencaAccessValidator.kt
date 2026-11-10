package licencas

data class Compositor(val userId: Long)

data class Guia(val compositores: List<Compositor>)

data class Venda(
    val id: Long,
    val compradorId: Long,
    val guia: Guia,
    val cancelada: Boolean,
)

/** Lançado por [LicencaAccessValidator.requireUpload] quando o usuário não pode enviar a licença da venda. */
class UploadNaoPermitido(val vendaId: Long, val userId: Long?) :
    RuntimeException("Upload de licença não permitido: venda=$vendaId, userId=$userId")

/**
 * Decide quem pode enviar e quem pode acessar a licença de uma venda.
 *
 * Em todas as verificações, `userId` nulo (usuário não autenticado) nunca tem permissão.
 */
class LicencaAccessValidator(private val adminIds: Set<Long>) {

    /**
     * Só compositor da guia da venda pode enviar licença.
     *
     * Admin fica de fora de propósito. O arquivo pertence a um titular, e
     * `LicenseUploadService.assertFileOwner` responde 403 a quem não é o dono: aceitar admin
     * aqui só empurraria a recusa para depois do envio, deixando um objeto órfão no S3.
     * Liberar de verdade exigiria que o admin agisse em nome de um titular, o que equivale a
     * aprovar a participação de um compositor. Para destravar uma venda, o caminho
     * administrativo é o `manual-complete`, que é auditado.
     */
    fun canUpload(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isCompositor(venda, userId)
    }

    /**
     * Igual a [canUpload], mas falha em vez de devolver falso.
     *
     * @throws UploadNaoPermitido se o usuário não puder enviar a licença da venda.
     */
    fun requireUpload(venda: Venda, userId: Long?) {
        if (!canUpload(venda, userId)) throw UploadNaoPermitido(venda.id, userId)
    }

    /**
     * Acesso à licença: admin, comprador ou compositor da guia.
     *
     * Não leva o cancelamento em conta; para venda cancelada, a regra é a de
     * [canAccessAfterCancel].
     */
    fun canAccess(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        if (isAdmin(userId)) return true
        if (venda.compradorId == userId) return true
        return isCompositor(venda, userId)
    }

    /**
     * Acesso à licença de uma venda cancelada: admin e compositor da guia mantêm o acesso;
     * ser comprador deixa de dar acesso.
     *
     * Não consulta [Venda.cancelada]: responde sempre pela regra pós-cancelamento, e cabe a
     * quem chama aplicá-la só a vendas canceladas.
     */
    fun canAccessAfterCancel(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isAdmin(userId) || isCompositor(venda, userId)
    }

    private fun isAdmin(userId: Long): Boolean = userId in adminIds

    private fun isCompositor(venda: Venda, userId: Long): Boolean =
        venda.guia.compositores.any { it.userId == userId }
}
