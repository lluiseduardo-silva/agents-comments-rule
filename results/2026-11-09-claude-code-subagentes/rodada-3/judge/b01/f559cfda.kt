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
    RuntimeException("Usuário $userId não pode enviar licença da venda $vendaId")

class LicencaAccessValidator(private val adminIds: Set<Long>) {

    /**
     * Só compositor da guia envia licença; admin não.
     *
     * O arquivo enviado pertence a um titular, e o upload exige que quem envia seja esse
     * titular. Aceitar admin aqui só adiaria a recusa para depois do arquivo já estar no
     * storage, deixando um objeto órfão. Para destravar uma venda, o admin usa o fluxo
     * auditado de `manual-complete`.
     */
    fun canUpload(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isCompositor(venda, userId)
    }

    /** Mesma regra de [canUpload], mas falha com [UploadNaoPermitido] em vez de devolver false. */
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
     * Acesso depois do cancelamento: admin e compositor da guia continuam vendo a venda;
     * o comprador perde o acesso. Para venda não cancelada, vale a regra de [canAccess].
     */
    fun canAccessAfterCancel(venda: Venda, userId: Long?): Boolean {
        if (!venda.cancelada) return canAccess(venda, userId)
        if (userId == null) return false
        if (isAdmin(userId)) return true
        // Sem checagem de comprador: é isso que corta o acesso dele. Se o comprador
        // também for compositor da guia, mantém o acesso por ser compositor.
        return isCompositor(venda, userId)
    }

    private fun isAdmin(userId: Long): Boolean = userId in adminIds

    private fun isCompositor(venda: Venda, userId: Long): Boolean =
        venda.guia.compositores.any { it.userId == userId }
}
