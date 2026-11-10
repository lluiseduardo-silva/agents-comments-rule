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
    """Usuário não pode enviar a licença desta venda (só compositor da guia pode)."""

    def __init__(self, venda_id: int, user_id: int | None) -> None:
        super().__init__(
            f"upload de licença não permitido: venda={venda_id} user_id={user_id}"
        )
        self.venda_id = venda_id
        self.user_id = user_id


class LicencaAccessValidator:
    def __init__(self, admin_ids: set[int]) -> None:
        self._admin_ids = admin_ids

    def can_upload(self, venda: Venda, user_id: int | None) -> bool:
        # Admin não envia licença (LIC-482): o arquivo pertence a um titular, e o
        # caminho administrativo auditado para destravar a venda é manual-complete.
        if user_id is None:
            return False
        return self._is_compositor(venda, user_id)

    def require_upload(self, venda: Venda, user_id: int | None) -> None:
        if not self.can_upload(venda, user_id):
            raise UploadNaoPermitido(venda.id, user_id)

    def can_access_after_cancel(self, venda: Venda, user_id: int | None) -> bool:
        # Venda cancelada: admin e compositor da guia mantêm o acesso; o comprador perde.
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
