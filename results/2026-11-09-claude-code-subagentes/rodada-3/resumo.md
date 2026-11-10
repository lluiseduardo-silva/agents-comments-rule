# Benchmark da rule de comentários

48 execuções avaliadas.

"baseline" é o projeto sem a rule; "rule" é o mesmo projeto com ela. As colunas de contrato vêm da avaliação cega (`bench/RUBRIC.md`); "tokens vazados" é a checagem determinística dos nomes, tickets e datas plantados no pedido. "contrato" é a média, por declaração-alvo, dos itens aplicáveis: doc, parâmetros, retorno, erros, mutação explícita e falha parcial.

## Geral

| | execuções | doc | parâmetros | retorno | erros | mutação explícita | mutação completa | falha parcial | **contrato** | frases narrativas | exec. sem narrativa | tokens vazados | exec. sem vazamento | linhas/doc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fable baseline | 5 | 100% | 8% | 75% | 60% | 8% | 15% | n/a | **56%** | 17 | 0/5 | 15 | 2/5 | 4.7 |
| fable rule | 11 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 11/11 | 0 | 11/11 | 15.1 |
| opus baseline | 5 | 88% | 0% | 25% | 60% | 8% | 15% | n/a | **45%** | 13 | 1/5 | 14 | 2/5 | 2.7 |
| opus rule | 11 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 11/11 | 0 | 11/11 | 12.0 |
| sonnet baseline | 5 | 88% | 0% | 0% | 60% | 0% | 0% | n/a | **41%** | 18 | 0/5 | 33 | 2/5 | 3.9 |
| sonnet rule | 11 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 11/11 | 0 | 11/11 | 10.5 |

## Por cenário

| | execuções | doc | parâmetros | retorno | erros | mutação explícita | mutação completa | falha parcial | **contrato** | frases narrativas | exec. sem narrativa | tokens vazados | exec. sem vazamento | linhas/doc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| s1-greenfield · fable rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 2/2 | 0 | 2/2 | 14.8 |
| s1-greenfield · opus rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 2/2 | 0 | 2/2 | 11.3 |
| s1-greenfield · sonnet rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 2/2 | 0 | 2/2 | 9.7 |
| s4-bugfix-comentado · fable baseline | 3 | 100% | 0% | 67% | 100% | 0% | 0% | n/a | **58%** | 7 | 0/3 | 15 | 0/3 | 5.1 |
| s4-bugfix-comentado · fable rule | 6 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 6/6 | 0 | 6/6 | 15.0 |
| s4-bugfix-comentado · opus baseline | 3 | 83% | 0% | 0% | 100% | 0% | 0% | n/a | **46%** | 3 | 1/3 | 14 | 0/3 | 2.7 |
| s4-bugfix-comentado · opus rule | 6 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 6/6 | 0 | 6/6 | 12.1 |
| s4-bugfix-comentado · sonnet baseline | 3 | 100% | 0% | 0% | 100% | 0% | 0% | n/a | **50%** | 9 | 0/3 | 33 | 0/3 | 4.6 |
| s4-bugfix-comentado · sonnet rule | 6 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 6/6 | 0 | 6/6 | 10.3 |
| s3-infested · fable baseline | 2 | 100% | 25% | 100% | 0% | 25% | 50% | n/a | **50%** | 10 | 0/2 | 0 | 2/2 | 3.5 |
| s3-infested · fable rule | 3 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 3/3 | 0 | 3/3 | 15.7 |
| s3-infested · opus baseline | 2 | 100% | 0% | 100% | 0% | 25% | 50% | n/a | **44%** | 10 | 0/2 | 0 | 2/2 | 2.8 |
| s3-infested · opus rule | 3 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 3/3 | 0 | 3/3 | 13.5 |
| s3-infested · sonnet baseline | 2 | 50% | 0% | 0% | 0% | 0% | 0% | n/a | **13%** | 9 | 0/2 | 0 | 2/2 | 2.0 |
| s3-infested · sonnet rule | 3 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 3/3 | 0 | 3/3 | 13.2 |

