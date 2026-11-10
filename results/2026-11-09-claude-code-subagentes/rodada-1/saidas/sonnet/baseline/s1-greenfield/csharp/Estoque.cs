using System;
using System.Collections.Generic;

public record ItemEstoque(string Sku, int Quantidade);

public class Pedido
{
    public List<ItemEstoque> Linhas { get; } = new();
}

public class QuantidadeInvalidaException : ArgumentException
{
    public QuantidadeInvalidaException(string sku, int quantidade)
        : base($"Quantidade invalida para o sku '{sku}': {quantidade}.") { }
}

public class EstoqueInsuficienteException : InvalidOperationException
{
    public EstoqueInsuficienteException(string sku, int solicitado, int disponivel)
        : base($"Estoque insuficiente para o sku '{sku}': solicitado {solicitado}, disponivel {disponivel}.") { }
}

public class Estoque
{
    private readonly int _limitePorSku;
    private readonly Dictionary<string, int> _saldos = new();
    private readonly object _trava = new();

    public Estoque(int limitePorSku)
    {
        if (limitePorSku <= 0)
            throw new ArgumentOutOfRangeException(nameof(limitePorSku), "O limite por sku deve ser maior que zero.");
        _limitePorSku = limitePorSku;
    }

    public void Repor(string sku, int quantidade)
    {
        ArgumentNullException.ThrowIfNull(sku);
        if (quantidade <= 0)
            throw new QuantidadeInvalidaException(sku, quantidade);

        lock (_trava)
        {
            _saldos.TryGetValue(sku, out var atual);
            // long evita overflow na soma; o saldo so muda se o limite for respeitado.
            if ((long)atual + quantidade > _limitePorSku)
                throw new InvalidOperationException(
                    $"Saldo do sku '{sku}' excederia o limite de {_limitePorSku}.");
            _saldos[sku] = atual + quantidade;
        }
    }

    public int Quantidade(string sku)
    {
        ArgumentNullException.ThrowIfNull(sku);
        lock (_trava)
        {
            return _saldos.TryGetValue(sku, out var saldo) ? saldo : 0;
        }
    }

    public void Reservar(IReadOnlyList<ItemEstoque> itens, Pedido pedido)
    {
        ArgumentNullException.ThrowIfNull(itens);
        ArgumentNullException.ThrowIfNull(pedido);

        // Verificacao e debito de cada item sao atomicos sob a mesma trava.
        // Em caso de erro, itens anteriores permanecem debitados e em pedido.Linhas.
        lock (_trava)
        {
            foreach (var item in itens)
            {
                if (item.Quantidade <= 0)
                    throw new QuantidadeInvalidaException(item.Sku, item.Quantidade);

                _saldos.TryGetValue(item.Sku, out var atual);
                if (atual < item.Quantidade)
                    throw new EstoqueInsuficienteException(item.Sku, item.Quantidade, atual);

                _saldos[item.Sku] = atual - item.Quantidade;
                pedido.Linhas.Add(item);
            }
        }
    }

    public int NormalizarSkus(List<string> skus)
    {
        ArgumentNullException.ThrowIfNull(skus);

        var escrita = 0;
        foreach (var sku in skus)
        {
            var normalizado = sku?.Trim().ToUpperInvariant();
            if (!string.IsNullOrEmpty(normalizado))
                skus[escrita++] = normalizado;
        }

        var removidos = skus.Count - escrita;
        skus.RemoveRange(escrita, removidos);
        return removidos;
    }
}
