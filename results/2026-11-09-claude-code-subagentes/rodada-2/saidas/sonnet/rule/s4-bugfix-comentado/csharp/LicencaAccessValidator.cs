using System;
using System.Collections.Generic;
using System.Linq;

namespace Licencas;

public record Compositor(long UserId);

public record Guia(IReadOnlyList<Compositor> Compositores);

public record Venda(long Id, long CompradorId, Guia Guia, bool Cancelada);

/// <summary>
/// Erro de envio de licença por usuário que não é compositor da guia da venda.
/// </summary>
/// <remarks>
/// Propriedades: <see cref="VendaId"/> é a venda do envio recusado e <see cref="UserId"/> o
/// usuário que tentou (<c>null</c> se anônimo).
/// </remarks>
public class UploadNaoPermitidoException : Exception
{
    public long VendaId { get; }

    public long? UserId { get; }

    /// <summary>
    /// Cria o erro para a venda e o usuário informados.
    /// </summary>
    /// <param name="vendaId">Identificador da venda.</param>
    /// <param name="userId">Identificador do usuário; <c>null</c> se anônimo.</param>
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
    /// Indica se o usuário pode enviar a licença da venda: somente compositor da guia pode.
    /// </summary>
    /// <remarks>
    /// Não modifica seus argumentos nem o estado da instância.
    /// </remarks>
    /// <param name="venda">Venda cuja guia é consultada.</param>
    /// <param name="userId">Identificador do usuário; <c>null</c> (anônimo) nunca é aceito.</param>
    /// <returns>
    /// <c>true</c> se o usuário é compositor da guia da venda; <c>false</c> caso contrário,
    /// inclusive para administradores e para o comprador.
    /// </returns>
    public bool CanUpload(Venda venda, long? userId)
    {
        if (userId is null) return false;
        return IsCompositor(venda, userId.Value);
    }

    /// <summary>
    /// Exige que o usuário possa enviar a licença da venda, falhando caso contrário.
    /// </summary>
    /// <remarks>
    /// Não modifica seus argumentos nem o estado da instância.
    /// </remarks>
    /// <param name="venda">Venda cuja guia é consultada.</param>
    /// <param name="userId">Identificador do usuário; <c>null</c> (anônimo) nunca é aceito.</param>
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

    /// <summary>
    /// Indica se o usuário mantém acesso à licença de uma venda cancelada: administrador e
    /// compositor da guia mantêm; o comprador perde.
    /// </summary>
    /// <remarks>
    /// Não modifica seus argumentos nem o estado da instância. Não consulta
    /// <see cref="Venda.Cancelada"/>: aplica a regra de acesso própria de uma venda cancelada,
    /// e quem chama decide quando ela vale.
    /// </remarks>
    /// <param name="venda">Venda cuja guia é consultada.</param>
    /// <param name="userId">Identificador do usuário; <c>null</c> (anônimo) nunca é aceito.</param>
    /// <returns>
    /// <c>true</c> se o usuário é administrador ou compositor da guia; <c>false</c> caso
    /// contrário, inclusive para o comprador.
    /// </returns>
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
