using System;
using System.Collections.Generic;

/// <summary>
/// Item de uma reserva ou de uma linha de pedido: um SKU e a quantidade associada a ele.
/// </summary>
/// <param name="Sku">Identificador do produto.</param>
/// <param name="Quantidade">Quantidade de unidades do SKU.</param>
public sealed record ItemPedido(string Sku, int Quantidade);

/// <summary>
/// Pedido mutável que acumula as linhas reservadas por <see cref="Estoque.Reservar"/>.
/// </summary>
public sealed class Pedido
{
    /// <summary>
    /// Linhas do pedido, na ordem em que foram acrescentadas. Nunca é nula.
    /// </summary>
    public List<ItemPedido> Linhas { get; } = new List<ItemPedido>();
}

/// <summary>
/// Erro lançado quando uma quantidade menor ou igual a zero é informada.
/// </summary>
public sealed class QuantidadeInvalidaException : Exception
{
    /// <summary>
    /// Cria o erro para o SKU e a quantidade recusados.
    /// </summary>
    /// <param name="sku">SKU da operação recusada.</param>
    /// <param name="quantidade">Quantidade recusada.</param>
    public QuantidadeInvalidaException(string sku, int quantidade)
        : base($"Quantidade inválida para o SKU '{sku}': {quantidade}.")
    {
        Sku = sku;
        Quantidade = quantidade;
    }

    /// <summary>SKU da operação recusada.</summary>
    public string Sku { get; }

    /// <summary>Quantidade recusada.</summary>
    public int Quantidade { get; }
}

/// <summary>
/// Erro lançado quando o saldo de um SKU é menor que a quantidade a debitar.
/// </summary>
public sealed class EstoqueInsuficienteException : Exception
{
    /// <summary>
    /// Cria o erro para o SKU, a quantidade pedida e o saldo disponível.
    /// </summary>
    /// <param name="sku">SKU sem saldo suficiente.</param>
    /// <param name="solicitado">Quantidade que se tentou debitar.</param>
    /// <param name="disponivel">Saldo do SKU no momento da tentativa.</param>
    public EstoqueInsuficienteException(string sku, int solicitado, int disponivel)
        : base($"Estoque insuficiente para o SKU '{sku}': solicitado {solicitado}, disponível {disponivel}.")
    {
        Sku = sku;
        Solicitado = solicitado;
        Disponivel = disponivel;
    }

    /// <summary>SKU sem saldo suficiente.</summary>
    public string Sku { get; }

    /// <summary>Quantidade que se tentou debitar.</summary>
    public int Solicitado { get; }

    /// <summary>Saldo do SKU no momento da tentativa.</summary>
    public int Disponivel { get; }
}

/// <summary>
/// Erro lançado quando uma reposição deixaria o saldo de um SKU acima do limite do estoque.
/// </summary>
public sealed class LimiteExcedidoException : Exception
{
    /// <summary>
    /// Cria o erro para o SKU, o saldo que resultaria da reposição e o limite.
    /// </summary>
    /// <param name="sku">SKU da reposição recusada.</param>
    /// <param name="saldoResultante">Saldo que o SKU teria após a reposição.</param>
    /// <param name="limite">Saldo máximo permitido por SKU.</param>
    public LimiteExcedidoException(string sku, long saldoResultante, int limite)
        : base($"Reposição do SKU '{sku}' resultaria em {saldoResultante}, acima do limite {limite}.")
    {
        Sku = sku;
        SaldoResultante = saldoResultante;
        Limite = limite;
    }

    /// <summary>SKU da reposição recusada.</summary>
    public string Sku { get; }

    /// <summary>Saldo que o SKU teria após a reposição.</summary>
    public long SaldoResultante { get; }

    /// <summary>Saldo máximo permitido por SKU.</summary>
    public int Limite { get; }
}

/// <summary>
/// Controle de estoque em memória: guarda o saldo de cada SKU, que nunca passa de
/// <see cref="LimitePorSku"/> nem fica negativo. Não é seguro para uso concorrente.
/// </summary>
public sealed class Estoque
{
    private readonly Dictionary<string, int> _saldos = new Dictionary<string, int>();

    /// <summary>
    /// Cria um estoque vazio.
    /// </summary>
    /// <param name="limitePorSku">Saldo máximo permitido para cada SKU; deve ser maior que zero.</param>
    /// <exception cref="ArgumentOutOfRangeException">Se <paramref name="limitePorSku"/> for menor ou igual a zero.</exception>
    public Estoque(int limitePorSku)
    {
        if (limitePorSku <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(limitePorSku), limitePorSku, "O limite por SKU deve ser maior que zero.");
        }

