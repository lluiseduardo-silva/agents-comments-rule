package estoque

import (
	"errors"
	"fmt"
	"strings"
	"sync"
)

// ErrLimiteInvalido indica que o limite por sku informado é menor ou igual a zero.
var ErrLimiteInvalido = errors.New("limite por sku deve ser maior que zero")

// ErrQuantidadeInvalida indica que a quantidade informada é menor ou igual a zero.
var ErrQuantidadeInvalida = errors.New("quantidade deve ser maior que zero")

// ErrLimiteExcedido indica que o saldo resultante de uma reposição ultrapassaria o limite por sku.
var ErrLimiteExcedido = errors.New("saldo resultante excede o limite por sku")

// ErrEstoqueInsuficiente indica que o saldo do sku é menor que a quantidade pedida.
var ErrEstoqueInsuficiente = errors.New("estoque insuficiente")

// Item é uma linha de reserva: um sku e a quantidade desejada dele.
type Item struct {
	// Sku identifica o produto.
	Sku string
	// Quantidade é o número de unidades; deve ser maior que zero para ser aceita.
	Quantidade int
}

// Pedido acumula os itens reservados.
type Pedido struct {
	// Linhas contém os itens já reservados, na ordem em que foram reservados.
	Linhas []Item
}

// Estoque é um controle de saldo por sku, em memória, seguro para uso concorrente.
//
// Cada sku tem saldo entre zero e o limite por sku definido na criação. Todas as
// operações são serializadas por um único mutex, que cobre apenas a leitura e a
// alteração de memória.
type Estoque struct {
	mu           sync.Mutex
	limitePorSku int
	saldos       map[string]int
}

// NovoEstoque cria um Estoque vazio com o limite de saldo por sku informado.
//
// Parâmetros:
//   - limitePorSku: saldo máximo de cada sku; deve ser maior que zero.
//
// Retorna o novo Estoque, ou nil junto com o erro.
//
// Erros:
//   - ErrLimiteInvalido: se limitePorSku for menor ou igual a zero.
func NovoEstoque(limitePorSku int) (*Estoque, error) {
	if limitePorSku <= 0 {
		return nil, ErrLimiteInvalido
	}
	return &Estoque{limitePorSku: limitePorSku, saldos: make(map[string]int)}, nil
}

// Repor soma quantidade ao saldo de sku.
//
// Modifica o saldo de sku no Estoque. Se retornar erro, o saldo não muda.
//
// Parâmetros:
//   - sku: identificador do produto; um sku ainda desconhecido começa com saldo zero.
//   - quantidade: unidades a somar; deve ser maior que zero.
//
// Erros:
//   - ErrQuantidadeInvalida: se quantidade for menor ou igual a zero.
//   - ErrLimiteExcedido: se o saldo resultante ficar acima do limite por sku.
func (e *Estoque) Repor(sku string, quantidade int) error {
	if quantidade <= 0 {
		return ErrQuantidadeInvalida
	}
	e.mu.Lock()
	defer e.mu.Unlock()
	// Comparação feita por subtração para não estourar int na soma.
	if quantidade > e.limitePorSku-e.saldos[sku] {
		return ErrLimiteExcedido
	}
	e.saldos[sku] += quantidade
	return nil
}

// Quantidade devolve o saldo atual de sku.
//
// Não modifica seus argumentos nem a instância.
//
// Parâmetros:
//   - sku: identificador do produto.
//
// Retorna o saldo de sku, ou zero se o sku não existir.
func (e *Estoque) Quantidade(sku string) int {
	e.mu.Lock()
	defer e.mu.Unlock()
	return e.saldos[sku]
}

// Reservar debita do saldo cada item de itens, na ordem, e o acrescenta a pedido.Linhas.
//
// Modifica o saldo de cada sku reservado e pedido.Linhas. Para no primeiro erro: os
// itens anteriores continuam debitados e continuam em pedido.Linhas, e o item com
// erro e os seguintes não são debitados nem acrescentados. Não modifica itens.
//
// Parâmetros:
//   - itens: itens a reservar, processados na ordem.
//   - pedido: pedido que recebe as linhas; não pode ser nil.
//
// Erros:
//   - ErrQuantidadeInvalida: se a quantidade de algum item for menor ou igual a zero.
//   - ErrEstoqueInsuficiente: se o saldo de algum sku for menor que a quantidade do item.
//
// Ambos os erros vêm embrulhados com o sku do item; use errors.Is para identificá-los.
func (e *Estoque) Reservar(itens []Item, pedido *Pedido) error {
	e.mu.Lock()
	defer e.mu.Unlock()
	for _, item := range itens {
		if item.Quantidade <= 0 {
			return fmt.Errorf("sku %q: %w", item.Sku, ErrQuantidadeInvalida)
		}
		if e.saldos[item.Sku] < item.Quantidade {
			return fmt.Errorf("sku %q: %w", item.Sku, ErrEstoqueInsuficiente)
		}
		e.saldos[item.Sku] -= item.Quantidade
		pedido.Linhas = append(pedido.Linhas, item)
	}
	return nil
}

// NormalizarSkus tira os espaços das pontas de cada sku, converte para maiúsculas e
// remove os que ficarem vazios.
//
// Modifica o array subjacente de skus: a lista é compactada no lugar, e as posições
// além do novo tamanho ficam com texto vazio. O slice do chamador mantém o tamanho
// original; use len(skus)-removidos para obter o trecho válido. Não modifica o estado
// de nenhum Estoque.
//
// Parâmetros:
//   - skus: lista de skus a normalizar; a ordem dos que sobram é preservada.
//
// Retorna a quantidade de skus removidos por ficarem vazios.
func NormalizarSkus(skus []string) int {
	escritos := 0
	for _, sku := range skus {
		normalizado := strings.ToUpper(strings.TrimSpace(sku))
		if normalizado == "" {
			continue
		}
		skus[escritos] = normalizado
		escritos++
	}
	removidos := len(skus) - escritos
	for i := escritos; i < len(skus); i++ {
		skus[i] = ""
	}
	return removidos
}
