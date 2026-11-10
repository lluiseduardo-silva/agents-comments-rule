"""Controle de estoque em memória."""

import threading


class QuantidadeInvalidaError(ValueError):
    """Quantidade menor ou igual a zero."""


class EstoqueInsuficienteError(Exception):
    """Saldo do sku menor que a quantidade pedida."""


class LimiteExcedidoError(ValueError):
    """Saldo resultante acima do limite por sku."""


class Estoque:
    """Saldos por sku, mantidos em memória, com limite máximo por sku.

    Atributos:
        limite_por_sku: Saldo máximo permitido para cada sku; sempre maior que zero.

    As operações são atômicas entre threads da mesma instância (um único lock
    protege os saldos). O estado vive só no processo: não é compartilhado entre
    instâncias.

    Args:
        limite_por_sku: Saldo máximo por sku.

    Raises:
        ValueError: Se `limite_por_sku` for menor ou igual a zero.
    """

    def __init__(self, limite_por_sku: int) -> None:
        if limite_por_sku <= 0:
            raise ValueError("limite_por_sku deve ser maior que zero")
        self.limite_por_sku = limite_por_sku
        self._saldos: dict[str, int] = {}
        self._lock = threading.Lock()

    def repor(self, sku: str, quantidade: int) -> None:
        """Soma `quantidade` ao saldo de `sku`.

        Modifica o saldo de `sku` na instância; se falhar, o saldo não muda.

        Args:
            sku: Identificador do item.
            quantidade: Quantidade a somar; deve ser maior que zero.

        Raises:
            QuantidadeInvalidaError: Se `quantidade` for menor ou igual a zero.
            LimiteExcedidoError: Se o saldo resultante passar de `limite_por_sku`.
        """
        if quantidade <= 0:
            raise QuantidadeInvalidaError(f"quantidade inválida: {quantidade}")
        with self._lock:
            novo = self._saldos.get(sku, 0) + quantidade
            if novo > self.limite_por_sku:
                raise LimiteExcedidoError(
                    f"saldo {novo} de {sku} excede o limite {self.limite_por_sku}"
                )
            self._saldos[sku] = novo

    def quantidade(self, sku: str) -> int:
        """Devolve o saldo atual de `sku`.

        Não modifica seus argumentos nem a instância.

        Args:
            sku: Identificador do item.

        Returns:
            O saldo de `sku`; zero se o sku não existir.
        """
        with self._lock:
            return self._saldos.get(sku, 0)

    def reservar(self, itens: list[dict], pedido) -> None:
        """Debita do saldo cada item de `itens` e o acrescenta a `pedido.linhas`.

        Processa os itens na ordem. Modifica o saldo da instância e `pedido.linhas`
        (os itens são acrescentados por referência, sem cópia). Não modifica
        `itens`. Se um item falhar, a operação para: os itens anteriores continuam
        debitados e em `pedido.linhas`, e o item que falhou e os seguintes não são
        alterados.

        Args:
            itens: Lista de mapeamentos com as chaves `sku` e `quantidade`.
            pedido: Objeto mutável com o atributo `linhas`, uma lista.

        Raises:
            QuantidadeInvalidaError: Se a quantidade de um item for menor ou igual
                a zero.
            EstoqueInsuficienteError: Se o saldo de um item for menor que a
                quantidade pedida.
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
                        f"saldo {saldo} de {sku} menor que {quantidade}"
                    )
                self._saldos[sku] = saldo - quantidade
                pedido.linhas.append(item)

    def normalizar_skus(self, skus: list[str]) -> int:
        """Normaliza `skus` no lugar: apara espaços, põe em maiúsculas e remove vazios.

        Modifica `skus` in-place, preservando a ordem dos restantes. Não modifica
        o estado da instância.

        Args:
            skus: Lista mutável de textos.

        Returns:
            Quantidade de elementos removidos por ficarem vazios.
        """
        normalizados = [s.strip().upper() for s in skus]
        restantes = [s for s in normalizados if s]
        removidos = len(skus) - len(restantes)
        skus[:] = restantes
        return removidos
