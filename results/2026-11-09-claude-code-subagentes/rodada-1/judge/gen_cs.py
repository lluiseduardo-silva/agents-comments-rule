import json
def T(name, doc=True, summ=True, p=0, ret=False, err=0, mut="absent", comp=False, pf=False, nar=None, inl=0, lines=0):
    return dict(name=name, found=True, has_doc=doc, summary_states_behavior=summ, params_documented=p,
        return_documented=ret, errors_documented=err, mutation=mut, mutation_complete=comp,
        partial_failure_documented=pf, narrative=nar or [], inline_comments=inl, doc_lines=lines)
def W(id, lang, idi, targets):
    json.dump(dict(id=id, prose_language=lang, idiomatic_format=idi, targets=targets), open(id+".judge.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
W("776a08fa","pt",True,[
 T("canUpload",p=2,ret=True,mut="explicit",comp=True,lines=12),
 T("canAccessAfterCancel",p=2,ret=True,mut="explicit",comp=True,lines=14),
 T("requireUpload",p=2,err=1,mut="explicit",comp=True,lines=9),
 T("UploadNaoPermitido",lines=3)])
W("2227d883","pt",True,[
 T("aplicar",p=2,err=3,mut="explicit",comp=True,lines=15),
 T("remover",p=2,ret=True,mut="explicit",comp=True,lines=10)])
nd=lambda n:T(n,doc=False,summ=False)
t=[nd("canUpload"),nd("canAccessAfterCancel"),nd("requireUpload"),nd("UploadNaoPermitido")]
t[0]["params_documented"]=0
W("a3687b81","none",None,t)
W("d3fe4f9a","none",None,[nd("Estoque"),nd("construtor de Estoque"),
 dict(nd("repor"),inline_comments=1),nd("quantidade"),dict(nd("reservar"),inline_comments=2),nd("normalizarSkus")])
W("714e49f4","pt",True,[
 T("aplicar",summ=False,mut="absent",comp=False,lines=5,inl=1,nar=[
  {"category":"emphasis","text":"⚠ **NÃO remover o limite.**"},
  {"category":"history","text":"Antes do PR 2291 dava para empilhar cupom à vontade e o Financeiro reclamou do prejuízo em novembro."},
  {"category":"attribution","text":"A Carla decidiu travar pelo <c>_maxCuponsPorPedido</c>"},
  {"category":"deliberation","text":"em vez de validar no front, que era a outra opção discutida."},
  {"category":"attribution","text":"// Limite pedido pelo Financeiro"}]),
 T("remover",ret=True,mut="explicit",comp=True,lines=4)])
W("daffbf0d","pt",True,[
 T("Estoque",lines=7),
 T("construtor de Estoque",p=1,err=1,lines=5),
 T("repor",p=2,err=2,mut="explicit",comp=True,lines=11),
 T("quantidade",p=1,ret=True,mut="explicit",comp=True,lines=7),
 T("reservar",p=2,err=2,mut="explicit",comp=True,pf=True,lines=13),
 T("normalizarSkus",p=1,ret=True,mut="explicit",comp=True,lines=10)])
