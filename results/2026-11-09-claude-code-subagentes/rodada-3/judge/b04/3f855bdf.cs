using System;
using System.Collections.Generic;
using System.Linq;

namespace Licencas;

public record Compositor(long UserId);

public record Guia(IReadOnlyList<Compositor> Compositores);

public record Venda(long Id, long CompradorId, Guia Guia, bool Cancelada);

/// <summary>
/// Erro de autorização: o usuário não pode enviar a licença da venda.
/// </summary>
public class UploadNaoPermitidoException : Exception
{
    /// <summary>Identificador da venda cujo envio foi negado.</summary>
    public long VendaId { get; }

    /// <summary>Identificador do usuário que tentou o envio; nulo se anônimo.</summary>
    public long? UserId { get; }

    /// <summary>
    /// Cria o erro para a venda e o usuário informados.
    /// </summary>
    /// <param name="vendaId">Identificador da venda cujo envio foi negado.</param>
    /// <param name="userId">Identificador do usuário que tentou o envio; nulo se anônimo.</param>
    public UploadNaoPermitidoException(long vendaId, long? userId)
        : base($"Usuário {(userId?.ToString() ?? "anônimo")} não pode enviar licença da venda {vendaId}.")
    {
        VendaId = vendaId;
        UserId = userId;
    }
}

public class LicencaAccessValidator
{
    private readonly ISet<long> _adminIds;

    public LicencaAccessValidator(ISet<long> adminIds)
    {
        _adminIds = adminIds;
    }

    /// <summary>
    /// Indica se o usuário pode enviar a licença da venda: somente compositor da guia da venda pode;
    /// administrador não envia licença.
    /// </summary>
    /// <remarks>
    /// Não modifica seus argumentos nem o estado da instância.
    /// </remarks>
    /// <param name="venda">Venda cuja guia define os compositores autorizados. Não pode ser nula.</param>
    /// <param name="userId">Identificador do usuário autenticado; nulo indica usuário anônimo.</param>
    /// <returns>
    /// <c>true</c> se <paramref name="userId"/> for compositor da guia da venda; <c>false</c> se for
    /// nulo, administrador sem ser compositor, comprador ou qualquer outro usuário.
    /// </returns>
    public bool CanUpload(Venda venda, long? userId)
    {
        if (userId is null) return false;
        return IsCompositor(venda, userId.Value);
    }

    /// <summary>
    /// Indica se o usuário mantém acesso à venda depois do cancelamento: administrador e compositor da
    /// guia mantêm; o comprador perde o acesso quando a venda está cancelada.
    /// </summary>
    /// <remarks>
    /// Não modifica seus argumentos nem o estado da instância.
    /// </remarks>
    /// <param name="venda">Venda a consultar. Não pode ser nula.</param>
    /// <param name="userId">Identificador do usuário autenticado; nulo indica usuário anônimo.</param>
    /// <returns>
    /// <c>false</c> se <paramref name="userId"/> for nulo. Para venda cancelada, <c>true</c> apenas
    /// para administrador ou compositor da guia. Para venda não cancelada, o mesmo resultado de
    /// <see cref="CanAccess"/>.
    /// </returns>
    public bool CanAccessAfterCancel(Venda venda, long? userId)
    {
        if (userId is null) return false;
        if (!venda.Cancelada) return CanAccess(venda, userId);
        return IsAdmin(userId.Value) || IsCompositor(venda, userId.Value);
    }

    /// <summary>
    /// Garante que o usuário pode enviar a licença da venda, conforme <see cref="CanUpload"/>.
    /// </summary>
    /// <remarks>
    /// Não modifica seus argumentos nem o estado da instância.
    /// </remarks>
    /// <param name="venda">Venda cuja guia define os compositores autorizados. Não pode ser nula.</param>
    /// <param name="userId">Identificador do usuário autenticado; nulo indica usuário anônimo.</param>
    /// <exception cref="UploadNaoPermitidoException">
    /// Se <see cref="CanUpload"/> devolver <c>false</c> para a venda e o usuário.
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

    private bool IsAdmin(long userId) => _adminIds.Contains(userId);

    private static bool IsCompositor(Venda venda, long userId) =>
        venda.Guia.Compositores.Any(c => c.UserId == userId);
}
