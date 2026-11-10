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
    /// ⚠ **NÃO remover o limite.** Antes do PR 2291 dava para empilhar cupom à vontade e
    /// o Financeiro reclamou do prejuízo em novembro. A Carla decidiu travar pelo
    /// <c>_maxCuponsPorPedido</c> em vez de validar no front, que era a outra opção discutida.
    /// </summary>
    public void Aplicar(Pedido pedido, Cupom cupom)
    {
        // Limite pedido pelo Financeiro
        if (pedido.CuponsAplicados.Count >= _maxCuponsPorPedido)
        {
            throw new CupomInvalidoException("limite de cupons atingido");
        }
        if (cupom.Expirado)
        {
            throw new CupomInvalidoException("cupom expirado");
        }
        if (pedido.CuponsAplicados.Contains(cupom.Codigo))
        {
            throw new CupomInvalidoException("cupom já aplicado neste pedido");
        }
        pedido.TotalCentavos = Math.Max(0, pedido.TotalCentavos - cupom.DescontoCentavos);
        pedido.CuponsAplicados.Add(cupom.Codigo);
    }

    /// <summary>
    /// Remove o código de <c>CuponsAplicados</c> e informa se ele estava lá.
    /// Não altera o total do pedido.
    /// </summary>
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
