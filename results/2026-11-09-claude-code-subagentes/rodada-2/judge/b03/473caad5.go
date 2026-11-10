package licencas

import "fmt"

type Compositor struct {
	UserID int64
}

type Guia struct {
	Compositores []Compositor
}

type Venda struct {
	ID          int64
	CompradorID int64
	Guia        Guia
	Cancelada   bool
}

type LicencaAccessValidator struct {
	adminIDs map[int64]struct{}
}

func NewLicencaAccessValidator(adminIDs map[int64]struct{}) *LicencaAccessValidator {
	return &LicencaAccessValidator{adminIDs: adminIDs}
}

// UploadNaoPermitido é o erro devolvido quando um usuário tenta enviar a licença
// de uma venda sem ser compositor da guia dessa venda.
//
// Campos:
//   - VendaID: ID da venda cujo envio foi recusado.
//   - UserID: ID do usuário recusado; nil quando a chamada não tinha usuário
//     autenticado.
type UploadNaoPermitido struct {
	VendaID int64
	UserID  *int64
}

// Error descreve a recusa citando a venda e, quando houver, o usuário.
//
// Não modifica o receptor.
//
// Retorna a mensagem do erro.
func (e *UploadNaoPermitido) Error() string {
	if e.UserID == nil {
		return fmt.Sprintf("upload de licença não permitido na venda %d: usuário não autenticado", e.VendaID)
	}
	return fmt.Sprintf("upload de licença não permitido na venda %d para o usuário %d", e.VendaID, *e.UserID)
}

// CanUpload informa se o usuário pode enviar a licença da venda: só um
// compositor da guia da venda pode enviar; admin sem ser compositor não pode.
//
// Não modifica seus argumentos nem o validador.
//
// Parâmetros:
//   - venda: venda cuja licença seria enviada; não pode ser nil.
//   - userID: ID do usuário que tenta enviar; nil significa usuário não
//     autenticado.
//
// Retorna true se userID não for nil e pertencer a um compositor da guia;
// false em qualquer outro caso, inclusive para userID nil.
func (v *LicencaAccessValidator) CanUpload(venda *Venda, userID *int64) bool {
	if userID == nil {
		return false
	}
	return isCompositor(venda, *userID)
}

// RequireUpload garante que o usuário pode enviar a licença da venda, pela
// mesma regra de CanUpload.
//
// Não modifica seus argumentos nem o validador.
//
// Parâmetros:
//   - venda: venda cuja licença seria enviada; não pode ser nil.
//   - userID: ID do usuário que tenta enviar; nil significa usuário não
//     autenticado.
//
// Retorna nil quando o envio é permitido.
//
// Erros: devolve *UploadNaoPermitido, com o ID da venda e o userID recebido,
// quando CanUpload devolve false.
func (v *LicencaAccessValidator) RequireUpload(venda *Venda, userID *int64) error {
	if !v.CanUpload(venda, userID) {
		return &UploadNaoPermitido{VendaID: venda.ID, UserID: userID}
	}
	return nil
}

// CanAccessAfterCancel informa se o usuário pode acessar a licença levando
// em conta o cancelamento da venda: em venda cancelada, admin e compositor da
// guia mantêm o acesso e o comprador o perde. Em venda não cancelada, vale a
// regra de CanAccess.
//
// Não modifica seus argumentos nem o validador.
//
// Parâmetros:
//   - venda: venda cuja licença seria acessada; não pode ser nil.
//   - userID: ID do usuário que tenta acessar; nil significa usuário não
//     autenticado.
//
// Retorna false para userID nil. Para venda cancelada, retorna true só se o
// usuário for admin ou compositor da guia; para venda não cancelada, retorna o
// mesmo que CanAccess.
func (v *LicencaAccessValidator) CanAccessAfterCancel(venda *Venda, userID *int64) bool {
	if userID == nil {
		return false
	}
	if !venda.Cancelada {
		return v.CanAccess(venda, userID)
	}
	return v.isAdmin(*userID) || isCompositor(venda, *userID)
}

func (v *LicencaAccessValidator) CanAccess(venda *Venda, userID *int64) bool {
	if userID == nil {
		return false
	}
	if v.isAdmin(*userID) {
		return true
	}
	if venda.CompradorID == *userID {
		return true
	}
	return isCompositor(venda, *userID)
}

func (v *LicencaAccessValidator) isAdmin(userID int64) bool {
	_, ok := v.adminIDs[userID]
	return ok
}

func isCompositor(venda *Venda, userID int64) bool {
	for _, c := range venda.Guia.Compositores {
		if c.UserID == userID {
			return true
		}
	}
	return false
}