## Por linguagem

| | execuções | doc | parâmetros | retorno | erros | mutação explícita | mutação completa | falha parcial | **contrato** | frases narrativas | exec. sem narrativa | tokens vazados | exec. sem vazamento | linhas/doc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kotlin · fable baseline | 2 | 100% | 10% | 33% | 50% | 0% | 20% | n/a | **48%** | 8 | 0/2 | 8 | 1/2 | 5.3 |
| Kotlin · fable rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 2/2 | 0 | 2/2 | 12.5 |
| Kotlin · opus baseline | 2 | 100% | 0% | 33% | 50% | 0% | 20% | n/a | **46%** | 5 | 0/2 | 4 | 1/2 | 3.3 |
| Kotlin · opus rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 2/2 | 0 | 2/2 | 11.7 |
| Kotlin · sonnet baseline | 2 | 83% | 0% | 0% | 50% | 0% | 0% | n/a | **38%** | 8 | 0/2 | 11 | 1/2 | 4.8 |
| Kotlin · sonnet rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 2/2 | 0 | 2/2 | 10.7 |
| Rust · fable baseline | 1 | 100% | 0% | 100% | 100% | 0% | 0% | n/a | **63%** | 2 | 0/1 | 4 | 0/1 | 5.0 |
| Rust · fable rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 16.5 |
| Rust · opus baseline | 1 | 100% | 0% | 0% | 100% | 0% | 0% | n/a | **50%** | 2 | 0/1 | 4 | 0/1 | 4.0 |
| Rust · opus rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 14.5 |
| Rust · sonnet baseline | 1 | 100% | 0% | 0% | 100% | 0% | 0% | n/a | **50%** | 3 | 0/1 | 14 | 0/1 | 4.0 |
| Rust · sonnet rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 10.3 |
| TypeScript · fable rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 2/2 | 0 | 2/2 | 13.3 |
| TypeScript · opus rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 2/2 | 0 | 2/2 | 10.3 |
| TypeScript · sonnet rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 2/2 | 0 | 2/2 | 10.0 |
| Python · fable baseline | 1 | 100% | 0% | 100% | 100% | 0% | 0% | n/a | **63%** | 2 | 0/1 | 3 | 0/1 | 4.5 |
| Python · fable rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 2/2 | 0 | 2/2 | 14.6 |
| Python · opus baseline | 1 | 50% | 0% | 0% | 100% | 0% | 0% | n/a | **38%** | 0 | 1/1 | 6 | 0/1 | 0.5 |
| Python · opus rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 2/2 | 0 | 2/2 | 13.9 |
| Python · sonnet baseline | 1 | 100% | 0% | 0% | 100% | 0% | 0% | n/a | **50%** | 2 | 0/1 | 8 | 0/1 | 3.8 |
| Python · sonnet rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 2/2 | 0 | 2/2 | 11.4 |
| Go · fable baseline | 1 | 100% | 25% | 100% | 0% | 50% | 50% | n/a | **56%** | 5 | 0/1 | 0 | 1/1 | 2.5 |
| Go · fable rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 2/2 | 0 | 2/2 | 14.5 |
| Go · opus baseline | 1 | 100% | 0% | 100% | 0% | 50% | 50% | n/a | **50%** | 6 | 0/1 | 0 | 1/1 | 2.5 |
| Go · opus rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 2/2 | 0 | 2/2 | 13.2 |
| Go · sonnet baseline | 1 | 50% | 0% | 0% | 0% | 0% | 0% | n/a | **13%** | 5 | 0/1 | 0 | 1/1 | 1.5 |
| Go · sonnet rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 2/2 | 0 | 2/2 | 12.5 |
| C# · fable rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 2/2 | 0 | 2/2 | 17.9 |
| C# · opus rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 2/2 | 0 | 2/2 | 9.8 |
| C# · sonnet rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 2/2 | 0 | 2/2 | 8.9 |

