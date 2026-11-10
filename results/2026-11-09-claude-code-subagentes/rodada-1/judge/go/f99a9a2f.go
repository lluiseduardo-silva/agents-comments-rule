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

// Aplicar aplica o cupom ao pedido: um cupom expirado, um cupom já aplicado ao pedido ou
// um pedido que já atingiu maxCuponsPorPedido são rejeitados, e o total do pedido nunca
// fica abaixo de zero.
//
// Em caso de sucesso, modifica o pedido apontado por pedido: subtrai o desconto de
// TotalCentavos (travando em zero) e acrescenta o código a CuponsAplicados. Em caso de
// erro, o pedido não é alterado. Não modifica o cupom nem o estado do serviço.
//
// pedido deve ser não nulo. cupom é o cupom a aplicar; Codigo identifica o cupom no
// pedido e Expirado indica que ele não pode mais ser usado.
//
// Retorna nil quando o cupom foi aplicado.
//
// Retorna um erro que satisfaz errors.Is(err, ErrCupomInvalido) quando o cupom está
// expirado, quando seu Codigo já consta em pedido.CuponsAplicados ou quando
// len(pedido.CuponsAplicados) já alcançou maxCuponsPorPedido.
func (s *CupomService) Aplicar(pedido *Pedido, cupom Cupom) error {
	if cupom.Expirado {
		return fmt.Errorf("%w: cupom expirado", ErrCupomInvalido)
	}
	if indiceDoCupom(pedido, cupom.Codigo) >= 0 {
		return fmt.Errorf("%w: cupom já aplicado ao pedido", ErrCupomInvalido)
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

// Remover tira codigo de pedido.CuponsAplicados e informa se ele estava lá.
//
// Modifica o pedido apontado por pedido: quando o código existe, ele é removido de
// CuponsAplicados, preservando a ordem dos demais, e o array subjacente da fatia é
// reaproveitado. Não altera TotalCentavos, não modifica o estado do serviço e, quando o
// código não existe, não altera nada.
//
// pedido deve ser não nulo. codigo é o código do cupom a remover.
//
// Retorna true se o código estava em CuponsAplicados e foi removido; false se não estava.
func (s *CupomService) Remover(pedido *Pedido, codigo string) bool {
	i := indiceDoCupom(pedido, codigo)
	if i < 0 {
		return false
	}
	pedido.CuponsAplicados = append(pedido.CuponsAplicados[:i], pedido.CuponsAplicados[i+1:]...)
	return true
}

// indiceDoCupom devolve a posição de codigo em pedido.CuponsAplicados, ou -1 se ele não
// estiver lá. Não modifica o pedido. pedido deve ser não nulo.
func indiceDoCupom(pedido *Pedido, codigo string) int {
	for i, c := range pedido.CuponsAplicados {
		if c == codigo {
			return i
		}
	}
	return -1
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
