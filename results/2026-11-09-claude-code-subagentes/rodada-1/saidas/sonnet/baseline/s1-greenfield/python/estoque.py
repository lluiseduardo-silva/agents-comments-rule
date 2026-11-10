"""Controle de estoque em memória."""

import threading


class EstoqueError(Exception):
    """Erro base do controle de estoque."""


class QuantidadeInvalidaError(EstoqueError):
    """Quantidade menor ou igual a zero."""


class LimiteExcedidoError(EstoqueError):
    """Saldo resultante acima de limite_por_sku."""


class EstoqueInsuficienteError(EstoqueError):
    """Saldo menor que a quantidade pedida."""


class Estoque:
    def __init__(self, limite_por_sku: int):
        if limite_por_sku <= 0:
            raise ValueError("limite_por_sku deve ser maior que zero")
        self._limite_por_sku = limite_por_sku
        self._saldos: dict[str, int] = {}
        # Leitura, decisão e escrita do saldo ocorrem sob o mesmo lock.
        self._lock = threading.Lock()

    def repor(self, sku: str, quantidade: int) -> None:
        if quantidade <= 0:
            raise QuantidadeInvalidaError(f"quantidade inválida: {quantidade}")
        with self._lock:
            novo_saldo = self._saldos.get(sku, 0) + quantidade
            if novo_saldo > self._limite_por_sku:
                raise LimiteExcedidoError(
                    f"saldo {novo_saldo} acima do limite {self._limite_por_sku} para {sku}"
                )
            self._saldos[sku] = novo_saldo

    def quantidade(self, sku: str) -> int:
        with self._lock:
            return self._saldos.get(sku, 0)

    def reservar(self, itens: list[dict], pedido) -> None:
        """Debita cada item na ordem e o acrescenta em pedido.linhas.

        No primeiro erro para; itens anteriores continuam debitados e em pedido.linhas.
        """
        with self._lock:
            for item in itens:
                sku = item["sku"]
                quantidade = item["quantidade"]
                if quantidade <= 0:
                    raise QuantidadeInvalidaError(f"quantidade inválida: {quantidade}")
                saldo = self._saldos.get(sku, 0)
                if saldo < quantidade:
                    raise EstoqueInsuficienteError(
                        f"saldo {saldo} insuficiente para {quantidade} de {sku}"
                    )
                self._saldos[sku] = saldo - quantidade
                pedido.linhas.append(item)


def normalizar_skus(skus: list[str]) -> int:
    """Altera a lista no lugar (strip + maiúsculas, sem vazios); devolve quantos removeu."""
    normalizados = [s.strip().upper() for s in skus]
    normalizados = [s for s in normalizados if s]
    removidos = len(skus) - len(normalizados)
    skus[:] = normalizados
    return removidos
