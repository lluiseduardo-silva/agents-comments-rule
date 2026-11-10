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
    """Indica que o usuário não pode enviar a licença da venda informada."""


class LicencaAccessValidator:
    def __init__(self, admin_ids: set[int]) -> None:
        self._admin_ids = admin_ids

    def can_upload(self, venda: Venda, user_id: int | None) -> bool:
        """Informa se o usuário pode enviar a licença da venda.

        Somente compositor da guia da venda pode enviar; administrador e
        comprador não podem. Não modifica seus argumentos nem a instância.

        Args:
            venda: Venda cuja licença seria enviada.
            user_id: Identificador do usuário; None representa usuário anônimo.

        Returns:
            True se o usuário é compositor da guia da venda; False se é
            anônimo ou não é compositor da guia.
        """
        if user_id is None:
            return False
        return self._is_compositor(venda, user_id)

    def can_access_after_cancel(self, venda: Venda, user_id: int | None) -> bool:
        """Informa se o usuário mantém acesso à licença de uma venda cancelada.

        Em venda cancelada, administrador e compositor da guia mantêm o acesso
        e o comprador o perde. Em venda não cancelada, o resultado é o de
        `can_access`. Não modifica seus argumentos nem a instância.

        Args:
            venda: Venda cujo acesso é avaliado.
            user_id: Identificador do usuário; None representa usuário anônimo.

        Returns:
            True se o usuário tem acesso; False se é anônimo ou não tem acesso
            segundo a regra acima.
        """
        if not venda.cancelada:
            return self.can_access(venda, user_id)
        if user_id is None:
            return False
        return self._is_admin(user_id) or self._is_compositor(venda, user_id)

    def require_upload(self, venda: Venda, user_id: int | None) -> None:
        """Garante que o usuário pode enviar a licença da venda.

        Não modifica seus argumentos nem a instância.

        Args:
            venda: Venda cuja licença seria enviada.
            user_id: Identificador do usuário; None representa usuário anônimo.

        Raises:
            UploadNaoPermitido: Se `can_upload` for falso para o usuário.
        """
        if not self.can_upload(venda, user_id):
            raise UploadNaoPermitido(
                f"usuário {user_id} não pode enviar a licença da venda {venda.id}"
            )

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
