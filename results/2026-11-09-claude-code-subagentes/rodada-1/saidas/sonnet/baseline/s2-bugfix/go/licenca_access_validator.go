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

func (v *LicencaAccessValidator) CanUpload(venda *Venda, userID *int64) bool {
	if userID == nil {
		return false
	}
	return isCompositor(venda, *userID)
}

// UploadNaoPermitido indica que o usuario nao pode enviar licenca para a venda.
type UploadNaoPermitido struct {
	VendaID int64
}

func (e *UploadNaoPermitido) Error() string {
	return fmt.Sprintf("upload de licenca nao permitido para a venda %d", e.VendaID)
}

// RequireUpload retorna *UploadNaoPermitido quando CanUpload for falso.
func (v *LicencaAccessValidator) RequireUpload(venda *Venda, userID *int64) error {
	if !v.CanUpload(venda, userID) {
		return &UploadNaoPermitido{VendaID: venda.ID}
	}
	return nil
}

// CanAccessAfterCancel: em venda cancelada, admin e compositor da guia
// mantem o acesso e o comprador perde. Venda nao cancelada segue CanAccess.
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
