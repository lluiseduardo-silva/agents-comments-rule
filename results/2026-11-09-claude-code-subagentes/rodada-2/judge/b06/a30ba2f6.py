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


class UploadNaoPermitidoError(Exception):
    """Levantada quando o usuário não pode enviar a licença da venda.

    Faz parte do contrato de `require_upload`: quem chama deve tratá-la
    (por exemplo, traduzindo para 403) antes de gerar qualquer efeito colateral.
    """


class LicencaAccessValidator:
    def __init__(self, admin_ids: set[int]) -> None:
        self._admin_ids = admin_ids

    def can_upload(self, venda: Venda, user_id: int | None) -> bool:
        # Anônimo nunca envia.
        if user_id is None:
            return False
        # Admin NÃO envia licença (LIC-482). O arquivo pertence a um titular e o
        # admin não é titular: antes, esta checagem devolvia True e a chamada
        # caía em 403 logo depois, deixando objeto órfão no S3. Habilitar de
        # verdade exigiria um `onBehalfOfUserId` explícito, dando ao admin poder de
        # aprovar a participação de um compositor. Para destravar uma venda, o
        # caminho auditado é `manual-complete`.
        # Portanto, só o compositor da guia pode enviar.
        return self._is_compositor(venda, user_id)

    def require_upload(self, venda: Venda, user_id: int | None) -> None:
        """Não devolve nada; falha com `UploadNaoPermitidoError` se não puder enviar.

        Deve ser chamada ANTES de qualquer efeito colateral (ex.: gravar no S3),
        para que uma tentativa negada não deixe objetos órfãos.
        """
        if not self.can_upload(venda, user_id):
            raise UploadNaoPermitidoError(
                f"Usuário {user_id} não pode enviar licença da venda {venda.id}"
            )

    def can_access_after_cancel(self, venda: Venda, user_id: int | None) -> bool:
        """Acesso à licença depois que a venda morre (cancelada).

        Venda cancelada: admin e compositor da guia mantêm o acesso; o comprador
        perde. Venda não cancelada: vale a regra normal de `can_access`.
        """
        if not venda.cancelada:
            return self.can_access(venda, user_id)
        if user_id is None:
            return False
        # Comprador é deliberadamente omitido: perde o acesso com o cancelamento.
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