        LimitePorSku = limitePorSku;
    }

    /// <summary>Saldo máximo permitido para cada SKU. Sempre maior que zero.</summary>
    public int LimitePorSku { get; }

    /// <summary>
    /// Soma <paramref name="quantidade"/> ao saldo de <paramref name="sku"/>.
    /// </summary>
    /// <remarks>
    /// Altera o saldo do SKU na instância, criando-o se ainda não existir. Quando lança
    /// exceção, nenhum saldo é alterado. Não modifica seus argumentos.
    /// </remarks>
    /// <param name="sku">SKU a repor; não pode ser nulo.</param>
    /// <param name="quantidade">Unidades a somar; deve ser maior que zero.</param>
    /// <exception cref="ArgumentNullException">Se <paramref name="sku"/> for nulo.</exception>
    /// <exception cref="QuantidadeInvalidaException">Se <paramref name="quantidade"/> for menor ou igual a zero.</exception>
    /// <exception cref="LimiteExcedidoException">Se o saldo resultante ficar acima de <see cref="LimitePorSku"/>.</exception>
    public void Repor(string sku, int quantidade)
    {
        if (sku is null)
        {
            throw new ArgumentNullException(nameof(sku));
        }

        if (quantidade <= 0)
        {
            throw new QuantidadeInvalidaException(sku, quantidade);
        }

        long resultante = (long)Quantidade(sku) + quantidade;
        if (resultante > LimitePorSku)
        {
            throw new LimiteExcedidoException(sku, resultante, LimitePorSku);
        }

        _saldos[sku] = (int)resultante;
    }

    /// <summary>
    /// Informa o saldo atual de <paramref name="sku"/>.
    /// </summary>
    /// <remarks>Não modifica a instância nem seus argumentos.</remarks>
    /// <param name="sku">SKU consultado; não pode ser nulo.</param>
    /// <returns>O saldo do SKU, ou zero se o SKU nunca foi reposto.</returns>
    /// <exception cref="ArgumentNullException">Se <paramref name="sku"/> for nulo.</exception>
    public int Quantidade(string sku)
    {
        if (sku is null)
        {
            throw new ArgumentNullException(nameof(sku));
        }

        return _saldos.TryGetValue(sku, out int saldo) ? saldo : 0;
    }

    /// <summary>
    /// Reserva cada item de <paramref name="itens"/>, na ordem: debita a quantidade do saldo
    /// do SKU e acrescenta o item ao fim de <see cref="Pedido.Linhas"/> de <paramref name="pedido"/>.
    /// </summary>
    /// <remarks>
    /// Altera os saldos da instância e <paramref name="pedido"/>.<see cref="Pedido.Linhas"/>;
    /// não modifica <paramref name="itens"/>. A operação para no primeiro item recusado: os
    /// itens anteriores a ele permanecem debitados e em <see cref="Pedido.Linhas"/>, e o item
    /// recusado e os seguintes não alteram nada.
    /// </remarks>
    /// <param name="itens">Itens a reservar; não pode ser nula nem conter elementos nulos. Lista vazia não altera nada.</param>
    /// <param name="pedido">Pedido que recebe as linhas reservadas; não pode ser nulo.</param>
    /// <exception cref="ArgumentNullException">
    /// Se <paramref name="itens"/>, <paramref name="pedido"/>, um item ou o SKU de um item for nulo.
    /// </exception>
    /// <exception cref="QuantidadeInvalidaException">Se a quantidade de um item for menor ou igual a zero.</exception>
    /// <exception cref="EstoqueInsuficienteException">Se o saldo do SKU de um item for menor que a quantidade dele.</exception>
    public void Reservar(IReadOnlyList<ItemPedido> itens, Pedido pedido)
    {
        if (itens is null)
        {
            throw new ArgumentNullException(nameof(itens));
        }

        if (pedido is null)
        {
            throw new ArgumentNullException(nameof(pedido));
        }

        foreach (ItemPedido item in itens)
        {
            if (item is null)
            {
                throw new ArgumentNullException(nameof(itens), "A lista de itens contém um elemento nulo.");
            }

            if (item.Sku is null)
            {
                throw new ArgumentNullException(nameof(itens), "Um item da lista tem SKU nulo.");
            }

            if (item.Quantidade <= 0)
            {
                throw new QuantidadeInvalidaException(item.Sku, item.Quantidade);
            }

            int saldo = Quantidade(item.Sku);
            if (saldo < item.Quantidade)
            {
                throw new EstoqueInsuficienteException(item.Sku, item.Quantidade, saldo);
            }

            _saldos[item.Sku] = saldo - item.Quantidade;
            pedido.Linhas.Add(item);
        }
    }

    /// <summary>
    /// Normaliza <paramref name="skus"/> no lugar: remove espaços das pontas de cada texto,
    /// converte-o para maiúsculas (regras de cultura invariante) e remove os que ficarem vazios.
    /// </summary>
    /// <remarks>
    /// Modifica <paramref name="skus"/>: cada elemento mantido é sobrescrito pela forma
    /// normalizada, na ordem original, e os vazios ou nulos são retirados. Não modifica a instância.
    /// </remarks>
    /// <param name="skus">Lista a normalizar; não pode ser nula. Elementos nulos são tratados como vazios.</param>
    /// <returns>Quantos elementos foram removidos.</returns>
    /// <exception cref="ArgumentNullException">Se <paramref name="skus"/> for nulo.</exception>
    public int NormalizarSkus(List<string> skus)
    {
        if (skus is null)
        {
            throw new ArgumentNullException(nameof(skus));
        }

        for (int i = 0; i < skus.Count; i++)
        {
            skus[i] = skus[i]?.Trim().ToUpperInvariant() ?? string.Empty;
        }

        return skus.RemoveAll(string.IsNullOrEmpty);
    }
}
