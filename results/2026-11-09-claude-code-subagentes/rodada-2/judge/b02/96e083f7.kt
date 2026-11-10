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
 * Falha de autorização: o usuário não pode enviar a licença da venda.
 * Faz parte do contrato de [LicencaAccessValidator.requireUpload].
 */
class UploadNaoPermitido(val vendaId: Long, val userId: Long?) :
    RuntimeException("Upload de licença não permitido (venda=$vendaId, usuario=$userId)")

class LicencaAccessValidator(private val adminIds: Set<Long>) {

    /**
     * Só compositor da guia pode enviar a licença (LIC-482).
     *
     * Admin NÃO envia: o arquivo pertence a um titular e habilitar o admin exigiria
     * aceitar um `onBehalfOfUserId` explícito no confirm, o que lhe daria o poder de
     * aprovar a participação de um compositor. Antes, este método devolvia true para
     * admin e o `LicenseUploadService.assertUploadAllowed` derrubava a chamada
     * com 403, deixando um objeto órfão no S3 a cada tentativa (incidente de 14/10).
     * Para destravar uma venda, o caminho administrativo auditado é `manual-complete`.
     */
    fun canUpload(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isCompositor(venda, userId)
    }

    /**
     * Garante que o upload é permitido; não devolve nada.
     * Deve ser chamado ANTES de qualquer efeito colateral (ex.: gerar URL de upload
     * ou gravar no S3), para não deixar objetos órfãos.
     *
     * @throws UploadNaoPermitido quando [canUpload] é falso.
     */
    fun requireUpload(venda: Venda, userId: Long?) {
        if (!canUpload(venda, userId)) throw UploadNaoPermitido(venda.id, userId)
    }

    /**
     * Acesso a uma venda cancelada: admin e compositor da guia mantêm o acesso;
     * o comprador perde. Venda não cancelada não é tratada aqui: use [canAccess].
     */
    fun canAccessAfterCancel(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        if (isAdmin(userId)) return true
        return isCompositor(venda, userId)
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
