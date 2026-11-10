using System;
using System.Collections.Generic;

/// <summary>
/// Item de uma reserva: um sku e a quantidade pedida dele.
/// </summary>
/// <param name="Sku">Identificador do produto.</param>
/// <param name="Quantidade">Quantidade pedida; deve ser maior que zero para ser reservada.</param>
public readonly record struct ItemReserva(string Sku, int Quantidade);

/// <summary>
/// Pedido mutável que acumula as linhas reservadas no estoque.
/// </summary>
public class Pedido
{
    /// <summary>
    /// Linhas já reservadas, na ordem em que foram reservadas.
    /// </summary>
    public List<ItemReserva> Linhas { get; } = new();
}

/// <summary>
/// Erro de reserva quando o saldo do sku é menor que a quantidade pedida.
/// </summary>
public class EstoqueInsuficienteException : Exception
{
    /// <summary>
    /// Cria o erro para o sku e a quantidade que não puderam ser atendidos.
    /// </summary>
    /// <param name="sku">Sku sem saldo suficiente.</param>
    /// <param name="solicitada">Quantidade pedida.</param>
    /// <param name="disponivel">Saldo do sku no momento do pedido.</param>
    public EstoqueInsuficienteException(string sku, int solicitada, int disponivel)
        : base($"Estoque insuficiente para '{sku}': pedido {solicitada}, disponível {disponivel}.")
    {
        Sku = sku;
        Solicitada = solicitada;
        Disponivel = disponivel;
    }

    /// <summary>Sku sem saldo suficiente.</summary>
    public string Sku { get; }

    /// <summary>Quantidade pedida.</summary>
    public int Solicitada { get; }

    /// <summary>Saldo do sku no momento do pedido.</summary>
    public int Disponivel { get; }
}

/// <summary>
/// Controle de estoque em memória, com saldo por sku limitado a <see cref="LimitePorSku"/>.
/// </summary>
/// <remarks>
/// Os métodos são serializados por um lock interno; o saldo vive apenas no processo
/// e não é compartilhado entre instâncias.
/// </remarks>
public class Estoque
{
    private readonly object _trava = new();
    private readonly Dictionary<string, int> _saldos = new();

    /// <summary>
    /// Cria um estoque vazio.
    /// </summary>
    /// <param name="limitePorSku">Saldo máximo de cada sku; deve ser maior que zero.</param>
    /// <exception cref="ArgumentOutOfRangeException">Se <paramref name="limitePorSku"/> for menor ou igual a zero.</exception>
    public Estoque(int limitePorSku)
    {
        if (limitePorSku <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(limitePorSku), "O limite por sku deve ser maior que zero.");
        }