## Cenário 3: o que aconteceu com a narrativa que já estava no arquivo

Tokens restantes no arquivo final, somados nas execuções (restantes/possíveis). "alterada" deveria ir a zero; "intocada" deveria ficar inteira.

| condição | função alterada (`aplicar`) | função intocada (`totalDeCupons`) | comentário da classe | vindos do pedido |
|---|---|---|---|---|
| fable baseline | 12/12 | 10/10 | 4/4 | 0/6 |
| fable rule | 0/18 | 15/15 | 6/6 | 0/9 |
| opus baseline | 12/12 | 10/10 | 4/4 | 0/6 |
| opus rule | 0/18 | 15/15 | 6/6 | 0/9 |
| sonnet baseline | 12/12 | 10/10 | 4/4 | 0/6 |
| sonnet rule | 0/18 | 15/15 | 6/6 | 0/9 |

## Formato e idioma

| condição | formato idiomático | prosa |
|---|---|---|
| fable baseline | 4/5 | pt: 5 |
| fable rule | 11/11 | pt: 11 |
| opus baseline | 5/5 | pt: 5 |
| opus rule | 11/11 | pt: 11 |
| sonnet baseline | 5/5 | pt: 5 |
| sonnet rule | 11/11 | pt: 11 |

## Falhas na condição "fable baseline"

- s4-bugfix-comentado · Rust · `canUpload` (083e18ef): falta params, mutation
- s4-bugfix-comentado · Rust · `canAccessAfterCancel` (083e18ef): falta params, mutation
- s4-bugfix-comentado · Rust · `requireUpload` (083e18ef): falta params, mutation
- s4-bugfix-comentado · Rust · `canUpload` (083e18ef): narrativa [deliberation] "Responder `true` para admin só adiaria essa recusa para depois de o objeto já ter sido gravado no storage, onde ficaria órfão."
- s4-bugfix-comentado · Rust · `canUpload` (083e18ef): narrativa [deliberation] "Enviar em nome de um titular equivaleria a aprovar a participação de um compositor; para destravar uma venda, o caminho administrativo é o `manual-complete`, que é auditado."
- s4-bugfix-comentado · Rust (083e18ef): tokens do pedido no arquivo: órfão, manual-complete, titular, auditado
- s3-infested · Kotlin · `aplicar` (275ce100): falta params, errors, mutation
- s3-infested · Kotlin · `remover` (275ce100): falta params (parcial), mutation
- s3-infested · Kotlin · `aplicar` (275ce100): narrativa [emphasis] "⚠ **NÃO remover o limite.**"
- s3-infested · Kotlin · `aplicar` (275ce100): narrativa [history] "Antes do PR 2291 dava para empilhar cupom à vontade e o Financeiro reclamou do prejuízo em novembro."
- s3-infested · Kotlin · `aplicar` (275ce100): narrativa [attribution] "A Carla decidiu travar pelo `maxCuponsPorPedido`"
- s3-infested · Kotlin · `aplicar` (275ce100): narrativa [deliberation] "em vez de validar no front, que era a outra opção discutida."
- s3-infested · Kotlin · `aplicar` (275ce100): narrativa [attribution] "// Limite pedido pelo Financeiro"
- s4-bugfix-comentado · Kotlin · `canUpload` (3845879f): falta params, ret, mutation
- s4-bugfix-comentado · Kotlin · `canAccessAfterCancel` (3845879f): falta params, ret, mutation
- s4-bugfix-comentado · Kotlin · `requireUpload` (3845879f): falta params, mutation
- s4-bugfix-comentado · Kotlin · `canUpload` (3845879f): narrativa [deliberation] "Admin fica de fora de propósito."
- s4-bugfix-comentado · Kotlin · `canUpload` (3845879f): narrativa [deliberation] "aceitar admin aqui só empurraria a recusa para depois do envio, deixando um objeto órfão no S3."
- s4-bugfix-comentado · Kotlin · `canUpload` (3845879f): narrativa [deliberation] "Liberar de verdade exigiria que o admin agisse em nome de um titular, o que equivale a aprovar a participação de um compositor."
- s4-bugfix-comentado · Kotlin (3845879f): tokens do pedido no arquivo: S3, 403, órfão, assertFileOwner, LicenseUploadService, manual-complete, titular, auditado
- s4-bugfix-comentado · Python · `canUpload` (6f23cc3e): falta params, mutation
- s4-bugfix-comentado · Python · `canAccessAfterCancel` (6f23cc3e): falta params, mutation
- s4-bugfix-comentado · Python · `requireUpload` (6f23cc3e): falta params, mutation
- s4-bugfix-comentado · Python · `canUpload` (6f23cc3e): narrativa [deliberation] "Ser admin não concede nada aqui, de propósito."
- s4-bugfix-comentado · Python · `canUpload` (6f23cc3e): narrativa [deliberation] "enviar em nome de um titular seria aprovar a participação dele."
- s4-bugfix-comentado · Python (6f23cc3e): tokens do pedido no arquivo: manual-complete, titular, auditado
- s3-infested · Go · `aplicar` (2242deb3): falta params, errors, mutation
- s3-infested · Go · `remover` (2242deb3): falta params (parcial)
- s3-infested · Go · `aplicar` (2242deb3): narrativa [emphasis] "⚠ **NÃO remover o limite.**"
- s3-infested · Go · `aplicar` (2242deb3): narrativa [history] "Antes do PR 2291 dava para empilhar cupom à vontade"
- s3-infested · Go · `aplicar` (2242deb3): narrativa [attribution] "A Carla decidiu travar pelo maxCuponsPorPedido"
- s3-infested · Go · `aplicar` (2242deb3): narrativa [deliberation] "em vez de validar no front, que era a outra opção discutida."
- s3-infested · Go · `aplicar` (2242deb3): narrativa [attribution] "Limite pedido pelo Financeiro"

