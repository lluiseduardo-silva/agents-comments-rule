using System;
using System.Collections.Generic;
using System.Linq;

namespace Licencas;

public record Compositor(long UserId);

public record Guia(IReadOnlyList<Compositor> Compositores);

public record Venda(long Id, long CompradorId, Guia Guia, bool Cancelada);

public class UploadNaoPermitidoException : Exception
{
    public UploadNaoPermitidoException(long vendaId, long? userId)
        : base($"Upload não permitido para o usuário {userId?.ToString() ?? "anônimo"} na venda {vendaId}.")
    {
    }
}

public class LicencaAccessValidator
{
    private readonly ISet<long> _adminIds;

    public LicencaAccessValidator(ISet<long> adminIds)
    {
        _adminIds = adminIds;
    }

    public bool CanUpload(Venda venda, long? userId)
    {
        if (userId is null) return false;
        return IsCompositor(venda, userId.Value);
    }

    public void RequireUpload(Venda venda, long? userId)
    {
        if (!CanUpload(venda, userId))
            throw new UploadNaoPermitidoException(venda.Id, userId);
    }

    public bool CanAccessAfterCancel(Venda venda, long? userId)
    {
        if (userId is null) return false;
        if (!venda.Cancelada) return CanAccess(venda, userId);
        return IsAdmin(userId.Value) || IsCompositor(venda, userId.Value);
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
