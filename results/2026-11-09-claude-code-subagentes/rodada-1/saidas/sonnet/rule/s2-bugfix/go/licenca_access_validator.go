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

// UploadNaoPermitidoError indica que o usuário não pode enviar licença para a venda.
//
// Campos: VendaID é o identificador da venda alvo; UserID é o usuário que tentou o
// envio, ou nil quando não havia usuário autenticado.
type UploadNaoPermitidoError struct {
	VendaID int64
	UserID  *int64
}

// Error devolve a mensagem do erro.
//
// Não modifica a instância.
//
// Retorna o texto descrevendo a venda e, quando existir, o usuário recusado.
func (e *UploadNaoPermitidoError) Error() string {
	if e.UserID == nil {
		return fmt.Sprintf("upload de licença não permitido: venda %d, usuário não autenticado", e.VendaID)
	}
	return fmt.Sprintf("upload de licença não permitido: venda %d, usuário %d", e.VendaID, *e.UserID)
}

// CanUpload informa se o usuário pode enviar licença para a venda: somente compositor
// da guia pode; administrador não.
//
// Não modifica seus argumentos nem a instância.
//
// Parâmetros: venda é a venda alvo, não nula; userID é o usuário solicitante, nil quando
// não há usuário autenticado.
//
// Retorna true apenas se userID não for nil e for compositor da guia da venda; false
// caso contrário.
func (v *LicencaAccessValidator) CanUpload(venda *Venda, userID *int64) bool {
	if userID == nil {
		return false
	}
	return isCompositor(venda, *userID)
}

// CanAccessAfterCancel informa se o usuário mantém acesso à licença de uma venda
// cancelada: administrador e compositor da guia mantêm; o comprador perde.
//
// Não modifica seus argumentos nem a instância.
//
// Parâmetros: venda é a venda alvo, não nula; userID é o usuário solicitante, nil quando
// não há usuário autenticado. Para venda não cancelada, o resultado é o de CanAccess.
//
// Retorna true se o usuário mantém o acesso; false caso contrário, inclusive quando
// userID é nil.
func (v *LicencaAccessValidator) CanAccessAfterCancel(venda *Venda, userID *int64) bool {
	if !venda.Cancelada {
		return v.CanAccess(venda, userID)
	}
	if userID == nil {
		return false
	}
	return v.isAdmin(*userID) || isCompositor(venda, *userID)
}

// RequireUpload exige que o usuário possa enviar licença para a venda.
//
// Não modifica seus argumentos nem a instância.
//
// Parâmetros: venda é a venda alvo, não nula; userID é o usuário solicitante, nil quando
// não há usuário autenticado.
//
// Retorna nil quando CanUpload é verdadeiro.
//
// Erros: *UploadNaoPermitidoError quando CanUpload é falso.
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
