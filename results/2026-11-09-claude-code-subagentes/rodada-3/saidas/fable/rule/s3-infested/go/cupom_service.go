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

// Aplicar aplica cupom a pedido: subtrai o desconto do total, que trava em zero e nunca
// fica negativo, e registra o código entre os cupons aplicados. Cupom expirado não é
// aceito, o mesmo código não é aceito duas vezes no mesmo pedido, e um pedido aceita no
// máximo o limite de cupons configurado em NewCupomService.
//
// Modifica pedido: TotalCentavos é reduzido em cupom.DescontoCentavos, limitado a zero, e
// cupom.Codigo é acrescentado ao fim de CuponsAplicados. Quando devolve erro, pedido fica
// inalterado. Não modifica o CupomService.
//
// O parâmetro pedido é o pedido que recebe o desconto e não pode ser nil. O parâmetro
// cupom é o cupom a aplicar: DescontoCentavos está em centavos e deve ser maior ou igual
// a zero, o que não é validado (um desconto negativo aumenta o total); Codigo vazio é
// tratado como qualquer outro código.
//
// Devolve nil quando o cupom foi aplicado. Devolve um erro que satisfaz
// errors.Is(err, ErrCupomInvalido) quando:
//   - pedido tem o limite de cupons ou mais em CuponsAplicados;
//   - cupom.Expirado é true;
//   - cupom.Codigo consta em pedido.CuponsAplicados.
//
// Entra em pânico se pedido ou o CupomService for nil.
func (s *CupomService) Aplicar(pedido *Pedido, cupom Cupom) error {
	if len(pedido.CuponsAplicados) >= s.maxCuponsPorPedido {
		return fmt.Errorf("%w: limite de cupons atingido", ErrCupomInvalido)
	}
	if cupom.Expirado {
		return fmt.Errorf("%w: cupom expirado", ErrCupomInvalido)
	}
	for _, aplicado := range pedido.CuponsAplicados {
		if aplicado == cupom.Codigo {
			return fmt.Errorf("%w: cupom já aplicado ao pedido", ErrCupomInvalido)
		}
	}
	pedido.TotalCentavos -= cupom.DescontoCentavos
	if pedido.TotalCentavos < 0 {
		pedido.TotalCentavos = 0
	}
	pedido.CuponsAplicados = append(pedido.CuponsAplicados, cupom.Codigo)
	return nil
}

// Remover retira codigo dos cupons aplicados a pedido e informa se ele estava lá. O total
// do pedido não é recalculado: o desconto concedido pelo cupom permanece.
//
// Modifica pedido: todas as ocorrências de codigo saem de CuponsAplicados, reescrevendo o
// array subjacente do slice, e a ordem dos demais códigos é preservada. Não altera
// pedido.TotalCentavos nem o CupomService.
//
// O parâmetro pedido é o pedido de onde o código é retirado e não pode ser nil. O
// parâmetro codigo é o código do cupom a retirar, comparado de forma exata; a string
// vazia é comparada como qualquer outro código.
//
// Devolve true se codigo estava em pedido.CuponsAplicados e foi retirado, e false se não
// estava, caso em que pedido fica inalterado.
//
// Entra em pânico se pedido for nil.
func (s *CupomService) Remover(pedido *Pedido, codigo string) bool {
	restantes := pedido.CuponsAplicados[:0]
	for _, aplicado := range pedido.CuponsAplicados {
		if aplicado != codigo {
			restantes = append(restantes, aplicado)
		}
	}
	removido := len(restantes) != len(pedido.CuponsAplicados)
	pedido.CuponsAplicados = restantes
	return removido
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
