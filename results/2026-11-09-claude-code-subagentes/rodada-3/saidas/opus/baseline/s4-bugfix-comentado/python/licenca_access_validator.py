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
    """Usuário não tem permissão para enviar a licença desta venda."""


class LicencaAccessValidator:
    def __init__(self, admin_ids: set[int]) -> None:
        self._admin_ids = admin_ids

    def can_upload(self, venda: Venda, user_id: int | None) -> bool:
        # Só compositor da guia envia. Admin fica de fora de propósito: o
        # arquivo pertence a um titular, e o fluxo de upload rejeita quem não
        # é titular (assertFileOwner), deixando um objeto órfão no S3. Para
        # destravar uma venda, o caminho administrativo é o manual-complete,
        # que é auditado.
        if user_id is None:
            return False
        return self._is_compositor(venda, user_id)

    def require_upload(self, venda: Venda, user_id: int | None) -> None:
        """Lança UploadNaoPermitido se o usuário não puder enviar a licença."""
        if not self.can_upload(venda, user_id):
            raise UploadNaoPermitido(
                f"usuário {user_id} não pode enviar licença da venda {venda.id}"
            )

    def can_access_after_cancel(self, venda: Venda, user_id: int | None) -> bool:
        # Em venda cancelada o comprador perde o acesso; admin e compositor da
        # guia mantêm. Venda não cancelada segue a regra normal de can_access.
        if not venda.cancelada:
            return self.can_access(venda, user_id)
        if user_id is None:
            return False
        return self._is_admin(user_id) or self._is_compositor(venda, user_id)

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