## Falhas na condição "fable rule"

Nenhuma.

## Falhas na condição "opus baseline"

- s4-bugfix-comentado · Kotlin · `canUpload` (f559cfda): falta params, ret, mutation
- s4-bugfix-comentado · Kotlin · `canAccessAfterCancel` (f559cfda): falta params, ret, mutation
- s4-bugfix-comentado · Kotlin · `requireUpload` (f559cfda): falta params, mutation
- s4-bugfix-comentado · Kotlin · `canUpload` (f559cfda): narrativa [deliberation] "Aceitar admin aqui só adiaria a recusa para depois do arquivo já estar no storage, deixando um objeto órfão."
- s4-bugfix-comentado · Kotlin (f559cfda): tokens do pedido no arquivo: órfão, manual-complete, titular, auditado
- s3-infested · Go · `aplicar` (254956d8): falta params, errors, mutation
- s3-infested · Go · `remover` (254956d8): falta params
- s3-infested · Go · `aplicar` (254956d8): narrativa [emphasis] "⚠ **NÃO remover o limite.**"
- s3-infested · Go · `aplicar` (254956d8): narrativa [history] "Antes do PR 2291 dava para empilhar cupom à vontade e o Financeiro reclamou do prejuízo em novembro."
- s3-infested · Go · `aplicar` (254956d8): narrativa [attribution] "Antes do PR 2291 dava para empilhar cupom à vontade e o Financeiro reclamou do prejuízo em novembro."
- s3-infested · Go · `aplicar` (254956d8): narrativa [attribution] "A Carla decidiu travar pelo maxCuponsPorPedido em vez de validar no front, que era a outra opção discutida."
- s3-infested · Go · `aplicar` (254956d8): narrativa [deliberation] "A Carla decidiu travar pelo maxCuponsPorPedido em vez de validar no front, que era a outra opção discutida."
- s3-infested · Go · `aplicar` (254956d8): narrativa [attribution] "Limite pedido pelo Financeiro"
- s4-bugfix-comentado · Python · `canUpload` (70587e1c): falta doc, params, ret, mutation
- s4-bugfix-comentado · Python · `canAccessAfterCancel` (70587e1c): falta doc, params, ret, mutation
- s4-bugfix-comentado · Python · `requireUpload` (70587e1c): falta params, mutation
- s4-bugfix-comentado · Python (70587e1c): tokens do pedido no arquivo: S3, órfão, assertFileOwner, manual-complete, titular, auditado
- s4-bugfix-comentado · Rust · `canUpload` (8ed28406): falta params, ret, mutation
- s4-bugfix-comentado · Rust · `canAccessAfterCancel` (8ed28406): falta params, ret, mutation
- s4-bugfix-comentado · Rust · `requireUpload` (8ed28406): falta params, mutation
- s4-bugfix-comentado · Rust · `canUpload` (8ed28406): narrativa [deliberation] "Liberar o admin aqui não habilita nada; a confirmação falha depois e o objeto já gravado no storage fica órfão."
- s4-bugfix-comentado · Rust · `canUpload` (8ed28406): narrativa [deliberation] "Permitir upload em nome de outro usuário daria ao admin o poder de aprovar a participação de um compositor."
- s4-bugfix-comentado · Rust (8ed28406): tokens do pedido no arquivo: órfão, manual-complete, titular, auditado
- s3-infested · Kotlin · `aplicar` (46efef2d): falta params, errors, mutation
- s3-infested · Kotlin · `remover` (46efef2d): falta params, mutation
- s3-infested · Kotlin · `aplicar` (46efef2d): narrativa [emphasis] "⚠ **NÃO remover o limite.**"
- s3-infested · Kotlin · `aplicar` (46efef2d): narrativa [history] "Antes do PR 2291 dava para empilhar cupom à vontade e o Financeiro reclamou do prejuízo em novembro."
- s3-infested · Kotlin · `aplicar` (46efef2d): narrativa [attribution] "A Carla decidiu travar pelo `maxCuponsPorPedido` em vez de validar no front, que era a outra opção discutida."
- s3-infested · Kotlin · `aplicar` (46efef2d): narrativa [attribution] "// Limite pedido pelo Financeiro"

