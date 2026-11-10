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

// UploadNaoPermitidoError é o erro devolvido por RequireUpload quando o usuário
// não pode enviar a licença da venda.
//
// Campos:
//   - VendaID: ID da venda para a qual o envio foi recusado.
//   - UserID: ID do usuário recusado, ou nil quando não havia usuário identificado.
type UploadNaoPermitidoError struct {
	VendaID int64
	UserID  *int64
}

// Error devolve a mensagem do erro com o ID da venda e, quando presente, o do
// usuário. Não modifica o erro.
func (e *UploadNaoPermitidoError) Error() string {
	if e.UserID == nil {
		return fmt.Sprintf("upload de licença não permitido na venda %d: usuário não identificado", e.VendaID)
	}
	return fmt.Sprintf("upload de licença não permitido na venda %d para o usuário %d", e.VendaID, *e.UserID)
}

// CanUpload informa se o usuário pode enviar a licença da venda: só um
// compositor da guia da venda pode enviar; administradores não podem.
//
// Não modifica venda, userID nem o validador.
//
// Parâmetros:
//   - venda: venda cuja licença seria enviada; não pode ser nil.
//   - userID: ID do usuário; nil significa usuário não identificado.
//
// Retorna true se userID pertence a um compositor da guia; false se userID é nil
// ou o usuário não é compositor da guia.
//
// Entra em pânico se venda for nil.
func (v *LicencaAccessValidator) CanUpload(venda *Venda, userID *int64) bool {
	if userID == nil {
		return false
	}
	return isCompositor(venda, *userID)
}

// RequireUpload exige que o usuário possa enviar a licença da venda, segundo
// CanUpload.
//
// Não modifica venda, userID nem o validador.
//
// Parâmetros:
//   - venda: venda cuja licença será enviada; não pode ser nil.
//   - userID: ID do usuário; nil significa usuário não identificado e é sempre
//     recusado.
//
// Retorna nil quando o envio é permitido, ou um *UploadNaoPermitidoError com o ID
// da venda e userID quando CanUpload devolve false.
//
// Entra em pânico se venda for nil.
func (v *LicencaAccessValidator) RequireUpload(venda *Venda, userID *int64) error {
	if !v.CanUpload(venda, userID) {
		return &UploadNaoPermitidoError{VendaID: venda.ID, UserID: userID}
	}
	return nil
}

// CanAccessAfterCancel informa se o usuário pode acessar a licença da venda,
// considerando o cancelamento: em venda cancelada, administradores e compositores
// da guia mantêm o acesso e o comprador o perde; em venda não cancelada, o
// resultado é o mesmo de CanAccess.
//
// Não modifica venda, userID nem o validador.
//
// Parâmetros:
//   - venda: venda cuja licença seria acessada; não pode ser nil.
//   - userID: ID do usuário; nil significa usuário não identificado.
//
// Retorna true se o usuário tem acesso; false se userID é nil ou o usuário não
// tem acesso. Um comprador que também é administrador ou compositor da guia
// mantém o acesso em venda cancelada.
//
// Entra em pânico se venda for nil.
func (v *LicencaAccessValidator) CanAccessAfterCancel(venda *Venda, userID *int64) bool {
	if !venda.Cancelada {
		return v.CanAccess(venda, userID)
	}
	if userID == nil {
		return false
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
