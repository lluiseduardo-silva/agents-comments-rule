package estoque

import (
	"errors"
	"fmt"
	"strings"
	"sync"
)

var (
	ErrLimiteInvalido        = errors.New("limitePorSku deve ser maior que zero")
	ErrQuantidadeInvalida    = errors.New("quantidade deve ser maior que zero")
	ErrLimiteExcedido        = errors.New("saldo acima do limitePorSku")
	ErrEstoqueInsuficiente   = errors.New("estoque insuficiente")
)

// Item é uma linha de reserva: um sku e a quantidade desejada.
type Item struct {
	Sku        string
	Quantidade int
}

// Pedido é um objeto mutável que acumula as linhas reservadas.
type Pedido struct {
	Linhas []Item
}

// Estoque é um controle de estoque em memória, seguro para uso concorrente.
// O mutex cobre apenas a mutação de estado (sem I/O dentro da seção crítica).
type Estoque struct {
	mu           sync.Mutex
	limitePorSku int
	saldos       map[string]int
}

// NovoEstoque cria um Estoque; limitePorSku menor ou igual a zero é erro.
func NovoEstoque(limitePorSku int) (*Estoque, error) {
	if limitePorSku <= 0 {
		return nil, ErrLimiteInvalido
	}
	return &Estoque{limitePorSku: limitePorSku, saldos: make(map[string]int)}, nil
}

// Repor soma quantidade ao saldo do sku. Se o saldo resultante passar de
// limitePorSku, devolve erro e o saldo não muda.
func (e *Estoque) Repor(sku string, quantidade int) error {
	if quantidade <= 0 {
		return fmt.Errorf("repor %q: %w", sku, ErrQuantidadeInvalida)
	}
	e.mu.Lock()
	defer e.mu.Unlock()
	if e.saldos[sku]+quantidade > e.limitePorSku {
		return fmt.Errorf("repor %q: %w", sku, ErrLimiteExcedido)
	}
	e.saldos[sku] += quantidade
	return nil
}

// Quantidade devolve o saldo atual do sku; zero se não existir.
func (e *Estoque) Quantidade(sku string) int {
	e.mu.Lock()
	defer e.mu.Unlock()
	return e.saldos[sku]
}

// Reservar processa os itens na ordem, debitando o saldo e acrescentando cada
// item em pedido.Linhas. No primeiro erro para; os itens anteriores continuam
// debitados e em pedido.Linhas.
func (e *Estoque) Reservar(itens []Item, pedido *Pedido) error {
	e.mu.Lock()
	defer e.mu.Unlock()
	for _, it := range itens {
		if it.Quantidade <= 0 {
			return fmt.Errorf("reservar %q: %w", it.Sku, ErrQuantidadeInvalida)
		}
		if e.saldos[it.Sku] < it.Quantidade {
			return fmt.Errorf("reservar %q: %w", it.Sku, ErrEstoqueInsuficiente)
		}
		e.saldos[it.Sku] -= it.Quantidade
		pedido.Linhas = append(pedido.Linhas, it)
	}
	return nil
}

// NormalizarSkus altera a lista no lugar: tira espaços das pontas, converte
// para maiúsculas e remove os que ficarem vazios. Devolve quantos foram removidos.
func NormalizarSkus(skus *[]string) int {
	original := *skus
	escritos := 0
	for _, s := range original {
		s = strings.ToUpper(strings.TrimSpace(s))
		if s == "" {
			continue
		}
		original[escritos] = s
		escritos++
	}
	removidos := len(original) - escritos
	*skus = original[:escritos]
	return removidos
}
