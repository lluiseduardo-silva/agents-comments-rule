using System;
using System.Collections.Generic;
using System.Linq;

namespace Licencas;

public record Compositor(long UserId);

public record Guia(IReadOnlyList<Compositor> Compositores);

public record Venda(long Id, long CompradorId, Guia Guia, bool Cancelada);

/// <summary>
/// Erro lançado por <see cref="LicencaAccessValidator.RequireUpload"/> quando o usuário não tem permissão
/// para enviar a licença da venda: nenhum usuário informado ou usuário que não é compositor da guia.
/// </summary>
public class UploadNaoPermitidoException : Exception
{
    /// <summary>
    /// Cria o erro de envio recusado, com uma mensagem que identifica a venda e o usuário.
    /// </summary>
    /// <param name="vendaId">Id da venda cujo envio de licença foi recusado.</param>
    /// <param name="userId">Id do usuário recusado; nulo quando nenhum usuário foi informado.</param>
    public UploadNaoPermitidoException(long vendaId, long? userId)
        : base(userId is null
            ? $"Envio de licença não permitido na venda {vendaId}: nenhum usuário informado."
            : $"Envio de licença não permitido na venda {vendaId}: o usuário {userId} não é compositor da guia.")
    {
        VendaId = vendaId;
        UserId = userId;
    }

    /// <summary>Id da venda cujo envio de licença foi recusado.</summary>
    public long VendaId { get; }

    /// <summary>Id do usuário recusado; nulo quando nenhum usuário foi informado.</summary>
    public long? UserId { get; }
}

/// <summary>
/// Decide, pelo papel do usuário (admin, comprador ou compositor da guia), se ele pode acessar uma venda
/// e enviar a licença dela.
/// </summary>
public class LicencaAccessValidator
{
    /// <summary>Ids dos usuários com papel de admin.</summary>
    private readonly ISet<long> _adminIds;

    /// <summary>
    /// Cria o validador com o conjunto de admins consultado nas decisões de acesso.
    /// </summary>
    /// <param name="adminIds">
    /// Ids dos usuários com papel de admin; pode ser vazio. A instância guarda a referência recebida, sem
    /// copiá-la, de modo que alterações posteriores no conjunto se refletem nas decisões. Nulo não é
    /// rejeitado aqui e faz <see cref="CanAccess"/> e <see cref="CanAccessAfterCancel"/> lançarem
    /// <see cref="NullReferenceException"/> para qualquer usuário não nulo.
    /// </param>
    public LicencaAccessValidator(ISet<long> adminIds)
    {
        _adminIds = adminIds;
    }

    /// <summary>
    /// Indica se o usuário pode enviar a licença da venda: só compositor da guia pode, e ser admin não
    /// concede essa permissão.
    /// </summary>
    /// <remarks>
    /// Não modifica seus argumentos, a instância nem estado externo.
    /// </remarks>
    /// <param name="venda">
    /// Venda cuja guia lista os compositores. Não pode ser nula, nem sua guia ou a lista de compositores;
    /// a lista pode ser vazia.
    /// </param>
    /// <param name="userId">
    /// Id do usuário avaliado; nulo significa que nenhum usuário foi identificado e nunca é aceito.
    /// </param>
    /// <returns>
    /// <c>true</c> se o usuário for compositor da guia da venda; <c>false</c> se não for ou se
    /// <paramref name="userId"/> for nulo.
    /// </returns>
    /// <exception cref="NullReferenceException">
    /// Se <paramref name="userId"/> não for nulo e <paramref name="venda"/>, sua guia ou um compositor
    /// percorrido na lista for nulo.
    /// </exception>
    /// <exception cref="ArgumentNullException">
    /// Se <paramref name="userId"/> não for nulo e a lista de compositores da guia for nula.
    /// </exception>
    public bool CanUpload(Venda venda, long? userId)
    {
        if (userId is null) return false;
        return IsCompositor(venda, userId.Value);
    }

    /// <summary>
    /// Exige que o usuário possa enviar a licença da venda, pela regra de <see cref="CanUpload"/>.
    /// </summary>
    /// <remarks>
    /// Não modifica seus argumentos, a instância nem estado externo. Retorna normalmente quando o envio é
    /// permitido.
    /// </remarks>
    /// <param name="venda">
    /// Venda cuja licença seria enviada. Não pode ser nula, nem sua guia ou a lista de compositores; a
    /// lista pode ser vazia.
    /// </param>
    /// <param name="userId">
    /// Id do usuário que faria o envio; nulo significa que nenhum usuário foi identificado e sempre é
    /// recusado.
    /// </param>
    /// <exception cref="UploadNaoPermitidoException">
    /// Se <see cref="CanUpload"/> devolver <c>false</c> para os mesmos argumentos:
    /// <paramref name="userId"/> nulo ou usuário que não é compositor da guia.
    /// </exception>
    /// <exception cref="NullReferenceException">
    /// Se <paramref name="venda"/> for nula; ou se <paramref name="userId"/> não for nulo e a guia ou um
    /// compositor percorrido na lista for nulo.
    /// </exception>
    /// <exception cref="ArgumentNullException">
    /// Se <paramref name="userId"/> não for nulo e a lista de compositores da guia for nula.
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
    /// Indica se o usuário tem acesso à venda depois de cancelada: admin e compositor da guia mantêm o
    /// acesso, e o comprador o perde.
    /// </summary>
    /// <remarks>
    /// Não modifica seus argumentos, a instância nem estado externo.
    /// </remarks>
    /// <param name="venda">
    /// Venda avaliada. <see cref="Venda.Cancelada"/> não é consultado: a regra de venda cancelada é
    /// aplicada qualquer que seja o seu valor. Não pode ser nula, nem sua guia ou a lista de compositores;
    /// a lista pode ser vazia.
    /// </param>
    /// <param name="userId">
    /// Id do usuário avaliado; nulo significa que nenhum usuário foi identificado e nunca é aceito.
    /// </param>
    /// <returns>
    /// <c>true</c> se o usuário for admin ou compositor da guia da venda; <c>false</c> nos demais casos,
    /// inclusive para quem é apenas o comprador e quando <paramref name="userId"/> for nulo.
    /// </returns>
    /// <exception cref="NullReferenceException">
    /// Se <paramref name="userId"/> não for nulo e o conjunto de admins da instância for nulo; ou se o
    /// usuário não for admin e <paramref name="venda"/>, sua guia ou um compositor percorrido na lista
    /// for nulo.
    /// </exception>
    /// <exception cref="ArgumentNullException">
    /// Se o usuário não for nulo nem admin e a lista de compositores da guia for nula.
    /// </exception>
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
