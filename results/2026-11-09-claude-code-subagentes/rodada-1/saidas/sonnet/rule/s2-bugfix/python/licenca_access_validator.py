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
    """Erro de envio de licença por usuário que não é compositor da guia da venda.

    Attributes:
        venda_id: Identificador da venda cujo envio foi recusado.
        user_id: Identificador do usuário recusado; None se anônimo.
    """

    def __init__(self, venda_id: int, user_id: int | None) -> None:
        """Cria o erro com a venda e o usuário recusados.

        Não modifica estado externo.

        Args:
            venda_id: Identificador da venda cujo envio foi recusado.
            user_id: Identificador do usuário recusado; None se anônimo.
        """
        super().__init__(f"Upload não permitido: venda={venda_id}, usuario={user_id}")
        self.venda_id = venda_id
        self.user_id = user_id


class LicencaAccessValidator:
    def __init__(self, admin_ids: set[int]) -> None:
        self._admin_ids = admin_ids

    def can_upload(self, venda: Venda, user_id: int | None) -> bool:
        """Indica se o usuário pode enviar a licença da venda.

        Somente compositor da guia da venda pode enviar; administrador não envia.
        Não modifica seus argumentos nem a instância.

        Args:
            venda: Venda cuja guia é consultada.
            user_id: Identificador do usuário; None (anônimo) nunca pode enviar.

        Returns:
            True se o usuário é compositor da guia da venda; False caso contrário.
        """
        if user_id is None:
            return False
        return self._is_compositor(venda, user_id)

    def can_access_after_cancel(self, venda: Venda, user_id: int | None) -> bool:
        """Indica se o usuário acessa a licença de uma venda cancelada.

        Em venda cancelada, administrador e compositor da guia mantêm o acesso e o
        comprador o perde. Em venda não cancelada, aplica a regra de `can_access`.
        Não modifica seus argumentos nem a instância.

        Args:
            venda: Venda consultada.
            user_id: Identificador do usuário; None (anônimo) nunca tem acesso.

        Returns:
            True se o usuário tem acesso; False caso contrário.
        """
        if not venda.cancelada:
            return self.can_access(venda, user_id)
        if user_id is None:
            return False
        return self._is_admin(user_id) or self._is_compositor(venda, user_id)

    def require_upload(self, venda: Venda, user_id: int | None) -> None:
        """Exige que o usuário possa enviar a licença da venda.

        Não modifica seus argumentos nem a instância.

        Args:
            venda: Venda cuja guia é consultada.
            user_id: Identificador do usuário; None (anônimo) não pode enviar.

        Raises:
            UploadNaoPermitido: Se `can_upload` for falso para o usuário.
        """
        if not self.can_upload(venda, user_id):
            raise UploadNaoPermitido(venda.id, user_id)

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
