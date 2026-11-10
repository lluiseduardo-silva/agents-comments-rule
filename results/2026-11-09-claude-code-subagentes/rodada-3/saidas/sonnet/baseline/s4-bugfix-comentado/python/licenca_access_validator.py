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
    """O usuário não tem permissão para enviar a licença desta venda."""


class LicencaAccessValidator:
    def __init__(self, admin_ids: set[int]) -> None:
        self._admin_ids = admin_ids

    def can_upload(self, venda: Venda, user_id: int | None) -> bool:
        """Só compositor da guia pode enviar a licença.

        Admin NÃO envia (LIC-482): o upload exige que o arquivo pertença a um
        titular, então admin sempre cairia em 403 no assertFileOwner, deixando
        um objeto órfão no S3. Para destravar uma venda, o admin usa o
        `manual-complete`, que é auditado.
        """
        # Sem usuário identificado, não há o que autorizar.
        if user_id is None:
            return False
        # Apenas compositor da guia; admin deliberadamente não é aceito aqui.
        return self._is_compositor(venda, user_id)

    def can_access_after_cancel(self, venda: Venda, user_id: int | None) -> bool:
        """Acesso a uma venda depois do cancelamento.

        Venda cancelada: admin e compositor da guia mantêm o acesso; o
        comprador perde. Venda não cancelada segue a regra normal de
        `can_access`.
        """
        if user_id is None:
            return False
        # Venda ativa: nada muda, vale a regra geral (inclui o comprador).
        if not venda.cancelada:
            return self.can_access(venda, user_id)
        # Cancelada: o comprador fica de fora; só admin e compositor passam.
        return self._is_admin(user_id) or self._is_compositor(venda, user_id)

    def require_upload(self, venda: Venda, user_id: int | None) -> None:
        """Não devolve nada; levanta `UploadNaoPermitido` se `can_upload` for falso."""
        if not self.can_upload(venda, user_id):
            raise UploadNaoPermitido(
                f"Usuário {user_id} não pode enviar licença da venda {venda.id}"
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
