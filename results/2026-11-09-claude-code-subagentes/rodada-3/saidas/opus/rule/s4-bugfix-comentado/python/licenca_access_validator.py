from dataclasses import dataclass


@dataclass
class Compositor:
    user_id: int


@dataclass
class Guia:
    compositores: list[Compositor]


@dataclass
class Venda:
    id: int
    comprador_id: int
    guia: Guia
    cancelada: bool


class UploadNaoPermitido(Exception):
    """Erro de quem tenta enviar a licença de uma venda sem ser compositor da guia.

    Attributes:
        venda_id: Id da venda cujo envio foi recusado.
        user_id: Id do usuário recusado; None quando não há usuário autenticado.

    Args:
        venda_id: Id da venda cujo envio foi recusado.
        user_id: Id do usuário recusado; None quando não há usuário autenticado.
    """

    def __init__(self, venda_id: int, user_id: int | None) -> None:
        super().__init__(
            f"Usuário {user_id} não pode enviar a licença da venda {venda_id}"
        )
        self.venda_id = venda_id
        self.user_id = user_id


class LicencaAccessValidator:
    def __init__(self, admin_ids: set[int]) -> None:
        self._admin_ids = admin_ids

    def can_upload(self, venda: Venda, user_id: int | None) -> bool:
        """Indica se o usuário pode enviar a licença da venda.

        Só um compositor da guia da venda pode enviar; admin e comprador não
        podem, a menos que também sejam compositores da guia.

        Não modifica a venda, seus argumentos nem o estado da instância.

        Args:
            venda: Venda cuja guia define os compositores autorizados.
            user_id: Id do usuário; None representa ausência de usuário
                autenticado e nunca é autorizado.

        Returns:
            True se ``user_id`` for compositor da guia; False caso contrário,
            inclusive quando ``user_id`` é None.
        """
        if user_id is None:
            return False
        return self._is_compositor(venda, user_id)

    def require_upload(self, venda: Venda, user_id: int | None) -> None:
        """Exige que o usuário possa enviar a licença da venda.

        Aplica a mesma regra de :meth:`can_upload`: só compositor da guia.

        Não modifica a venda, seus argumentos nem o estado da instância.

        Args:
            venda: Venda cuja guia define os compositores autorizados.
            user_id: Id do usuário; None representa ausência de usuário
                autenticado e sempre resulta em erro.

        Raises:
            UploadNaoPermitido: Se :meth:`can_upload` devolver False para
                ``venda`` e ``user_id``.
        """
        if not self.can_upload(venda, user_id):
            raise UploadNaoPermitido(venda.id, user_id)

    def can_access_after_cancel(self, venda: Venda, user_id: int | None) -> bool:
        """Indica se o usuário pode acessar a licença, considerando o cancelamento.

        Em venda cancelada, admin e compositor da guia mantêm o acesso e o
        comprador o perde. Em venda não cancelada, vale a regra de
        :meth:`can_access`: admin, comprador e compositor da guia acessam.

        Não modifica a venda, seus argumentos nem o estado da instância.

        Args:
            venda: Venda consultada; ``venda.cancelada`` define qual regra se
                aplica.
            user_id: Id do usuário; None representa ausência de usuário
                autenticado e nunca tem acesso.

        Returns:
            True se o usuário tem acesso pela regra aplicável; False caso
            contrário, inclusive quando ``user_id`` é None.
        """
        if not venda.cancelada:
            return self.can_access(venda, user_id)
        if user_id is None:
            return False
        if self._is_admin(user_id):
            return True
        return self._is_compositor(venda, user_id)

    def can_access(self, venda: Venda, user_id: int | None) -> bool:
        if user_id is None:
            return False
        if self._is_admin(user_id):
            return True
        if venda.comprador_id == user_id:
            return True
        return self._is_compositor(venda, user_id)

    def _is_admin(self, user_id: int) -> bool:
        return user_id in self._admin_ids

    def _is_compositor(self, venda: Venda, user_id: int) -> bool:
        return any(c.user_id == user_id for c in venda.guia.compositores)
