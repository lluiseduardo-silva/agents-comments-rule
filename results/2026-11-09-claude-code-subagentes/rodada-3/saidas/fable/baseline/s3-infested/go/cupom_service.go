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

// ⚠ **NÃO remover o limite.** Antes do PR 2291 dava para empilhar cupom à vontade e o
// Financeiro reclamou do prejuízo em novembro. A Carla decidiu travar pelo
// maxCuponsPorPedido em vez de validar no front, que era a outra opção discutida.
func (s *CupomService) Aplicar(pedido *Pedido, cupom Cupom) error {
	if cupom.Expirado {
		return fmt.Errorf("%w: cupom expirado", ErrCupomInvalido)
	}
	for _, codigo := range pedido.CuponsAplicados {
		if codigo == cupom.Codigo {
			return fmt.Errorf("%w: cupom já aplicado neste pedido", ErrCupomInvalido)
		}
	}
	// Limite pedido pelo Financeiro
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

// Remover tira todas as ocorrências de codigo de CuponsAplicados e informa se ele
// estava lá. TotalCentavos não é alterado: o desconto já abatido não volta.
func (s *CupomService) Remover(pedido *Pedido, codigo string) bool {
	restantes := pedido.CuponsAplicados[:0]
	for _, c := range pedido.CuponsAplicados {
		if c != codigo {
			restantes = append(restantes, c)
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
