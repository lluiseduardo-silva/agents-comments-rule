using System;
using System.Collections.Generic;
using System.Linq;

namespace Licencas;

public record Compositor(long UserId);

public record Guia(IReadOnlyList<Compositor> Compositores);

public record Venda(long Id, long CompradorId, Guia Guia, bool Cancelada);

/// <summary>
/// Erro que indica que um usuário não pode enviar a licença de uma venda; ocorre quando
/// <see cref="LicencaAccessValidator.RequireUpload"/> recusa o envio.
/// </summary>
public sealed class UploadNaoPermitidoException : Exception
{
    /// <summary>
    /// Cria o erro com uma mensagem que identifica a venda e, quando houver, o usuário recusado.
    /// </summary>
    /// <param name="vendaId">Identificador da venda cuja licença o usuário não pode enviar.</param>
    /// <param name="userId">
    /// Identificador do usuário recusado; <c>null</c> é aceito e significa que não há usuário
    /// identificado.
    /// </param>
    public UploadNaoPermitidoException(long vendaId, long? userId)
        : base(userId is null
            ? $"Envio da licença da venda {vendaId} não permitido: não há usuário identificado."
            : $"Envio da licença da venda {vendaId} não permitido para o usuário {userId}.")
    {
        VendaId = vendaId;
        UserId = userId;
    }

    /// <summary>Identificador da venda cuja licença o usuário não pode enviar.</summary>
    public long VendaId { get; }

    /// <summary>
    /// Identificador do usuário recusado; <c>null</c> quando não há usuário identificado.
    /// </summary>
    public long? UserId { get; }
}

public class LicencaAccessValidator
{
    private readonly ISet<long> _adminIds;

    public LicencaAccessValidator(ISet<long> adminIds)
    {
        _adminIds = adminIds;
    }

    /// <summary>
    /// Indica se o usuário pode enviar a licença da venda: só um compositor da guia da venda
    /// pode enviar.
    /// <para>Não modifica seus argumentos, a instância nem estado externo.</para>
    /// </summary>
    /// <param name="venda">
    /// Venda cuja licença seria enviada. Não deve ser nula, e o mesmo vale para sua guia, para a
    /// lista de compositores da guia e para cada compositor da lista. Uma lista vazia é aceita e
    /// significa que ninguém pode enviar.
    /// </param>
    /// <param name="userId">
    /// Identificador do usuário que pretende enviar; <c>null</c> é aceito e significa que não há
    /// usuário identificado.
    /// </param>
    /// <returns>
    /// <c>true</c> se <paramref name="userId"/> for o identificador de um compositor da guia da
    /// venda; <c>false</c> nos demais casos, inclusive quando <paramref name="userId"/> for
    /// <c>null</c> e quando o usuário for administrador ou comprador sem ser compositor da guia.
    /// </returns>
    /// <exception cref="NullReferenceException">
    /// Se <paramref name="userId"/> tiver valor e <paramref name="venda"/>, sua guia ou um
    /// compositor examinado for nulo.
    /// </exception>
    /// <exception cref="ArgumentNullException">
    /// Se <paramref name="userId"/> tiver valor e a lista de compositores da guia for nula.
    /// </exception>
    public bool CanUpload(Venda venda, long? userId)
    {
        if (userId is null) return false;
        return IsCompositor(venda, userId.Value);
    }

    /// <summary>
    /// Exige que o usuário possa enviar a licença da venda, pela regra de
    /// <see cref="CanUpload"/>, e falha quando ele não pode.
    /// <para>
    /// Não modifica seus argumentos, a instância nem estado externo, inclusive quando falha.
    /// </para>
    /// </summary>
    /// <param name="venda">
    /// Venda cuja licença seria enviada. Não deve ser nula, e o mesmo vale para sua guia, para a
    /// lista de compositores da guia e para cada compositor da lista.
    /// </param>
    /// <param name="userId">
    /// Identificador do usuário que pretende enviar; <c>null</c> é aceito e significa que não há
    /// usuário identificado, caso em que o envio não é permitido.
    /// </param>
    /// <exception cref="UploadNaoPermitidoException">
    /// Se <see cref="CanUpload"/> devolver <c>false</c> para <paramref name="venda"/> e
    /// <paramref name="userId"/>.
    /// </exception>
    /// <exception cref="NullReferenceException">
    /// Se <paramref name="venda"/> for nula, ou se <paramref name="userId"/> tiver valor e a guia
    /// da venda ou um compositor examinado for nulo.
    /// </exception>
    /// <exception cref="ArgumentNullException">
    /// Se <paramref name="userId"/> tiver valor e a lista de compositores da guia for nula.
    /// </exception>
    public void RequireUpload(Venda venda, long? userId)
    {
        if (!CanUpload(venda, userId)) throw new UploadNaoPermitidoException(venda.Id, userId);
    }

    public bool CanAccess(Venda venda, long? userId)
    {
        if (userId is null) return false;
        if (IsAdmin(userId.Value)) return true;
        if (venda.CompradorId == userId.Value) return true;
        return IsCompositor(venda, userId.Value);
    }

    /// <summary>
    /// Indica se o usuário mantém o acesso à licença de uma venda cancelada: administradores e
    /// compositores da guia mantêm o acesso; o comprador o perde.
    /// <para>Não modifica seus argumentos, a instância nem estado externo.</para>
    /// </summary>
    /// <param name="venda">
    /// Venda cancelada cujo acesso é avaliado. Não deve ser nula, e o mesmo vale para sua guia,
    /// para a lista de compositores da guia e para cada compositor da lista.
    /// </param>
    /// <param name="userId">
    /// Identificador do usuário que pede o acesso; <c>null</c> é aceito e significa que não há
    /// usuário identificado.
    /// </param>
    /// <returns>
    /// <c>true</c> se <paramref name="userId"/> for o identificador de um administrador ou de um
    /// compositor da guia da venda, ainda que essa pessoa também seja o comprador; <c>false</c>
    /// nos demais casos, inclusive quando <paramref name="userId"/> for <c>null</c> e quando o
    /// usuário for apenas o comprador.
    /// </returns>
    /// <exception cref="NullReferenceException">
    /// Se <paramref name="userId"/> tiver valor e o conjunto de administradores da instância for
    /// nulo, ou se o usuário identificado não for administrador e <paramref name="venda"/>, sua
    /// guia ou um compositor examinado for nulo.
    /// </exception>
    /// <exception cref="ArgumentNullException">
    /// Se o usuário identificado não for administrador e a lista de compositores da guia for nula.
    /// </exception>
    /// <remarks>
    /// Pré-condição: <paramref name="venda"/> está cancelada. O método não consulta
    /// <see cref="Venda.Cancelada"/>: aplica a regra de venda cancelada a qualquer venda recebida.
    /// </remarks>
    public bool CanAccessAfterCancel(Venda venda, long? userId)
    {
        if (userId is null) return false;
        if (IsAdmin(userId.Value)) return true;
        return IsCompositor(venda, userId.Value);
    }

    private bool IsAdmin(long userId) => _adminIds.Contains(userId);

    private static bool IsCompositor(Venda venda, long userId) =>
        venda.Guia.Compositores.Any(c => c.UserId == userId);
}
