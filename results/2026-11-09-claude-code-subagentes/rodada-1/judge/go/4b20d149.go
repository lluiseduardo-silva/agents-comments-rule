package estoque

import (
	"errors"
	"strings"
	"sync"
)

var (
	// ErrLimiteInvalido ocorre quando o limite por sku informado é menor ou igual a zero.
	ErrLimiteInvalido = errors.New("estoque: limite por sku deve ser maior que zero")

	// ErrQuantidadeInvalida ocorre quando uma quantidade informada é menor ou igual a zero.
	ErrQuantidadeInvalida = errors.New("estoque: quantidade deve ser maior que zero")

	// ErrLimiteExcedido ocorre quando uma reposição levaria o saldo do sku acima do limite.
	ErrLimiteExcedido = errors.New("estoque: saldo resultante excede o limite por sku")

	// ErrEstoqueInsuficiente ocorre quando o saldo do sku é menor que a quantidade reservada.
	ErrEstoqueInsuficiente = errors.New("estoque: estoque insuficiente")
)

// Item é uma quantidade de um sku, usada em reservas e registrada nas linhas de um pedido.
//
// Sku identifica o produto e Quantidade é o número de unidades.
type Item struct {
	Sku        string
	Quantidade int
}

// Pedido acumula os itens reservados para uma compra.
//
// Linhas guarda os itens na ordem em que foram reservados. O tipo não é seguro para uso
// concorrente.
type Pedido struct {
	Linhas []Item
}

// Estoque controla em memória o saldo de unidades por sku, com um limite máximo por sku.
//
// Os métodos são seguros para uso concorrente; cada operação é atômica em relação às
// demais chamadas ao mesmo Estoque. O valor zero não é utilizável: crie com NovoEstoque.
type Estoque struct {
	mu          sync.Mutex
	limitePorSku int
	saldos      map[string]int
}

// NovoEstoque cria um Estoque vazio cujo saldo de cada sku nunca excede limitePorSku.
//
// Não modifica nenhum estado externo.
//
// O parâmetro limitePorSku é o saldo máximo permitido por sku e deve ser maior que zero.
//
// Devolve ErrLimiteInvalido se limitePorSku for menor ou igual a zero.
func NovoEstoque(limitePorSku int) (*Estoque, error) {
	if limitePorSku <= 0 {
		return nil, ErrLimiteInvalido
	}
	return &Estoque{limitePorSku: limitePorSku, saldos: make(map[string]int)}, nil
}

// Repor soma quantidade ao saldo de sku.
//
// Modifica o saldo de sku no Estoque. Se retornar erro, nenhum saldo é alterado.
//
// O parâmetro sku identifica o produto; quantidade é o número de unidades a somar e deve
// ser maior que zero.
//
// Devolve ErrQuantidadeInvalida se quantidade for menor ou igual a zero e
// ErrLimiteExcedido se o saldo resultante ficaria acima do limite por sku.
func (e *Estoque) Repor(sku string, quantidade int) error {
	if quantidade <= 0 {
		return ErrQuantidadeInvalida
	}

	e.mu.Lock()
	defer e.mu.Unlock()

	// Comparar com a folga evita overflow de inteiro em saldo+quantidade.
	if quantidade > e.limitePorSku-e.saldos[sku] {
		return ErrLimiteExcedido
	}
	e.saldos[sku] += quantidade
	return nil
}

// Quantidade devolve o saldo atual de sku.
//
// Não modifica seus argumentos nem o Estoque.
//
// O parâmetro sku identifica o produto. Devolve zero se o sku nunca recebeu reposição.
func (e *Estoque) Quantidade(sku string) int {
	e.mu.Lock()
	defer e.mu.Unlock()

	return e.saldos[sku]
}

// Reservar debita do saldo, na ordem, cada item de itens e o acrescenta a pedido.Linhas.
//
// Modifica o Estoque (saldos debitados) e pedido (Linhas ganha um item por reserva
// concluída). Não modifica itens. A operação para no primeiro erro: os itens anteriores
// continuam debitados e presentes em pedido.Linhas, e o item que falhou e os seguintes
// não são alterados. A operação inteira é atômica em relação às demais chamadas ao mesmo
// Estoque, mas pedido não é sincronizado.
//
// O parâmetro itens é a lista de reservas; cada Quantidade deve ser maior que zero.
// O parâmetro pedido recebe as linhas reservadas e não pode ser nil.
//
// Devolve ErrQuantidadeInvalida se a quantidade de um item for menor ou igual a zero e
// ErrEstoqueInsuficiente se o saldo do sku do item for menor que a quantidade pedida.
func (e *Estoque) Reservar(itens []Item, pedido *Pedido) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	for _, item := range itens {
		if item.Quantidade <= 0 {
			return ErrQuantidadeInvalida
		}
		if e.saldos[item.Sku] < item.Quantidade {
			return ErrEstoqueInsuficiente
		}
		e.saldos[item.Sku] -= item.Quantidade
		pedido.Linhas = append(pedido.Linhas, item)
	}
	return nil
}

// NormalizarSkus tira os espaços das pontas de cada sku, converte para maiúsculas e
// remove os que ficarem vazios, preservando a ordem dos demais.
//
// Modifica *skus no lugar: o slice é reescrito sobre o mesmo array e encurtado, e as
// posições além do novo tamanho são zeradas. Não modifica nenhum outro estado.
//
// O parâmetro skus aponta para a lista a normalizar e não pode ser nil.
//
// Devolve a quantidade de skus removidos.
func NormalizarSkus(skus *[]string) int {
	lista := *skus
	escritos := 0
	for _, sku := range lista {
		normalizado := strings.ToUpper(strings.TrimSpace(sku))
		if normalizado == "" {
			continue
		}
		lista[escritos] = normalizado
		escritos++
	}
	removidos := len(lista) - escritos
	clear(lista[escritos:])
	*skus = lista[:escritos]
	return removidos
}
