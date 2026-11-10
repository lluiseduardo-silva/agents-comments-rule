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
    """O usuário não pode enviar a licença desta venda.

    Os identificadores ficam em atributos para que a borda (HTTP, fila) traduza
    a recusa sem precisar interpretar o texto da mensagem.
    """

    def __init__(self, venda_id: int, user_id: int | None) -> None:
        super().__init__(
            f"upload de licença não permitido: venda={venda_id}, usuário={user_id}"
        )
        self.venda_id = venda_id
        self.user_id = user_id


class LicencaAccessValidator:
    """Decide quem pode enviar e quem pode acessar a licença de uma venda.

    Cada `True` devolvido aqui é uma promessa a quem chama: a camada que executa
    a operação precisa honrá-la. Ao mudar uma regra, confira se o serviço que
    faz o trabalho exige a mesma coisa; quando os dois discordam, a operação
    começa e só falha no meio do caminho.
    """

    def __init__(self, admin_ids: set[int]) -> None:
        self._admin_ids = admin_ids

    def can_upload(self, venda: Venda, user_id: int | None) -> bool:
        """Só compositor da guia da venda pode enviar a licença.

        Admin fica de fora de propósito. O arquivo pertence a um titular, e
        `LicenseUploadService.assertUploadAllowed` recusa com 403 quem não é
        titular. Um `True` para admin aqui seria uma promessa que termina em
        erro e deixa um objeto órfão no armazenamento a cada tentativa.

        O caminho administrativo para destravar uma venda é `manual-complete`,
        que é auditado.
        """
        # Sem usuário identificado não há a quem conceder nada.
        if user_id is None:
            return False
        return self._is_compositor(venda, user_id)

    def require_upload(self, venda: Venda, user_id: int | None) -> None:
        """Exige a permissão de envio; levanta `UploadNaoPermitidoError` se faltar.

        Forma imperativa de `can_upload`, para ser chamada antes de qualquer
        efeito do envio (gravar o arquivo, registrar a licença): recusando
        cedo, nada fica para trás. A regra em si vive só em `can_upload`.
        """
        if not self.can_upload(venda, user_id):
            raise UploadNaoPermitidoError(venda.id, user_id)

    def can_access(self, venda: Venda, user_id: int | None) -> bool:
        """Acesso à licença da venda: admin, comprador ou compositor da guia.

        Não considera o estado da venda; a regra para venda cancelada está em
        `can_access_after_cancel`.
        """
        if user_id is None:
            return False
        if self._is_admin(user_id):
            return True
        if venda.comprador_id == user_id:
            return True
        return self._is_compositor(venda, user_id)

    def can_access_after_cancel(self, venda: Venda, user_id: int | None) -> bool:
        """Quem continua com acesso à licença depois que a venda foi cancelada.

        Admin e compositor da guia mantêm o acesso. O comprador perde: é a
        única diferença em relação a `can_access`.

        Este método não consulta `venda.cancelada`. Ele responde à regra da
        venda morta, e quem chama decide quando ela se aplica. Usado por engano
        numa venda viva, nega o comprador, ou seja, erra para o lado fechado.
        """
        if user_id is None:
            return False
        if self._is_admin(user_id):
            return True
        # O comprador não tem ramo aqui de propósito: só passa se também for
        # compositor da guia.
        return self._is_compositor(venda, user_id)

    def _is_admin(self, user_id: int) -> bool:
        return user_id in self._admin_ids

    def _is_compositor(self, venda: Venda, user_id: int) -> bool:
        return any(c.user_id == user_id for c in venda.guia.compositores)
