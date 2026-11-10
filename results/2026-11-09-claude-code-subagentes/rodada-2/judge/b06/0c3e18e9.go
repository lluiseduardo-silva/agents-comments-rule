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

// UploadNaoPermitidoError é o erro devolvido por [LicencaAccessValidator.RequireUpload]
// quando o usuário não pode enviar a licença da venda.
type UploadNaoPermitidoError struct {
	// VendaID é o ID da venda cujo envio de licença foi recusado.
	VendaID int64
}

// Error devolve a mensagem do erro, que identifica a venda por VendaID.
//
// Não modifica o receptor.
func (e *UploadNaoPermitidoError) Error() string {
	return fmt.Sprintf("upload de licença não permitido para a venda %d", e.VendaID)
}

type LicencaAccessValidator struct {
	adminIDs map[int64]struct{}
}

func NewLicencaAccessValidator(adminIDs map[int64]struct{}) *LicencaAccessValidator {
	return &LicencaAccessValidator{adminIDs: adminIDs}
}

// CanUpload informa se o usuário userID pode enviar a licença da venda: só os
// compositores da guia da venda podem. Ser administrador ou comprador não concede,
// por si só, permissão de envio.
//
// Não modifica venda, userID nem o validador.
//
// venda é a venda cuja licença seria enviada e não pode ser nil. userID aponta para o
// ID do usuário autenticado; nil significa que não há usuário autenticado.
//
// Devolve true se userID constar em venda.Guia.Compositores; devolve false nos demais
// casos, inclusive quando userID é nil.
//
// Provoca panic (desreferência de ponteiro nil) se venda for nil e userID não for nil.
func (v *LicencaAccessValidator) CanUpload(venda *Venda, userID *int64) bool {
	if userID == nil {
		return false
	}
	return isCompositor(venda, *userID)
}

// RequireUpload exige que o usuário userID possa enviar a licença da venda, pela mesma
// regra de [LicencaAccessValidator.CanUpload].
//
// Não modifica venda, userID nem o validador.
//
// venda é a venda cuja licença seria enviada e não pode ser nil. userID aponta para o
// ID do usuário autenticado; nil significa que não há usuário autenticado.
//
// Devolve nil quando o envio é permitido.
//
// Devolve um [*UploadNaoPermitidoError] com o ID da venda quando CanUpload devolve
// false para os mesmos argumentos, o que inclui userID nil. Provoca panic
// (desreferência de ponteiro nil) se venda for nil.
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

// CanAccessAfterCancel informa se o usuário userID mantém o acesso à licença de uma
// venda cancelada: administradores e compositores da guia mantêm o acesso; o comprador
// perde, a menos que também seja administrador ou compositor da guia.
//
// Não modifica venda, userID nem o validador.
//
// venda é a venda cancelada e não pode ser nil. userID aponta para o ID do usuário
// autenticado; nil significa que não há usuário autenticado.
//
// Devolve true se userID for administrador ou constar em venda.Guia.Compositores;
// devolve false nos demais casos, inclusive quando userID é nil.
//
// Provoca panic (desreferência de ponteiro nil) se venda for nil e userID identificar
// um usuário que não é administrador.
//
// A função não consulta venda.Cancelada: o chamador deve usá-la apenas para vendas
// canceladas, porque para uma venda ativa ela nega o acesso do comprador.
func (v *LicencaAccessValidator) CanAccessAfterCancel(venda *Venda, userID *int64) bool {
	if userID == nil {
		return false
	}
	return v.isAdmin(*userID) || isCompositor(venda, *userID)
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
