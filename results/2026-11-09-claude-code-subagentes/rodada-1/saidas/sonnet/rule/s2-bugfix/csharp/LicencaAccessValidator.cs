using System;
using System.Collections.Generic;
using System.Linq;

namespace Licencas;

public record Compositor(long UserId);

public record Guia(IReadOnlyList<Compositor> Compositores);

public record Venda(long Id, long CompradorId, Guia Guia, bool Cancelada);

/// <summary>
/// Erro lançado quando um usuário sem permissão tenta enviar a licença de uma venda.
/// </summary>
public class UploadNaoPermitidoException : Exception
{
    /// <summary>Identificador da venda cujo envio foi negado.</summary>
    public long VendaId { get; }

    /// <summary>Identificador do usuário negado; nulo se não autenticado.</summary>
    public long? UserId { get; }

    /// <summary>
    /// Cria o erro para a venda e o usuário informados.
    /// </summary>
    /// <param name="vendaId">Identificador da venda cujo envio foi negado.</param>
    /// <param name="userId">Identificador do usuário negado; nulo se não autenticado.</param>
    public UploadNaoPermitidoException(long vendaId, long? userId)
        : base($"Usuário {userId?.ToString() ?? "anônimo"} não pode enviar licença da venda {vendaId}.")
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
    /// Indica se o usuário pode enviar a licença da venda: somente compositor da guia da venda.
    /// </summary>
    /// <remarks>
    /// Não modifica os argumentos nem o estado da instância.
    /// </remarks>
    /// <param name="venda">Venda cuja guia define os compositores autorizados.</param>
    /// <param name="userId">Identificador do usuário; nulo significa usuário não autenticado.</param>
    /// <returns>
    /// <c>true</c> se o usuário é compositor da guia; <c>false</c> se for nulo, administrador sem
    /// participação na guia, comprador ou qualquer outro usuário.
    /// </returns>
    public bool CanUpload(Venda venda, long? userId)
    {
        if (userId is null) return false;
        return IsCompositor(venda, userId.Value);
    }

    /// <summary>
    /// Indica se o usuário mantém acesso à venda após ela ser cancelada: administrador e
    /// compositor da guia mantêm; o comprador perde. Para venda não cancelada, o resultado é o
    /// de <see cref="CanAccess"/>.
    /// </summary>
    /// <remarks>
    /// Não modifica os argumentos nem o estado da instância.
    /// </remarks>
    /// <param name="venda">Venda a consultar.</param>
    /// <param name="userId">Identificador do usuário; nulo significa usuário não autenticado.</param>
    /// <returns>
    /// <c>true</c> se o acesso é mantido; <c>false</c> se o usuário for nulo ou, em venda
    /// cancelada, for o comprador sem outro papel que conceda acesso.
    /// </returns>
    public bool CanAccessAfterCancel(Venda venda, long? userId)
    {
        if (!venda.Cancelada) return CanAccess(venda, userId);
        if (userId is null) return false;
        return IsAdmin(userId.Value) || IsCompositor(venda, userId.Value);
    }

    /// <summary>
    /// Garante que o usuário pode enviar a licença da venda, segundo <see cref="CanUpload"/>.
    /// </summary>
    /// <remarks>
    /// Não modifica os argumentos nem o estado da instância.
    /// </remarks>
    /// <param name="venda">Venda cuja guia define os compositores autorizados.</param>
    /// <param name="userId">Identificador do usuário; nulo significa usuário não autenticado.</param>
    /// <exception cref="UploadNaoPermitidoException">Se <see cref="CanUpload"/> for falso.</exception>
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
