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
 * Erro que sinaliza uma tentativa de enviar a licença de uma venda por quem não tem
 * permissão de envio.
 *
 * @property vendaId Identificador da venda cuja licença seria enviada.
 * @property userId Identificador de quem tentou o envio; `null` quando a tentativa não
 * tinha usuário.
 * @constructor Cria o erro com uma mensagem que cita [vendaId] e [userId].
 */
class UploadNaoPermitido(val vendaId: Long, val userId: Long?) :
    RuntimeException("Envio de licença não permitido: venda $vendaId, usuário $userId")

/**
 * Decide quem pode enviar e quem pode acessar a licença de uma venda.
 *
 * @property adminIds Identificadores dos usuários admin; conjunto vazio significa que
 * nenhum usuário é admin.
 */
class LicencaAccessValidator(private val adminIds: Set<Long>) {

    /**
     * Indica se [userId] pode enviar a licença de [venda]: só compositor da guia da venda
     * pode, e ser admin não concede essa permissão.
     *
     * Não modifica seus argumentos nem o estado da instância.
     *
     * @param venda Venda cuja licença seria enviada.
     * @param userId Identificador de quem tenta o envio; `null` é aceito e representa a
     * ausência de usuário: o resultado é sempre `false`.
     * @return `true` se [userId] é compositor da guia de [venda]; `false` nos demais
     * casos, inclusive quando [userId] é `null`.
     */
    fun canUpload(venda: Venda, userId: Long?): Boolean {
        if (userId == null) return false
        return isCompositor(venda, userId)
    }

    /**
     * Exige que [userId] possa enviar a licença de [venda], pela mesma regra de [canUpload].
     *
     * Não modifica seus argumentos nem o estado da instância.
     *
     * @param venda Venda cuja licença seria enviada.
     * @param userId Identificador de quem tenta o envio; `null` é aceito e representa a
     * ausência de usuário: sempre produz [UploadNaoPermitido].
     * @throws UploadNaoPermitido Se [canUpload] devolve `false` para [venda] e [userId].
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
     * Indica se [userId] mantém o acesso à licença de [venda] depois do cancelamento da
     * venda: admin e compositor da guia mantêm, e o comprador perde.
     *
     * Não modifica seus argumentos nem o estado da instância.
     *
     * @param venda Venda cuja licença seria acessada. [Venda.cancelada] não é consultado:
     * cabe a quem chama usar esta função só para venda cancelada e [canAccess] para as
     * demais.
     * @param userId Identificador de quem tenta o acesso; `null` é aceito e representa a
     * ausência de usuário: o resultado é sempre `false`.
     * @return `true` se [userId] é admin ou compositor da guia de [venda]; `false` nos
     * demais casos, inclusive quando [userId] é `null` ou é apenas o comprador de [venda].
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
