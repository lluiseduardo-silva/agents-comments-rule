using System;
using System.Collections.Generic;
using System.Linq;

namespace Cupons;

public class CupomInvalidoException : Exception
{
    public CupomInvalidoException(string mensagem) : base(mensagem) { }
}

public record Cupom(string Codigo, long DescontoCentavos, bool Expirado);

public class Pedido
{
    public long TotalCentavos { get; set; }
    public List<string> CuponsAplicados { get; } = new();
}

/// <summary>
/// Criado depois do incidente da Black Friday (ticket PAG-1187), quando o cálculo de
/// desconto ficava espalhado pelos controllers e o time de Checkout pediu para
/// centralizar tudo aqui.
/// </summary>
public class CupomService
{
    private readonly int _maxCuponsPorPedido;

    public CupomService(int maxCuponsPorPedido)
    {
        _maxCuponsPorPedido = maxCuponsPorPedido;
    }

    /// <summary>
    /// Aplica o cupom ao pedido: um cupom expirado, repetido no pedido ou além do limite de
    /// cupons por pedido é rejeitado, e o total nunca fica abaixo de zero.
    /// </summary>
    /// <remarks>
    /// Modifica <paramref name="pedido"/>: subtrai o desconto de <c>TotalCentavos</c> (travando
    /// em zero) e adiciona o código a <c>CuponsAplicados</c>. Quando lança exceção, o pedido
    /// não é alterado. Não modifica <paramref name="cupom"/> nem o estado da instância.
    /// </remarks>
    /// <param name="pedido">Pedido que recebe o cupom; não pode ser nulo.</param>
    /// <param name="cupom">Cupom a aplicar; não pode ser nulo.</param>
    /// <exception cref="CupomInvalidoException">
    /// Se o cupom estiver expirado, se o mesmo código já estiver aplicado ao pedido, ou se o
    /// pedido já tiver o número máximo de cupons.
    /// </exception>
    public void Aplicar(Pedido pedido, Cupom cupom)
    {
        if (cupom.Expirado)
        {
            throw new CupomInvalidoException("cupom expirado");
        }
        if (pedido.CuponsAplicados.Contains(cupom.Codigo))
        {
            throw new CupomInvalidoException("cupom já aplicado ao pedido");
        }
        if (pedido.CuponsAplicados.Count >= _maxCuponsPorPedido)
        {
            throw new CupomInvalidoException("limite de cupons atingido");
        }
        pedido.TotalCentavos = Math.Max(0, pedido.TotalCentavos - cupom.DescontoCentavos);
        pedido.CuponsAplicados.Add(cupom.Codigo);
    }

    /// <summary>
    /// Remove o código de cupom da lista de cupons aplicados do pedido.
    /// </summary>
    /// <remarks>
    /// Modifica <paramref name="pedido"/>: retira o código de <c>CuponsAplicados</c> quando
    /// presente. Não altera <c>TotalCentavos</c> nem o estado da instância.
    /// </remarks>
    /// <param name="pedido">Pedido do qual o cupom é removido; não pode ser nulo.</param>
    /// <param name="codigo">Código do cupom a remover.</param>
    /// <returns><c>true</c> se o código estava aplicado e foi removido; <c>false</c> caso contrário.</returns>
    public bool Remover(Pedido pedido, string codigo)
    {
        return pedido.CuponsAplicados.Remove(codigo);
    }

    /// <summary>
    /// Movido do PedidoController no refactor de março (PAG-1203). O Diego do time de
    /// Plataforma achou melhor somar aqui porque o relatório antigo contava errado.
    /// </summary>
    public int TotalDeCupons(IEnumerable<Pedido> pedidos)
    {
        // Antes isso era um loop manual
        return pedidos.Sum(p => p.CuponsAplicados.Count);
    }
}