## Falhas na condição "opus rule"

Nenhuma.

## Falhas na condição "sonnet baseline"

- s4-bugfix-comentado · Python · `canUpload` (8b41fcf6): falta params, ret, mutation
- s4-bugfix-comentado · Python · `canAccessAfterCancel` (8b41fcf6): falta params, ret, mutation
- s4-bugfix-comentado · Python · `requireUpload` (8b41fcf6): falta params, mutation
- s4-bugfix-comentado · Python · `canUpload` (8b41fcf6): narrativa [attribution] "Admin NÃO envia (LIC-482)"
- s4-bugfix-comentado · Python · `canUpload` (8b41fcf6): narrativa [emphasis] "Admin NÃO envia (LIC-482)"
- s4-bugfix-comentado · Python (8b41fcf6): tokens do pedido no arquivo: LIC-482, S3, 403, órfão, assertFileOwner, manual-complete, titular, auditado
- s3-infested · Go · `aplicar` (dfe10797): falta params, errors, mutation
- s3-infested · Go · `remover` (dfe10797): falta doc, params, ret, mutation
- s3-infested · Go · `aplicar` (dfe10797): narrativa [emphasis] "⚠ **NÃO remover o limite.**"
- s3-infested · Go · `aplicar` (dfe10797): narrativa [history] "Antes do PR 2291 dava para empilhar cupom à vontade"
- s3-infested · Go · `aplicar` (dfe10797): narrativa [attribution] "A Carla decidiu travar pelo maxCuponsPorPedido"
- s3-infested · Go · `aplicar` (dfe10797): narrativa [deliberation] "em vez de validar no front, que era a outra opção discutida."
- s3-infested · Go · `aplicar` (dfe10797): narrativa [attribution] "Limite pedido pelo Financeiro"
- s4-bugfix-comentado · Kotlin · `canUpload` (7de266db): falta params, ret, mutation
- s4-bugfix-comentado · Kotlin · `canAccessAfterCancel` (7de266db): falta params, ret, mutation
- s4-bugfix-comentado · Kotlin · `requireUpload` (7de266db): falta params, mutation
- s4-bugfix-comentado · Kotlin · `canUpload` (7de266db): narrativa [attribution] "Admin NÃO envia (LIC-482)"
- s4-bugfix-comentado · Kotlin · `canUpload` (7de266db): narrativa [emphasis] "Admin NÃO envia (LIC-482)"
- s4-bugfix-comentado · Kotlin · `canUpload` (7de266db): narrativa [history] "antes este método devolvia true para admin, mas o `LicenseUploadService.assertUploadAllowed` derrubava a chamada com 403 em `assertFileOwner` (o arquivo é do titular), deixando um objeto órfão no S3."
- s4-bugfix-comentado · Kotlin · `canUpload` (7de266db): narrativa [deliberation] "Habilitar de verdade exigiria um `onBehalfOfUserId` no confirm, o que daria ao admin o poder de aprovar a participação de um compositor."
- s4-bugfix-comentado · Kotlin (7de266db): tokens do pedido no arquivo: LIC-482, S3, 403, órfão, assertFileOwner, LicenseUploadService, assertUploadAllowed, manual-complete, onBehalfOfUserId, titular, auditado
- s4-bugfix-comentado · Rust · `canUpload` (198db170): falta params, ret, mutation
- s4-bugfix-comentado · Rust · `canAccessAfterCancel` (198db170): falta params, ret, mutation
- s4-bugfix-comentado · Rust · `requireUpload` (198db170): falta params, mutation
- s4-bugfix-comentado · Rust · `canUpload` (198db170): narrativa [attribution] "LIC-482 (PR9, passo D2)"
- s4-bugfix-comentado · Rust · `canUpload` (198db170): narrativa [history] "O admin deixou de ser aceito porque `LicenseUploadService.assertUploadAllowed` ja rejeitava o admin com 403 em `assertFileOwner` (o arquivo pertence ao titular), deixando um objeto orfao no S3 a cada tentativa (incidente"
- s4-bugfix-comentado · Rust · `canUpload` (198db170): narrativa [deliberation] "Habilitar de verdade exigiria um `onBehalfOfUserId` no confirm, dando ao admin o poder de aprovar a participacao de um compositor."
- s4-bugfix-comentado · Rust (198db170): tokens do pedido no arquivo: LIC-482, D2, PR9, 14/10, S3, 403, incidente, assertFileOwner, LicenseUploadService, assertUploadAllowed, manual-complete, onBehalfOfUserId, titular, auditado
- s3-infested · Kotlin · `aplicar` (1003d891): falta params, errors, mutation
- s3-infested · Kotlin · `remover` (1003d891): falta doc, params, ret, mutation
- s3-infested · Kotlin · `aplicar` (1003d891): narrativa [emphasis] "⚠ **NÃO remover o limite.**"
- s3-infested · Kotlin · `aplicar` (1003d891): narrativa [history] "Antes do PR 2291 dava para empilhar cupom à vontade e o Financeiro reclamou do prejuízo em novembro."
- s3-infested · Kotlin · `aplicar` (1003d891): narrativa [attribution] "A Carla decidiu travar pelo `maxCuponsPorPedido` em vez de validar no front, que era a outra opção discutida."
- s3-infested · Kotlin · `aplicar` (1003d891): narrativa [attribution] "// Limite pedido pelo Financeiro"

## Falhas na condição "sonnet rule"

Nenhuma.
