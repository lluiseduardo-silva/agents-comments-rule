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
    """O usuário não pode enviar a licença desta venda.

    Levantado por ``LicencaAccessValidator.require_upload`` quando
    ``can_upload`` é falso.
    """

    def __init__(self, venda_id: int, user_id: int | None) -> None:
        super().__init__(
            f"usuário {user_id} não pode enviar licença da venda {venda_id}"
        )
        self.venda_id = venda_id
        self.user_id = user_id


class LicencaAccessValidator:
    def __init__(self, admin_ids: set[int]) -> None:
        self._admin_ids = admin_ids

    def can_upload(self, venda: Venda, user_id: int | None) -> bool:
        """Só um compositor da guia pode enviar a licença.

        Admin não é aceito de propósito: o arquivo pertence a um titular, e o
        fluxo de envio exige que quem confirma seja esse titular. Aceitar admin
        aqui só adiava a recusa para depois do upload, deixando um objeto órfão
        no armazenamento. Habilitar o envio por admin exigiria aceitar um
        compositor explícito na confirmação, o que daria ao admin o poder de
        aprovar a participação de um compositor. Para destravar uma venda, o
        caminho administrativo é ``manual-complete``, que é auditado.
        """
        if user_id is None:
            return False
        return self._is_compositor(venda, user_id)

    def require_upload(self, venda: Venda, user_id: int | None) -> None:
        """Versão impositiva de ``can_upload``: falha em vez de devolver bool.

        Deve ser chamada antes de qualquer gravação no armazenamento, para que
        uma recusa nunca deixe arquivo para trás.

        Raises:
            UploadNaoPermitido: quando ``can_upload`` é falso.
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

    def can_access_after_cancel(
        self, venda: Venda, user_id: int | None
    ) -> bool:
        """Acesso à licença levando em conta o cancelamento da venda.

        Venda cancelada: o comprador perde o acesso; admin e compositores da
        guia mantêm. Venda não cancelada: vale a regra normal de
        ``can_access``.
        """
        if not venda.cancelada:
            return self.can_access(venda, user_id)
        if user_id is None:
            return False
        # O comprador não tem caso próprio aqui: só é aceito se também for
        # admin ou compositor da guia.
        return self._is_admin(user_id) or self._is_compositor(venda, user_id)

    def _is_admin(self, user_id: int) -> bool:
        return user_id in self._admin_ids

    def _is_compositor(self, venda: Venda, user_id: int) -> bool:
        return any(c.user_id == user_id for c in venda.guia.compositores)
