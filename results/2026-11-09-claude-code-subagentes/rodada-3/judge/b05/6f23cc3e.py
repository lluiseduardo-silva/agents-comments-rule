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
    """O usuário não pode enviar a licença da venda."""


class LicencaAccessValidator:
    """Regras de quem pode enviar e consultar a licença de uma venda.

    Em todos os métodos, `user_id` igual a `None` representa uma chamada sem
    usuário autenticado e nunca tem permissão.
    """

    def __init__(self, admin_ids: set[int]) -> None:
        self._admin_ids = admin_ids

    def can_upload(self, venda: Venda, user_id: int | None) -> bool:
        """Diz se o usuário pode enviar a licença: só compositor da guia."""
        if user_id is None:
            return False
        # Ser admin não concede nada aqui, de propósito. O arquivo enviado
        # precisa pertencer a um titular da guia, e enviar em nome de um
        # titular seria aprovar a participação dele. Para destravar uma venda,
        # o caminho administrativo é o `manual-complete`, que é auditado.
        return self._is_compositor(venda, user_id)

    def require_upload(self, venda: Venda, user_id: int | None) -> None:
        """Garante que o usuário pode enviar a licença.

        Aplica a mesma regra de `can_upload`, para quem prefere interromper o
        fluxo a testar um booleano.

        Raises:
            UploadNaoPermitido: se `can_upload` for falso.
        """
        if not self.can_upload(venda, user_id):
            raise UploadNaoPermitido(
                f"usuário {user_id} não pode enviar a licença da venda {venda.id}"
            )

    def can_access(self, venda: Venda, user_id: int | None) -> bool:
        """Diz se o usuário pode consultar a licença.

        Têm acesso o admin, o comprador e os compositores da guia.
        """
        if user_id is None:
            return False
        if self._is_admin(user_id):
            return True
        if venda.comprador_id == user_id:
            return True
        return self._is_compositor(venda, user_id)

    def can_access_after_cancel(self, venda: Venda, user_id: int | None) -> bool:
        """Diz se o usuário mantém o acesso à licença de uma venda cancelada.

        Admin e compositores da guia mantêm o acesso. O comprador perde, e essa
        é a única diferença em relação a `can_access`.

        Não consulta `venda.cancelada`: cabe a quem chama decidir quando a
        venda está cancelada e esta regra passa a valer.
        """
        if user_id is None:
            return False
        if self._is_admin(user_id):
            return True
        # Sem o atalho por `comprador_id`: um comprador só passa daqui se
        # também for compositor da guia.
        return self._is_compositor(venda, user_id)

    def _is_admin(self, user_id: int) -> bool:
        return user_id in self._admin_ids

    def _is_compositor(self, venda: Venda, user_id: int) -> bool:
        return any(c.user_id == user_id for c in venda.guia.compositores)
