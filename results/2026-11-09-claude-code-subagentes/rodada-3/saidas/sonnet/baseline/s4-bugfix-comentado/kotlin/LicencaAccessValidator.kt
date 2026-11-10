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
 * Erro lançado quando o usuário não pode enviar a licença da venda.
 * Deve ser traduzido para 403 na camada HTTP.
 */
class UploadNaoPermitido(message: String) : RuntimeException(message)

class LicencaAccessValidator(private val adminIds: Set<Long>) {

    /**
     * Só compositor da guia pode enviar a licença.
     *
     * Admin NÃO envia (LIC-482): antes este método devolvia true para admin, mas o
     * `LicenseUploadService.assertUploadAllowed` derrubava a chamada com 403 em
     * `assertFileOwner` (o arquivo é do titular), deixando um objeto órfão no S3.
     * Habilitar de verdade exigiria um `onBehalfOfUserId` no confirm, o que daria ao
     * admin o poder de aprovar a participação de um compositor. Para destravar uma
     * venda, o caminho administrativo auditado é o `manual-complete`.
     */
    fun canUpload(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isCompositor(venda, userId)
    }

    /**
     * Versão que falha em vez de devolver booleano: não retorna nada e lança
     * [UploadNaoPermitido] quando [canUpload] for falso.
     */
    fun requireUpload(venda: Venda, userId: Long?) {
        if (!canUpload(venda, userId)) {
            throw UploadNaoPermitido("Usuário $userId não pode enviar licença da venda ${venda.id}")
        }
    }

    fun canAccess(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        if (isAdmin(userId)) return true
        if (venda.compradorId == userId) return true
        return isCompositor(venda, userId)
    }

    /**
     * Acesso levando em conta o cancelamento da venda.
     *
     * Venda cancelada: admin e compositor da guia mantêm o acesso; o comprador perde.
     * Venda não cancelada: vale a regra normal de [canAccess].
     */
    fun canAccessAfterCancel(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        if (!venda.cancelada) return canAccess(venda, userId)
        // Comprador é deliberadamente omitido aqui.
        return isAdmin(userId) || isCompositor(venda, userId)
    }

    private fun isAdmin(userId: Long): Boolean = userId in adminIds

    private fun isCompositor(venda: Venda, userId: Long): Boolean =
        venda.guia.compositores.any { it.userId == userId }
}
