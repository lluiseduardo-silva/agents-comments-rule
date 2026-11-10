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
    """Erro lançado quando um usuário tenta enviar a licença de uma venda sem permissão.

    Ocorre quando o usuário não é compositor da guia da venda, inclusive quando é
    admin ou quando não há usuário identificado.

    Attributes:
        venda_id: Identificador da venda cujo envio foi recusado.
        user_id: Usuário que tentou o envio; ``None`` quando não havia usuário
            identificado.
    """

    def __init__(self, venda_id: int, user_id: int | None) -> None:
        """Cria o erro para a venda e o usuário recusados.

        Args:
            venda_id: Identificador da venda cujo envio foi recusado.
            user_id: Usuário que tentou o envio, ou ``None`` se não identificado.
        """
        super().__init__(
            f"Usuário {user_id} não pode enviar a licença da venda {venda_id}"
        )
        self.venda_id = venda_id
        self.user_id = user_id


class LicencaAccessValidator:
    """Decide quem pode enviar e quem pode acessar a licença de uma venda.

    Attributes:
        _admin_ids: Identificadores dos usuários tratados como admin.
    """

    def __init__(self, admin_ids: set[int]) -> None:
        """Cria o validador com o conjunto de admins informado.

        Args:
            admin_ids: Identificadores dos usuários admin. O conjunto é guardado por
                referência, sem cópia; alterações feitas nele depois afetam o validador.
        """
        self._admin_ids = admin_ids

    def can_upload(self, venda: Venda, user_id: int | None) -> bool:
        """Indica se o usuário pode enviar a licença da venda.

        Só compositores da guia da venda podem enviar; admin não envia licença.

        Não modifica os argumentos nem o estado da instância.

        Args:
            venda: Venda cuja licença seria enviada.
            user_id: Usuário que tenta enviar; ``None`` representa usuário não
                identificado.

        Returns:
            ``True`` se o usuário é compositor da guia da venda; ``False`` caso
            contrário, inclusive quando ``user_id`` é ``None``.
        """
        if user_id is None:
            return False
        return self._is_compositor(venda, user_id)

    def require_upload(self, venda: Venda, user_id: int | None) -> None:
        """Garante que o usuário pode enviar a licença da venda.

        Aplica a mesma regra de ``can_upload``: só compositores da guia enviam.

        Não modifica os argumentos nem o estado da instância.

        Args:
            venda: Venda cuja licença seria enviada.
            user_id: Usuário que tenta enviar; ``None`` representa usuário não
                identificado.

        Raises:
            UploadNaoPermitido: Se ``can_upload`` devolver ``False`` para a venda e
                o usuário informados.
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

    def can_access_after_cancel(self, venda: Venda, user_id: int | None) -> bool:
        """Indica se o usuário pode acessar a licença, considerando o cancelamento da venda.

        Em venda cancelada, admin e compositores da guia mantêm o acesso e o
        comprador o perde. Em venda não cancelada, vale a mesma regra de
        ``can_access``.

        Não modifica os argumentos nem o estado da instância.

        Args:
            venda: Venda cuja licença seria acessada.
            user_id: Usuário que tenta acessar; ``None`` representa usuário não
                identificado.

        Returns:
            ``True`` se o usuário pode acessar a licença; ``False`` caso contrário,
            inclusive quando ``user_id`` é ``None``.
        """
        if not venda.cancelada:
            return self.can_access(venda, user_id)
        if user_id is None:
            return False
        if self._is_admin(user_id):
            return True
        return self._is_compositor(venda, user_id)

    def _is_admin(self, user_id: int) -> bool:
        return user_id in self._admin_ids

    def _is_compositor(self, venda: Venda, user_id: int) -> bool:
        return any(c.user_id == user_id for c in venda.guia.compositores)
