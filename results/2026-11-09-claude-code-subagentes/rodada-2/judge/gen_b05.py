import json
def T(name, doc=True, summ=True, p=0, r=False, e=0, m="absent", mc=False, pf=False, n=None, i=0, dl=0):
    return dict(name=name, found=True, has_doc=doc, summary_states_behavior=summ, params_documented=p,
        return_documented=r, errors_documented=e, mutation=m, mutation_complete=mc,
        partial_failure_documented=pf, narrative=n or [], inline_comments=i, doc_lines=dl)
def W(id, lang, idio, ts):
    json.dump(dict(id=id, prose_language=lang, idiomatic_format=idio, targets=ts), open(id+".judge.json","w"), ensure_ascii=False, indent=2)

W("07d359a8","pt",True,[
 T("canUpload",p=0,r=False,n=[dict(category="attribution",text="Admin não envia (LIC-482)")],dl=2),
 T("canAccessAfterCancel",dl=2),
 T("requireUpload",e=1,dl=1),
 T("UploadNaoPermitido",doc=False,summ=False,dl=0)])

ex=dict(m="explicit",mc=True)
W("322daae2","pt",True,[
 T("canUpload",p=2,r=True,dl=13,**ex),
 T("canAccessAfterCancel",p=2,r=True,dl=14,**ex),
 T("requireUpload",p=2,r=False,e=1,dl=11,**ex),
 T("UploadNaoPermitido",dl=1)])

W("544b7b9f","pt",True,[
 T("canUpload",p=1,r=True,dl=16,n=[
   dict(category="deliberation",text="Responder `true` para admin seria prometer um upload que falha logo adiante, deixando um objeto órfão no storage;"),
   dict(category="deliberation",text="para o admin enviar de verdade, a confirmação teria de aceitar o compositor como parâmetro, o que daria ao admin o poder de aprovar a participação de um compositor;")]),
 T("canAccessAfterCancel",p=1,r=True,i=1,dl=10),
 T("requireUpload",p=1,r=False,e=1,dl=6),
 T("UploadNaoPermitido",dl=5)])

W("b070d424","pt",True,[
 T("canUpload",p=2,r=True,dl=11,**ex),
 T("canAccessAfterCancel",p=2,r=True,dl=14,**ex),
 T("requireUpload",p=2,r=False,e=1,dl=10,**ex),
 T("UploadNaoPermitido",dl=3)])

W("cec1129c","pt",True,[
 T("canUpload",p=2,r=True,dl=10,**ex),
 T("canAccessAfterCancel",p=2,r=True,dl=12,**ex),
 T("requireUpload",p=2,r=False,e=1,dl=9,**ex),
 T("UploadNaoPermitido",dl=6)])

W("519644b9","pt",True,[
 T("Estoque",dl=10),
 T("construtor de Estoque",p=1,e=1,dl=10),
 T("repor",p=2,e=2,dl=10,**ex),
 T("quantidade",p=1,r=True,dl=8,**ex),
 T("reservar",p=2,e=2,pf=True,dl=15,**ex),
 T("normalizarSkus",p=1,r=True,dl=10,**ex)])
