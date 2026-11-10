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
    """Recusa do envio da licença de uma venda a um usuário sem permissão de envio.

    A mensagem do erro traz os dois identificadores abaixo.

    Attributes:
        venda_id: Identificador da venda cuja licença seria enviada.
        user_id: Identificador do usuário recusado; None quando a tentativa não tem
            usuário identificado.
    """

    def __init__(self, venda_id: int, user_id: int | None) -> None:
        """Cria o erro para uma tentativa de envio recusada.

        Args:
            venda_id: Identificador da venda cuja licença seria enviada.
            user_id: Identificador do usuário recusado; None é aceito e indica que a
                tentativa não tem usuário identificado.
        """
        super().__init__(
            f"Upload de licença não permitido: venda_id={venda_id}, user_id={user_id}"
        )
        self.venda_id = venda_id
        self.user_id = user_id


class LicencaAccessValidator:
    """Decide quem pode enviar e quem pode acessar a licença de uma venda.

    As decisões distinguem três papéis: administrador, comprador da venda e compositor
    da guia da venda. A instância guarda apenas o conjunto de administradores; a venda
    e a sua guia chegam por argumento em cada chamada.

    Args:
        admin_ids: Identificadores dos usuários administradores. O conjunto é guardado
            por referência, sem cópia: alterações feitas nele depois da construção
            valem para as chamadas seguintes.
    """

    def __init__(self, admin_ids: set[int]) -> None:
        self._admin_ids = admin_ids

    def can_upload(self, venda: Venda, user_id: int | None) -> bool:
        """Indica se o usuário pode enviar a licença da venda.

        Só compositores da guia da venda podem enviar. Ser administrador ou comprador
        da venda não concede essa permissão.

        Não modifica os argumentos nem a instância.

        Args:
            venda: Venda cuja licença seria enviada. A decisão lê apenas os
                compositores de `venda.guia`.
            user_id: Identificador do usuário avaliado; None é aceito e sempre resulta
                em False.

        Returns:
            True se `user_id` for um dos compositores da guia da venda. False nos
            demais casos, inclusive quando `user_id` é None.
        """
        if user_id is None:
            return False
        return self._is_compositor(venda, user_id)

    def require_upload(self, venda: Venda, user_id: int | None) -> None:
        """Exige que o usuário possa enviar a licença da venda.

        A permissão é a mesma decidida por `can_upload`.

        Não modifica os argumentos nem a instância.

        Args:
            venda: Venda cuja licença seria enviada.
            user_id: Identificador do usuário avaliado; None é aceito e sempre resulta
                em erro.

        Raises:
            UploadNaoPermitido: Se `can_upload(venda, user_id)` for False.
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
        """Indica se o usuário mantém o acesso à licença de uma venda cancelada.

        Depois do cancelamento, administradores e compositores da guia da venda mantêm
        o acesso; o comprador perde.

        Pré-condição: a venda está cancelada. `venda.cancelada` não é consultado; cabe
        a quem chama usar este método apenas para vendas canceladas.

        Não modifica os argumentos nem a instância.

        Args:
            venda: Venda cancelada cuja licença seria acessada. A decisão lê apenas os
                compositores de `venda.guia`.
            user_id: Identificador do usuário avaliado; None é aceito e sempre resulta
                em False.

        Returns:
            True se `user_id` for administrador ou compositor da guia da venda. False
            nos demais casos, inclusive quando `user_id` é None e quando o usuário é
            apenas o comprador da venda.
        """
        if user_id is None:
            return False
        return self._is_admin(user_id) or self._is_compositor(venda, user_id)

    def _is_admin(self, user_id: int) -> bool:
        return user_id in self._admin_ids

    def _is_compositor(self, venda: Venda, user_id: int) -> bool:
        return any(c.user_id == user_id for c in venda.guia.compositores)
