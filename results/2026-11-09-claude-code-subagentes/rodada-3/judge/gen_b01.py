import json
def T(name,doc_lines,summ=True,p=0,r=False,e=0,m="absent",mc=False,pf=False,n=None,ic=0,has=True):
    return dict(name=name,found=True,has_doc=has,summary_states_behavior=summ,params_documented=p,return_documented=r,errors_documented=e,mutation=m,mutation_complete=mc,partial_failure_documented=pf,narrative=n or [],inline_comments=ic,doc_lines=doc_lines)
def W(id,targets):
    json.dump(dict(id=id,prose_language="pt",idiomatic_format=True,targets=targets),open(id+".judge.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
W("083e18ef",[
 T("canUpload",10,r=True,n=[
  {"category":"deliberation","text":"Responder `true` para admin só adiaria essa recusa para depois de o objeto já ter sido gravado no storage, onde ficaria órfão."},
  {"category":"deliberation","text":"Enviar em nome de um titular equivaleria a aprovar a participação de um compositor; para destravar uma venda, o caminho administrativo é o `manual-complete`, que é auditado."}]),
 T("canAccessAfterCancel",6,r=True,ic=1),
 T("requireUpload",2,e=1),
 T("UploadNaoPermitido",2)])
W("f559cfda",[
 T("canUpload",8,n=[{"category":"deliberation","text":"Aceitar admin aqui só adiaria a recusa para depois do arquivo já estar no storage, deixando um objeto órfão."}]),
 T("canAccessAfterCancel",4,ic=1),
 T("requireUpload",1,e=1),
 T("UploadNaoPermitido",1)])
W("faabaca9",[
 T("canUpload",11,p=2,r=True,m="explicit",mc=True),
 T("canAccessAfterCancel",12,p=2,r=True,m="explicit",mc=True),
 T("requireUpload",9,p=2,e=1,m="explicit",mc=True),
 T("UploadNaoPermitido",4)])
W("72ecc21b",[
 T("canUpload",14,p=2,r=True,m="explicit",mc=True),
 T("canAccessAfterCancel",17,p=2,r=True,m="explicit",mc=True),
 T("requireUpload",14,p=2,e=1,m="explicit",mc=True),
 T("UploadNaoPermitido",6)])
W("90e9163a",[
 T("aplicar",16,p=2,e=3,m="explicit",mc=True),
 T("remover",13,p=2,r=True,m="explicit",mc=True)])
W("1ffba35e",[
 T("aplicar",12,p=2,e=3,m="explicit",mc=True),
 T("remover",11,p=2,r=True,m="explicit",mc=True)])