        LimitePorSku = limitePorSku;
    }

    /// <summary>Saldo máximo permitido para cada sku.</summary>
    public int LimitePorSku { get; }

    /// <summary>
    /// Soma a quantidade ao saldo do sku.
    /// </summary>
    /// <remarks>
    /// Modifica o saldo do sku na instância; não modifica argumentos. Se falhar, o saldo não muda.
    /// </remarks>
    /// <param name="sku">Sku a repor; não pode ser nulo.</param>
    /// <param name="quantidade">Quantidade a somar; deve ser maior que zero.</param>
    /// <exception cref="ArgumentNullException">Se <paramref name="sku"/> for nulo.</exception>
    /// <exception cref="ArgumentOutOfRangeException">Se <paramref name="quantidade"/> for menor ou igual a zero.</exception>
    /// <exception cref="InvalidOperationException">Se o saldo resultante ultrapassar <see cref="LimitePorSku"/>.</exception>
    public void Repor(string sku, int quantidade)
    {
        ArgumentNullException.ThrowIfNull(sku);
        if (quantidade <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(quantidade), "A quantidade deve ser maior que zero.");
        }

        lock (_trava)
        {
            _saldos.TryGetValue(sku, out var atual);
            var novo = (long)atual + quantidade;
            if (novo > LimitePorSku)
            {
                throw new InvalidOperationException(
                    $"O saldo de '{sku}' ficaria em {novo}, acima do limite de {LimitePorSku}.");
            }

            _saldos[sku] = (int)novo;
        }
    }

    /// <summary>
    /// Devolve o saldo atual do sku.
    /// </summary>
    /// <remarks>Não modifica seus argumentos nem a instância.</remarks>
    /// <param name="sku">Sku consultado; não pode ser nulo.</param>
    /// <returns>O saldo do sku; zero se o sku não existir.</returns>
    /// <exception cref="ArgumentNullException">Se <paramref name="sku"/> for nulo.</exception>
    public int Quantidade(string sku)
    {
        ArgumentNullException.ThrowIfNull(sku);

        lock (_trava)
        {
            return _saldos.TryGetValue(sku, out var saldo) ? saldo : 0;
        }
    }

    /// <summary>
    /// Reserva os itens na ordem recebida, debitando o saldo e acrescentando cada um a <paramref name="pedido"/>.
    /// </summary>
    /// <remarks>
    /// Modifica o saldo da instância e <c>pedido.Linhas</c>; não modifica <paramref name="itens"/>.
    /// Não é atômico: no primeiro erro a operação para, e os itens anteriores continuam
    /// debitados e presentes em <c>pedido.Linhas</c>. O item que falhou não altera saldo nem pedido.
    /// </remarks>
    /// <param name="itens">Itens a reservar; não pode ser nulo.</param>
    /// <param name="pedido">Pedido que recebe as linhas; não pode ser nulo.</param>
    /// <exception cref="ArgumentNullException">Se <paramref name="itens"/> ou <paramref name="pedido"/> for nulo.</exception>
    /// <exception cref="ArgumentOutOfRangeException">Se a quantidade de algum item for menor ou igual a zero.</exception>
    /// <exception cref="EstoqueInsuficienteException">Se o saldo de algum item for menor que a quantidade pedida.</exception>
    public void Reservar(IReadOnlyList<ItemReserva> itens, Pedido pedido)
    {
        ArgumentNullException.ThrowIfNull(itens);
        ArgumentNullException.ThrowIfNull(pedido);

        lock (_trava)
        {
            foreach (var item in itens)
            {
                if (item.Quantidade <= 0)
                {
                    throw new ArgumentOutOfRangeException(nameof(itens), "A quantidade de cada item deve ser maior que zero.");
                }

                _saldos.TryGetValue(item.Sku, out var saldo);
                if (saldo < item.Quantidade)
                {
                    throw new EstoqueInsuficienteException(item.Sku, item.Quantidade, saldo);
                }

                _saldos[item.Sku] = saldo - item.Quantidade;
                pedido.Linhas.Add(item);
            }
        }
    }

    /// <summary>
    /// Remove espaços das pontas, converte para maiúsculas e descarta os skus que ficarem vazios.
    /// </summary>
    /// <remarks>
    /// Modifica <paramref name="skus"/> no lugar, preservando a ordem dos que sobram. Não modifica a instância.
    /// </remarks>
    /// <param name="skus">Lista mutável de skus; não pode ser nula nem conter itens nulos.</param>
    /// <returns>Quantidade de skus removidos.</returns>
    /// <exception cref="ArgumentNullException">Se <paramref name="skus"/> for nula.</exception>
    /// <exception cref="NullReferenceException">Se algum item de <paramref name="skus"/> for nulo; itens anteriores já terão sido alterados.</exception>
    public int NormalizarSkus(List<string> skus)
    {
        ArgumentNullException.ThrowIfNull(skus);

        var removidos = 0;
        var escrita = 0;
        for (var leitura = 0; leitura < skus.Count; leitura++)
        {
            var normalizado = skus[leitura].Trim().ToUpperInvariant();
            if (normalizado.Length == 0)
            {
                removidos++;
                continue;
            }

            skus[escrita++] = normalizado;
        }

        skus.RemoveRange(escrita, skus.Count - escrita);
        return removidos;
    }
}
