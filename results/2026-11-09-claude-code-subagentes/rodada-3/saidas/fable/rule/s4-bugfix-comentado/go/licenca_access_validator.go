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

// UploadNaoPermitidoError é o erro que indica que um usuário não pode enviar a
// licença de uma venda. Ocorre quando o usuário não está identificado ou não é
// compositor da guia da venda.
//
// É devolvido por [LicencaAccessValidator.RequireUpload] como ponteiro; para
// reconhecê-lo, use errors.As com um alvo do tipo *UploadNaoPermitidoError.
type UploadNaoPermitidoError struct {
	// VendaID é o identificador da venda cujo envio de licença foi recusado.
	VendaID int64
}

// Error devolve a mensagem do erro, que inclui o identificador da venda.
//
// Não modifica o receptor.
//
// Pré-condição: o receptor não é nil; a violação causa pânico por
// desreferência de ponteiro nulo.
func (e *UploadNaoPermitidoError) Error() string {
	return fmt.Sprintf("upload de licença não permitido para a venda %d", e.VendaID)
}

type LicencaAccessValidator struct {
	adminIDs map[int64]struct{}
}

func NewLicencaAccessValidator(adminIDs map[int64]struct{}) *LicencaAccessValidator {
	return &LicencaAccessValidator{adminIDs: adminIDs}
}

// CanUpload informa se o usuário pode enviar a licença da venda: só compositor
// da guia da venda pode enviar; ser administrador ou comprador não concede a
// permissão.
//
// Não modifica venda, userID nem o validador, e não acessa nada externo.
//
// venda é a venda cuja licença seria enviada. userID é o identificador do
// usuário que tenta o envio; nil significa usuário não identificado.
//
// Devolve true quando userID identifica um compositor da guia da venda, e
// false nos demais casos, inclusive quando userID é nil.
//
// Pré-condição: venda não é nil; a violação pode causar pânico por
// desreferência de ponteiro nulo.
func (v *LicencaAccessValidator) CanUpload(venda *Venda, userID *int64) bool {
	if userID == nil {
		return false
	}
	return isCompositor(venda, *userID)
}

// RequireUpload exige que o usuário possa enviar a licença da venda, pela
// mesma regra de [LicencaAccessValidator.CanUpload].
//
// Não modifica venda, userID nem o validador, e não acessa nada externo.
//
// venda é a venda cuja licença seria enviada. userID é o identificador do
// usuário que tenta o envio; nil significa usuário não identificado.
//
// Devolve nil quando o envio é permitido. Devolve um *UploadNaoPermitidoError
// com o identificador da venda quando CanUpload devolve false para os mesmos
// argumentos.
//
// Pré-condição: venda não é nil; a violação causa pânico por desreferência de
// ponteiro nulo.
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

// CanAccessAfterCancel informa se o usuário tem acesso à licença de uma venda
// cancelada: administrador e compositor da guia da venda mantêm o acesso; o
// comprador perde.
//
// Não modifica venda, userID nem o validador, e não acessa nada externo.
//
// venda é a venda consultada; o campo Cancelada não é verificado, de modo que
// a regra de venda cancelada é aplicada qualquer que seja o seu valor. userID
// é o identificador do usuário que pede o acesso; nil significa usuário não
// identificado.
//
// Devolve true quando userID identifica um administrador ou um compositor da
// guia da venda, e false nos demais casos, inclusive quando userID é nil ou
// identifica apenas o comprador.
//
// Pré-condição: o validador e venda não são nil; a violação pode causar pânico
// por desreferência de ponteiro nulo.
func (v *LicencaAccessValidator) CanAccessAfterCancel(venda *Venda, userID *int64) bool {
	if userID == nil {
		return false
	}
	if v.isAdmin(*userID) {
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
