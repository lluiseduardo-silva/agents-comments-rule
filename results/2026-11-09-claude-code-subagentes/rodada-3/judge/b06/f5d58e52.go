package cupons

import (
	"errors"
	"fmt"
)

var ErrCupomInvalido = errors.New("cupom inválido")

type Cupom struct {
	Codigo           string
	DescontoCentavos int64
	Expirado         bool
}

type Pedido struct {
	TotalCentavos   int64
	CuponsAplicados []string
}

// CupomService foi criado depois do incidente da Black Friday (ticket PAG-1187), quando
// o cálculo de desconto ficava espalhado pelos handlers e o time de Checkout pediu para
// centralizar tudo aqui.
type CupomService struct {
	maxCuponsPorPedido int
}

func NewCupomService(maxCuponsPorPedido int) *CupomService {
	return &CupomService{maxCuponsPorPedido: maxCuponsPorPedido}
}

// Aplicar aplica o desconto de cupom ao pedido: um cupom expirado, um cupom já aplicado
// ao pedido ou o excesso de cupons além do máximo do serviço são rejeitados, e o total
// do pedido nunca fica abaixo de zero.
//
// Modifica pedido in-place: subtrai o desconto de TotalCentavos (travando em zero) e
// acrescenta o código do cupom ao final de CuponsAplicados. Em caso de erro, pedido não
// é alterado. Não modifica cupom nem o estado do serviço.
//
// Parâmetros:
//   - pedido: pedido que recebe o cupom; não pode ser nil.
//   - cupom: cupom a aplicar; Expirado indica que não pode mais ser usado e
//     DescontoCentavos é o desconto em centavos.
//
// Retorna nil quando o cupom foi aplicado.
//
// Erros: retorna erro que envolve ErrCupomInvalido (use errors.Is) se cupom.Expirado for
// verdadeiro, se cupom.Codigo já estiver em pedido.CuponsAplicados, ou se o pedido já
// tiver maxCuponsPorPedido cupons aplicados.
func (s *CupomService) Aplicar(pedido *Pedido, cupom Cupom) error {
	if cupom.Expirado {
		return fmt.Errorf("%w: cupom expirado", ErrCupomInvalido)
	}
	for _, codigo := range pedido.CuponsAplicados {
		if codigo == cupom.Codigo {
			return fmt.Errorf("%w: cupom já aplicado ao pedido", ErrCupomInvalido)
		}
	}
	if len(pedido.CuponsAplicados) >= s.maxCuponsPorPedido {
		return fmt.Errorf("%w: limite de cupons atingido", ErrCupomInvalido)
	}
	pedido.TotalCentavos -= cupom.DescontoCentavos
	if pedido.TotalCentavos < 0 {
		pedido.TotalCentavos = 0
	}
	pedido.CuponsAplicados = append(pedido.CuponsAplicados, cupom.Codigo)
	return nil
}

// Remover retira o código de cupom da lista de cupons aplicados do pedido e informa se
// ele estava presente.
//
// Modifica pedido in-place: remove a ocorrência de codigo em CuponsAplicados, mantendo a
// ordem dos demais, e reaproveita o array subjacente da lista. Não altera
// TotalCentavos nem o estado do serviço. Se codigo não estiver na lista, nada é
// alterado.
//
// Parâmetros:
//   - pedido: pedido do qual o cupom é removido; não pode ser nil.
//   - codigo: código do cupom a remover.
//
// Retorna true se codigo estava em CuponsAplicados e foi removido, false caso contrário.
func (s *CupomService) Remover(pedido *Pedido, codigo string) bool {
	for i, c := range pedido.CuponsAplicados {
		if c == codigo {
			pedido.CuponsAplicados = append(pedido.CuponsAplicados[:i], pedido.CuponsAplicados[i+1:]...)
			return true
		}
	}
	return false
}

// Movido do PedidoController no refactor de março (PAG-1203). O Diego do time de
// Plataforma achou melhor somar aqui porque o relatório antigo contava errado.
func (s *CupomService) TotalDeCupons(pedidos []Pedido) int {
	// Antes isso era um loop manual
	total := 0
	for _, p := range pedidos {
		total += len(p.CuponsAplicados)
	}
	return total
}
