using System;
using System.Collections.Generic;

/// <summary>
/// Item de uma reserva: um sku e a quantidade desejada.
/// </summary>
/// <param name="Sku">Identificador do produto.</param>
/// <param name="Quantidade">Quantidade do item; deve ser maior que zero para ser reservada.</param>
public record ItemReserva(string Sku, int Quantidade);

/// <summary>
/// Pedido mutável que acumula as linhas reservadas no estoque.
/// </summary>
public class Pedido
{
    /// <summary>
    /// Linhas do pedido, na ordem em que foram reservadas.
    /// </summary>
    public List<ItemReserva> Linhas { get; } = new List<ItemReserva>();
}

/// <summary>
/// Erro de quantidade menor ou igual a zero.
/// </summary>
public class QuantidadeInvalidaException : Exception
{
    /// <summary>
    /// Cria o erro com a mensagem indicada.
    /// </summary>
    /// <param name="mensagem">Descrição do erro.</param>
    public QuantidadeInvalidaException(string mensagem) : base(mensagem) { }
}

/// <summary>
/// Erro de saldo menor que a quantidade solicitada.
/// </summary>
public class EstoqueInsuficienteException : Exception
{
    /// <summary>
    /// Cria o erro com a mensagem indicada.
    /// </summary>
    /// <param name="mensagem">Descrição do erro.</param>
    public EstoqueInsuficienteException(string mensagem) : base(mensagem) { }
}

/// <summary>
/// Controle de estoque em memória, com saldo por sku limitado por <c>limitePorSku</c>.
/// </summary>
public class Estoque
{
    private readonly int _limitePorSku;
    private readonly Dictionary<string, int> _saldos = new Dictionary<string, int>();

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
        _limitePorSku = limitePorSku;
    }

    /// <summary>
    /// Soma a quantidade ao saldo do sku.
    /// </summary>
    /// <remarks>
    /// Modifica o saldo do sku na instância. Se lançar exceção, o saldo não é alterado.
    /// </remarks>
    /// <param name="sku">Identificador do produto; não pode ser nulo.</param>
    /// <param name="quantidade">Quantidade a somar; deve ser maior que zero.</param>
    /// <exception cref="QuantidadeInvalidaException">Se <paramref name="quantidade"/> for menor ou igual a zero.</exception>
    /// <exception cref="InvalidOperationException">Se o saldo resultante ultrapassar o limite por sku.</exception>
    public void Repor(string sku, int quantidade)
    {
        if (quantidade <= 0)
        {
            throw new QuantidadeInvalidaException("A quantidade deve ser maior que zero.");
        }
        long novoSaldo = (long)Quantidade(sku) + quantidade;
        if (novoSaldo > _limitePorSku)
        {
            throw new InvalidOperationException("O saldo resultante ultrapassa o limite por sku.");
        }
        _saldos[sku] = (int)novoSaldo;
    }

    /// <summary>
    /// Devolve o saldo atual do sku.
    /// </summary>
    /// <remarks>
    /// Não modifica seus argumentos nem a instância.
    /// </remarks>
    /// <param name="sku">Identificador do produto; não pode ser nulo.</param>
    /// <returns>O saldo do sku, ou zero se o sku não existir.</returns>
    public int Quantidade(string sku)
    {
        return _saldos.TryGetValue(sku, out int saldo) ? saldo : 0;
    }

    /// <summary>
    /// Debita do saldo cada item, na ordem, e o acrescenta às linhas do pedido.
    /// </summary>
    /// <remarks>
    /// Modifica os saldos da instância e <c>pedido.Linhas</c>. Se um item falhar, a operação
    /// para: os itens anteriores permanecem debitados e presentes em <c>pedido.Linhas</c>, e
    /// o item que falhou e os seguintes não alteram saldo nem pedido. Não modifica
    /// <paramref name="itens"/>.
    /// </remarks>
    /// <param name="itens">Itens a reservar, processados na ordem; não pode ser nulo.</param>
    /// <param name="pedido">Pedido que recebe as linhas; não pode ser nulo.</param>
    /// <exception cref="QuantidadeInvalidaException">Se a quantidade de algum item for menor ou igual a zero.</exception>
    /// <exception cref="EstoqueInsuficienteException">Se o saldo de algum item for menor que a quantidade pedida.</exception>
    public void Reservar(IEnumerable<ItemReserva> itens, Pedido pedido)
    {
        foreach (ItemReserva item in itens)
        {
            if (item.Quantidade <= 0)
            {
                throw new QuantidadeInvalidaException("A quantidade deve ser maior que zero.");
            }
            int saldo = Quantidade(item.Sku);
            if (saldo < item.Quantidade)
            {
                throw new EstoqueInsuficienteException("Estoque insuficiente para o sku " + item.Sku + ".");
            }
            _saldos[item.Sku] = saldo - item.Quantidade;
            pedido.Linhas.Add(item);
        }
    }

    /// <summary>
    /// Remove espaços das pontas de cada sku, converte para maiúsculas e remove os que ficarem vazios.
    /// </summary>
    /// <remarks>
    /// Modifica <paramref name="skus"/> no lugar: substitui os elementos pelo valor normalizado
    /// e remove os vazios. Não modifica a instância.
    /// </remarks>
    /// <param name="skus">Lista mutável de textos; não pode ser nula nem conter elementos nulos.</param>
    /// <returns>A quantidade de elementos removidos.</returns>
    public int NormalizarSkus(List<string> skus)
    {
        for (int i = 0; i < skus.Count; i++)
        {
            skus[i] = skus[i].Trim().ToUpperInvariant();
        }
        return skus.RemoveAll(sku => sku.Length == 0);
    }
}
