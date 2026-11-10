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

// CanUpload informa se o usuário pode enviar a licença da venda: somente
// compositores da guia da venda podem; administradores não.
//
// Não modifica seus argumentos nem o estado do validador.
//
// Parâmetros:
//   - venda: venda cuja guia define os compositores; não pode ser nil.
//   - userID: identificador do usuário autenticado; nil representa usuário
//     anônimo e resulta em false.
//
// Retorna true se o usuário é compositor da guia; false caso contrário.
func (v *LicencaAccessValidator) CanUpload(venda *Venda, userID *int64) bool {
	if userID == nil {
		return false
	}
	return isCompositor(venda, *userID)
}

// CanAccessAfterCancel informa se o usuário pode acessar a licença da venda,
// considerando o estado de cancelamento: em venda cancelada, administradores e
// compositores da guia mantêm o acesso e o comprador o perde. Em venda não
// cancelada, a decisão é a mesma de CanAccess.
//
// Não modifica seus argumentos nem o estado do validador.
//
// Parâmetros:
//   - venda: venda avaliada; não pode ser nil.
//   - userID: identificador do usuário autenticado; nil representa usuário
//     anônimo e resulta em false.
//
// Retorna true se o acesso é permitido; false caso contrário.
func (v *LicencaAccessValidator) CanAccessAfterCancel(venda *Venda, userID *int64) bool {
	if userID == nil {
		return false
	}
	if !venda.Cancelada {
		return v.CanAccess(venda, userID)
	}
	return v.isAdmin(*userID) || isCompositor(venda, *userID)
}

// UploadNaoPermitidoError é o erro devolvido quando um usuário sem permissão de
// envio tenta enviar a licença de uma venda.
//
// Campos:
//   - VendaID: identificador da venda cujo envio foi recusado.
//   - UserID: usuário que tentou o envio; nil quando não havia usuário
//     autenticado.
type UploadNaoPermitidoError struct {
	VendaID int64
	UserID  *int64
}

// Error devolve a mensagem do erro, identificando a venda recusada.
//
// Não modifica a instância.
func (e *UploadNaoPermitidoError) Error() string {
	return fmt.Sprintf("upload de licença não permitido para a venda %d", e.VendaID)
}

// RequireUpload exige que o usuário possa enviar a licença da venda, conforme
// CanUpload.
//
// Não modifica seus argumentos nem o estado do validador.
//
// Parâmetros:
//   - venda: venda cuja guia define os compositores; não pode ser nil.
//   - userID: identificador do usuário autenticado; nil representa usuário
//     anônimo.
//
// Retorna nil quando o envio é permitido.
//
// Erros: *UploadNaoPermitidoError quando CanUpload é false.
func (v *LicencaAccessValidator) RequireUpload(venda *Venda, userID *int64) error {
	if !v.CanUpload(venda, userID) {
		return &UploadNaoPermitidoError{VendaID: venda.ID, UserID: userID}
	}
	return nil
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
