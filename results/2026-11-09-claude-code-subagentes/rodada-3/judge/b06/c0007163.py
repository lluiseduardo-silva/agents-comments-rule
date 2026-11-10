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
    """Erro que indica que o usuário não pode enviar a licença da venda.

    Ocorre quando `LicencaAccessValidator.require_upload` é chamado para um usuário
    a quem `LicencaAccessValidator.can_upload` nega o envio.

    Args:
        venda_id: Id da venda cujo envio foi negado.
        user_id: Id do usuário que teve o envio negado. None quando não havia
            usuário identificado.

    Attributes:
        venda_id: Id da venda cujo envio foi negado.
        user_id: Id do usuário que teve o envio negado. None quando não havia
            usuário identificado.
    """

    def __init__(self, venda_id: int, user_id: int | None) -> None:
        super().__init__(
            f"Envio de licença não permitido (venda={venda_id}, usuário={user_id})"
        )
        self.venda_id = venda_id
        self.user_id = user_id


class LicencaAccessValidator:
    """Decide quem pode enviar e quem pode acessar a licença de uma venda.

    As decisões distinguem três papéis: admin, comprador da venda e compositor da
    guia da venda. Um mesmo usuário pode acumular mais de um papel.

    Args:
        admin_ids: Ids dos usuários admin. O conjunto é guardado por referência,
            sem cópia: mudanças feitas nele depois da construção alteram as
            decisões da instância.
    """

    def __init__(self, admin_ids: set[int]) -> None:
        self._admin_ids = admin_ids

    def can_upload(self, venda: Venda, user_id: int | None) -> bool:
        """Indica se o usuário pode enviar a licença da venda.

        Só compositor da guia da venda pode enviar. Ser admin ou comprador da venda
        não concede o envio.

        Não modifica os argumentos nem a instância.

        Args:
            venda: Venda cuja licença seria enviada.
            user_id: Id do usuário que quer enviar. None representa a ausência de
                usuário identificado.

        Returns:
            True se `user_id` for de um compositor da guia de `venda`. False nos
            demais casos, inclusive quando `user_id` é None.
        """
        if user_id is None:
            return False
        return self._is_compositor(venda, user_id)

    def can_access_after_cancel(self, venda: Venda, user_id: int | None) -> bool:
        """Indica se o usuário tem acesso à licença de uma venda cancelada.

        Admin e compositor da guia da venda mantêm o acesso depois do cancelamento;
        o comprador perde o acesso quando a venda é cancelada. Não consulta
        `venda.cancelada`: a resposta é sempre a da regra de venda cancelada, e
        aplicá-la apenas a vendas canceladas fica a cargo de quem chama.

        Não modifica os argumentos nem a instância.

        Args:
            venda: Venda cuja licença seria acessada.
            user_id: Id do usuário que quer acessar. None representa a ausência de
                usuário identificado.

        Returns:
            True se `user_id` for de um admin ou de um compositor da guia de
            `venda`. False nos demais casos, inclusive para o comprador que não
            seja admin nem compositor da guia e quando `user_id` é None.
        """
        if user_id is None:
            return False
        if self._is_admin(user_id):
            return True
        return self._is_compositor(venda, user_id)

    def require_upload(self, venda: Venda, user_id: int | None) -> None:
        """Exige que o usuário possa enviar a licença da venda.

        Aplica a regra de `can_upload` e termina sem devolver valor quando o envio
        é permitido.

        Não modifica os argumentos nem a instância.

        Args:
            venda: Venda cuja licença seria enviada.
            user_id: Id do usuário que quer enviar. None representa a ausência de
                usuário identificado e sempre resulta em erro.

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

    def _is_admin(self, user_id: int) -> bool:
        return user_id in self._admin_ids

    def _is_compositor(self, venda: Venda, user_id: int) -> bool:
        return any(c.user_id == user_id for c in venda.guia.compositores)
