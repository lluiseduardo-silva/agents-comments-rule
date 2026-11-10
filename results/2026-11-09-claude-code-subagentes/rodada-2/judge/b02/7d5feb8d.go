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

// CanUpload informa se o usuário pode enviar a licença da venda: somente compositor da
// guia pode; administrador e comprador não.
//
// Não modifica seus argumentos nem a instância.
//
// Parâmetros:
//   - venda: venda consultada; não pode ser nil.
//   - userID: identificador do usuário; nil representa usuário não autenticado.
//
// Retorna false quando userID é nil ou o usuário não é compositor da guia da venda.
func (v *LicencaAccessValidator) CanUpload(venda *Venda, userID *int64) bool {
	if userID == nil {
		return false
	}
	return isCompositor(venda, *userID)
}

// CanAccessAfterCancel informa se o usuário mantém acesso a uma venda cancelada:
// administrador e compositor da guia mantêm; o comprador perde.
//
// Não modifica seus argumentos nem a instância. Não consulta Venda.Cancelada: quem chama
// decide em quais vendas aplicar esta regra.
//
// Parâmetros:
//   - venda: venda consultada; não pode ser nil.
//   - userID: identificador do usuário; nil representa usuário não autenticado.
//
// Retorna false quando userID é nil ou o usuário é apenas o comprador da venda.
func (v *LicencaAccessValidator) CanAccessAfterCancel(venda *Venda, userID *int64) bool {
	if userID == nil {
		return false
	}
	if v.isAdmin(*userID) {
		return true
	}
	return isCompositor(venda, *userID)
}

// UploadNaoPermitidoError indica que o usuário não pode enviar licença para a venda.
//
// Campos:
//   - VendaID: identificador da venda cujo envio foi recusado.
type UploadNaoPermitidoError struct {
	VendaID int64
}

// Error devolve a mensagem do erro, que inclui o identificador da venda.
//
// Não modifica a instância.
func (e *UploadNaoPermitidoError) Error() string {
	return fmt.Sprintf("upload de licença não permitido para a venda %d", e.VendaID)
}

// RequireUpload exige que o usuário possa enviar a licença da venda, segundo CanUpload.
//
// Não modifica seus argumentos nem a instância.
//
// Parâmetros:
//   - venda: venda consultada; não pode ser nil.
//   - userID: identificador do usuário; nil representa usuário não autenticado.
//
// Retorna nil quando o envio é permitido.
//
// Erros: *UploadNaoPermitidoError quando CanUpload retorna false.
func (v *LicencaAccessValidator) RequireUpload(venda *Venda, userID *int64) error {
	if !v.CanUpload(venda, userID) {
		return &UploadNaoPermitidoError{VendaID: venda.ID}
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
