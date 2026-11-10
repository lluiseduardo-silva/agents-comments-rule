using System;
using System.Collections.Generic;
using System.Linq;

namespace Licencas;

public record Compositor(long UserId);

public record Guia(IReadOnlyList<Compositor> Compositores);

public record Venda(long Id, long CompradorId, Guia Guia, bool Cancelada);

/// <summary>
/// Erro lançado quando um usuário tenta enviar a licença de uma venda sem ser
/// compositor da guia dessa venda.
/// </summary>
public class UploadNaoPermitidoException : Exception
{
    /// <summary>Identificador da venda cujo envio foi recusado.</summary>
    public long VendaId { get; }

    /// <summary>Usuário que tentou o envio; <c>null</c> quando não havia usuário identificado.</summary>
    public long? UserId { get; }

    /// <summary>
    /// Cria o erro para a venda e o usuário informados.
    /// </summary>
    /// <param name="vendaId">Identificador da venda cujo envio foi recusado.</param>
    /// <param name="userId">Usuário que tentou o envio; <c>null</c> quando não havia usuário identificado.</param>
    public UploadNaoPermitidoException(long vendaId, long? userId)
        : base($"Usuário {userId?.ToString() ?? "anônimo"} não pode enviar a licença da venda {vendaId}.")
    {
        VendaId = vendaId;
        UserId = userId;
    }
}

/// <summary>
/// Decide quem pode enviar e acessar a licença de uma venda, a partir do comprador,
/// dos compositores da guia e do conjunto de administradores.
/// </summary>
public class LicencaAccessValidator
{
    private readonly ISet<long> _adminIds;

    public LicencaAccessValidator(ISet<long> adminIds)
    {
        _adminIds = adminIds;
    }

    /// <summary>
    /// Indica se o usuário pode enviar a licença da venda: só um compositor da guia
    /// pode; administradores e o comprador não podem.
    /// </summary>
    /// <remarks>
    /// Não modifica seus argumentos nem o estado da instância.
    /// </remarks>
    /// <param name="venda">Venda cuja licença seria enviada.</param>
    /// <param name="userId">Usuário que quer enviar; <c>null</c> representa um usuário não identificado.</param>
    /// <returns>
    /// <c>true</c> se o usuário é compositor da guia da venda; <c>false</c> caso contrário,
    /// inclusive quando <paramref name="userId"/> é <c>null</c>.
    /// </returns>
    public bool CanUpload(Venda venda, long? userId)
    {
        if (userId is null) return false;
        return IsCompositor(venda, userId.Value);
    }

    /// <summary>
    /// Garante que o usuário pode enviar a licença da venda, seguindo a mesma regra de
    /// <see cref="CanUpload"/>.
    /// </summary>
    /// <remarks>
    /// Não modifica seus argumentos nem o estado da instância.
    /// </remarks>
    /// <param name="venda">Venda cuja licença seria enviada.</param>
    /// <param name="userId">Usuário que quer enviar; <c>null</c> representa um usuário não identificado.</param>
    /// <exception cref="UploadNaoPermitidoException">
    /// Se <see cref="CanUpload"/> devolver <c>false</c> para a venda e o usuário informados.
    /// </exception>
    public void RequireUpload(Venda venda, long? userId)
    {
        if (!CanUpload(venda, userId))
            throw new UploadNaoPermitidoException(venda.Id, userId);
    }

    public bool CanAccess(Venda venda, long? userId)
    {
        if (userId is null) return false;
        if (IsAdmin(userId.Value)) return true;
        if (venda.CompradorId == userId.Value) return true;
        return IsCompositor(venda, userId.Value);
    }

    /// <summary>
    /// Indica se o usuário pode acessar a licença levando em conta o cancelamento: em
    /// venda cancelada, administradores e compositores da guia mantêm o acesso e o
    /// comprador o perde; em venda não cancelada, vale a regra de <see cref="CanAccess"/>.
    /// </summary>
    /// <remarks>
    /// Não modifica seus argumentos nem o estado da instância.
    /// </remarks>
    /// <param name="venda">Venda cuja licença seria acessada.</param>
    /// <param name="userId">Usuário que quer acessar; <c>null</c> representa um usuário não identificado.</param>
    /// <returns>
    /// <c>true</c> se o usuário tem acesso; <c>false</c> caso contrário, inclusive quando
    /// <paramref name="userId"/> é <c>null</c>.
    /// </returns>
    public bool CanAccessAfterCancel(Venda venda, long? userId)
    {
        if (!venda.Cancelada) return CanAccess(venda, userId);
        if (userId is null) return false;
        if (IsAdmin(userId.Value)) return true;
        return IsCompositor(venda, userId.Value);
    }

    private bool IsAdmin(long userId) => _adminIds.Contains(userId);

    private static bool IsCompositor(Venda venda, long userId) =>
        venda.Guia.Compositores.Any(c => c.UserId == userId);
}
