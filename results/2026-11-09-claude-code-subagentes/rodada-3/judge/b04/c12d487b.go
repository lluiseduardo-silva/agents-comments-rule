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

// Aplicar desconta o valor de cupom do total de pedido e registra o código do cupom
// como aplicado. O total resultante nunca fica abaixo de zero: um desconto maior que o
// total deixa o total em zero.
//
// Em caso de sucesso, modifica pedido: TotalCentavos recebe o novo total e o código
// do cupom é acrescentado ao final de CuponsAplicados. Em caso de erro, pedido não é
// alterado. Não modifica cupom nem o estado do serviço.
//
// Parâmetros:
//   - pedido: pedido que recebe o desconto; não pode ser nil.
//   - cupom: cupom a aplicar; DescontoCentavos é o valor descontado, em centavos.
//
// Retorna nil quando o cupom foi aplicado. Retorna um erro que satisfaz
// errors.Is(err, ErrCupomInvalido) quando:
//   - o cupom está expirado;
//   - o código do cupom já está em CuponsAplicados;
//   - pedido já tem maxCuponsPorPedido cupons aplicados.
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

// Remover tira o código informado da lista de cupons aplicados de pedido.
//
// Modifica pedido.CuponsAplicados: todas as ocorrências de codigo são removidas,
// preservando a ordem dos demais códigos e reaproveitando o array subjacente da
// slice. Não altera pedido.TotalCentavos, ou seja, o desconto já aplicado continua
// no total. Não modifica o estado do serviço.
//
// Parâmetros:
//   - pedido: pedido do qual o código é removido; não pode ser nil.
//   - codigo: código do cupom a remover; a comparação é exata.
//
// Retorna true se codigo estava em CuponsAplicados e false caso contrário, situação
// em que pedido não é alterado.
func (s *CupomService) Remover(pedido *Pedido, codigo string) bool {
	restantes := pedido.CuponsAplicados[:0]
	removido := false
	for _, c := range pedido.CuponsAplicados {
		if c == codigo {
			removido = true
			continue
		}
		restantes = append(restantes, c)
	}
	if removido {
		pedido.CuponsAplicados = restantes
	}
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
