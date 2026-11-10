package licencas

data class Compositor(val userId: Long)

data class Guia(val compositores: List<Compositor>)

data class Venda(
    val id: Long,
    val compradorId: Long,
    val guia: Guia,
    val cancelada: Boolean,
)

class UploadNaoPermitido(val vendaId: Long, val userId: Long?) :
    RuntimeException("Upload de licença não permitido: venda=$vendaId, userId=$userId")

class LicencaAccessValidator(private val adminIds: Set<Long>) {

    // Admin não envia licença (LIC-482): só compositor da guia. O caminho
    // administrativo para destravar uma venda é o `manual-complete`.
    fun canUpload(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isCompositor(venda, userId)
    }

    /** @throws UploadNaoPermitido quando [canUpload] é falso. */
    fun requireUpload(venda: Venda, userId: Long?) {
        if (!canUpload(venda, userId)) throw UploadNaoPermitido(venda.id, userId)
    }

    fun canAccess(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        if (isAdmin(userId)) return true
        if (venda.compradorId == userId) return true
        return isCompositor(venda, userId)
    }

    // Acesso a uma venda cancelada: admin e compositor da guia mantêm; ser o
    // comprador deixa de dar acesso. Não consulta `venda.cancelada`: quem
    // chama decide quando a venda está morta.
    fun canAccessAfterCancel(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        if (isAdmin(userId)) return true
        return isCompositor(venda, userId)
    }

    private fun isAdmin(userId: Long): Boolean = userId in adminIds

    private fun isCompositor(venda: Venda, userId: Long): Boolean =
        venda.guia.compositores.any { it.userId == userId }
}
