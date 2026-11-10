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
 * Falha de [LicencaAccessValidator.requireUpload]: o usuário não pode enviar a
 * licença desta venda. `userId` é nulo quando a chamada não está autenticada.
 */
class UploadNaoPermitido(
    val vendaId: Long,
    val userId: Long?,
) : RuntimeException("Usuário $userId não pode enviar licença da venda $vendaId")

class LicencaAccessValidator(private val adminIds: Set<Long>) {

    /**
     * Só um compositor da guia pode enviar a licença (LIC-482).
     *
     * Admin não é aceito de propósito: o arquivo pertence a um titular, e a
     * etapa seguinte do upload exige que quem envia seja titular. Aceitar o
     * admin aqui só adiava a recusa para depois do envio do objeto, deixando
     * arquivos órfãos no storage. Para destravar uma venda, o caminho
     * administrativo é o `manual-complete`, que é auditado.
     */
    fun canUpload(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isCompositor(venda, userId)
    }

    /**
     * Versão que falha de [canUpload], para ser chamada na entrada do fluxo de
     * upload, antes de qualquer efeito colateral (como gravar o arquivo).
     *
     * @throws UploadNaoPermitido quando [canUpload] devolve false.
     */
    fun requireUpload(venda: Venda, userId: Long?) {
        if (!canUpload(venda, userId)) throw UploadNaoPermitido(venda.id, userId)
    }

    /** Acesso à licença enquanto a venda está ativa: admin, comprador e compositores da guia. */
    fun canAccess(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        if (isAdmin(userId)) return true
        if (venda.compradorId == userId) return true
        return isCompositor(venda, userId)
    }

    /**
     * Acesso à licença considerando o cancelamento da venda.
     *
     * - Venda cancelada: admin e compositores da guia mantêm o acesso; o
     *   comprador perde, porque a compra deixou de valer.
     * - Venda ativa: mesmas regras de [canAccess].
     */
    fun canAccessAfterCancel(venda: Venda, userId: Long?): Boolean {
        if (!venda.cancelada) return canAccess(venda, userId)
        if (userId == null) return false
        if (isAdmin(userId)) return true
        return isCompositor(venda, userId)
    }

    private fun isAdmin(userId: Long): Boolean = userId in adminIds

    private fun isCompositor(venda: Venda, userId: Long): Boolean =
        venda.guia.compositores.any { it.userId == userId }
}
