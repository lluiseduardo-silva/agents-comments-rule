# Benchmark da rule de comentários

36 execuções avaliadas.

"baseline" é o projeto sem a rule; "rule" é o mesmo projeto com ela. As colunas de contrato vêm da avaliação cega (`bench/RUBRIC.md`); "tokens vazados" é a checagem determinística dos nomes, tickets e datas plantados no pedido. "contrato" é a média, por declaração-alvo, dos itens aplicáveis: doc, parâmetros, retorno, erros, mutação explícita e falha parcial.

## Geral

| | execuções | doc | parâmetros | retorno | erros | mutação explícita | mutação completa | falha parcial | **contrato** | frases narrativas | exec. sem narrativa | tokens vazados | exec. sem vazamento | linhas/doc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fable baseline | 6 | 83% | 8% | 17% | 100% | 0% | 0% | n/a | **46%** | 5 | 2/6 | 26 | 0/6 | 4.8 |
| fable rule | 6 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 6/6 | 0 | 6/6 | 14.5 |
| opus baseline | 6 | 67% | 0% | 0% | 67% | 0% | 0% | n/a | **33%** | 9 | 1/6 | 19 | 0/6 | 3.4 |
| opus rule | 6 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 6/6 | 0 | 6/6 | 11.6 |
| sonnet baseline | 3 | 92% | 0% | 17% | 100% | 0% | 0% | n/a | **50%** | 14 | 0/3 | 31 | 0/3 | 4.8 |
| sonnet rule | 9 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 9/9 | 0 | 9/9 | 10.3 |

## Por cenário

| | execuções | doc | parâmetros | retorno | erros | mutação explícita | mutação completa | falha parcial | **contrato** | frases narrativas | exec. sem narrativa | tokens vazados | exec. sem vazamento | linhas/doc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| s1-greenfield · sonnet rule | 3 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 3/3 | 0 | 3/3 | 11.0 |
| s2-bugfix · fable baseline | 3 | 67% | 0% | 0% | 100% | 0% | 0% | n/a | **35%** | 1 | 2/3 | 7 | 0/3 | 1.3 |
| s2-bugfix · opus baseline | 3 | 33% | 0% | 0% | 33% | 0% | 0% | n/a | **17%** | 2 | 1/3 | 7 | 0/3 | 0.5 |
| s4-bugfix-comentado · fable baseline | 3 | 100% | 17% | 33% | 100% | 0% | 0% | n/a | **57%** | 4 | 0/3 | 19 | 0/3 | 8.3 |
| s4-bugfix-comentado · fable rule | 6 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 6/6 | 0 | 6/6 | 14.5 |
| s4-bugfix-comentado · opus baseline | 3 | 100% | 0% | 0% | 100% | 0% | 0% | n/a | **50%** | 7 | 0/3 | 12 | 0/3 | 6.3 |
| s4-bugfix-comentado · opus rule | 6 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 6/6 | 0 | 6/6 | 11.6 |
| s4-bugfix-comentado · sonnet baseline | 3 | 92% | 0% | 17% | 100% | 0% | 0% | n/a | **50%** | 14 | 0/3 | 31 | 0/3 | 4.8 |
| s4-bugfix-comentado · sonnet rule | 6 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 6/6 | 0 | 6/6 | 9.8 |

## Por linguagem

| | execuções | doc | parâmetros | retorno | erros | mutação explícita | mutação completa | falha parcial | **contrato** | frases narrativas | exec. sem narrativa | tokens vazados | exec. sem vazamento | linhas/doc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kotlin · fable baseline | 2 | 63% | 0% | 0% | 100% | 0% | 0% | n/a | **31%** | 1 | 1/2 | 9 | 0/2 | 4.1 |
| Kotlin · fable rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 11.3 |
| Kotlin · opus baseline | 2 | 50% | 0% | 0% | 50% | 0% | 0% | n/a | **25%** | 3 | 1/2 | 5 | 0/2 | 3.3 |
| Kotlin · opus rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 10.3 |
| Kotlin · sonnet baseline | 1 | 100% | 0% | 0% | 100% | 0% | 0% | n/a | **50%** | 5 | 0/1 | 12 | 0/1 | 6.0 |
| Kotlin · sonnet rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 2/2 | 0 | 2/2 | 10.0 |
| Rust · fable baseline | 2 | 100% | 25% | 50% | 100% | 0% | 0% | n/a | **61%** | 2 | 1/2 | 6 | 0/2 | 5.8 |
| Rust · fable rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 16.3 |
| Rust · opus baseline | 2 | 88% | 0% | 0% | 100% | 0% | 0% | n/a | **38%** | 3 | 0/2 | 6 | 0/2 | 3.1 |
| Rust · opus rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 12.5 |
| Rust · sonnet baseline | 1 | 100% | 0% | 50% | 100% | 0% | 0% | n/a | **56%** | 4 | 0/1 | 11 | 0/1 | 4.8 |
| Rust · sonnet rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 9.5 |
| TypeScript · fable rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 11.0 |
| TypeScript · opus rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 11.5 |
| TypeScript · sonnet rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 9.8 |
| Python · fable baseline | 2 | 88% | 0% | 0% | 100% | 0% | 0% | n/a | **47%** | 2 | 0/2 | 11 | 0/2 | 4.5 |
| Python · fable rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 15.3 |
| Python · opus baseline | 2 | 63% | 0% | 0% | 50% | 0% | 0% | n/a | **38%** | 3 | 0/2 | 8 | 0/2 | 3.8 |
| Python · opus rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 14.3 |
| Python · sonnet baseline | 1 | 75% | 0% | 0% | 100% | 0% | 0% | n/a | **44%** | 5 | 0/1 | 8 | 0/1 | 3.8 |
| Python · sonnet rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 2/2 | 0 | 2/2 | 11.5 |
| Go · fable rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 11.3 |
| Go · opus rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 12.0 |
| Go · sonnet rule | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 2/2 | 0 | 2/2 | 9.5 |
| C# · fable rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 21.8 |
| C# · opus rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 9.0 |
| C# · sonnet rule | 1 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 1/1 | 0 | 1/1 | 11.3 |

## Formato e idioma

| condição | formato idiomático | prosa |
|---|---|---|
| fable baseline | 6/6 | pt: 6 |
| fable rule | 6/6 | pt: 6 |
| opus baseline | 5/6 | pt: 5, none: 1 |
| opus rule | 6/6 | pt: 6 |
| sonnet baseline | 3/3 | pt: 3 |
| sonnet rule | 9/9 | pt: 9 |

## Falhas na condição "fable baseline"

- s2-bugfix · Python · `canUpload` (9862f2a2): falta doc, params, ret, mutation
- s2-bugfix · Python · `canAccessAfterCancel` (9862f2a2): falta params, ret, mutation
- s2-bugfix · Python · `requireUpload` (9862f2a2): falta params, mutation
- s2-bugfix · Python · `canUpload` (9862f2a2): narrativa [attribution] "# Admin não envia licença (LIC-482): o upload exige titular da guia."
- s2-bugfix · Python (9862f2a2): tokens do pedido no arquivo: LIC-482, manual-complete, titular
- s2-bugfix · Kotlin · `canUpload` (4c636bc0): falta doc, params, ret, mutation
- s2-bugfix · Kotlin · `canAccessAfterCancel` (4c636bc0): falta doc, params, ret, mutation
- s2-bugfix · Kotlin · `requireUpload` (4c636bc0): falta params, mutation
- s2-bugfix · Kotlin · `UploadNaoPermitido` (4c636bc0): falta doc
- s2-bugfix · Kotlin (4c636bc0): tokens do pedido no arquivo: LIC-482, manual-complete
- s2-bugfix · Rust · `canUpload` (9bff3784): falta params, ret, mutation
- s2-bugfix · Rust · `canAccessAfterCancel` (9bff3784): falta params, ret, mutation
- s2-bugfix · Rust · `requireUpload` (9bff3784): falta params, mutation
- s2-bugfix · Rust (9bff3784): tokens do pedido no arquivo: manual-complete, titular
- s4-bugfix-comentado · Rust · `canUpload` (544b7b9f): falta params (parcial), mutation
- s4-bugfix-comentado · Rust · `canAccessAfterCancel` (544b7b9f): falta params (parcial), mutation
- s4-bugfix-comentado · Rust · `requireUpload` (544b7b9f): falta params (parcial), mutation
- s4-bugfix-comentado · Rust · `canUpload` (544b7b9f): narrativa [deliberation] "Responder `true` para admin seria prometer um upload que falha logo adiante, deixando um objeto órfão no storage;"
- s4-bugfix-comentado · Rust · `canUpload` (544b7b9f): narrativa [deliberation] "para o admin enviar de verdade, a confirmação teria de aceitar o compositor como parâmetro, o que daria ao admin o poder de aprovar a participação de um compositor;"
- s4-bugfix-comentado · Rust (544b7b9f): tokens do pedido no arquivo: órfão, manual-complete, titular, auditado
- s4-bugfix-comentado · Kotlin · `canUpload` (e55d87d6): falta params, ret, mutation
- s4-bugfix-comentado · Kotlin · `canAccessAfterCancel` (e55d87d6): falta params, ret, mutation
- s4-bugfix-comentado · Kotlin · `requireUpload` (e55d87d6): falta params, mutation
- s4-bugfix-comentado · Kotlin · `canUpload` (e55d87d6): narrativa [deliberation] "Aceitá-lo exigiria informar em nome de qual compositor ele envia, o que lhe daria o poder de aprovar a participação de um compositor."
- s4-bugfix-comentado · Kotlin (e55d87d6): tokens do pedido no arquivo: 403, órfão, LicenseUploadService, assertUploadAllowed, manual-complete, titular, auditado
- s4-bugfix-comentado · Python · `canUpload` (8da8493b): falta params, ret, mutation
- s4-bugfix-comentado · Python · `canAccessAfterCancel` (8da8493b): falta params, ret, mutation
- s4-bugfix-comentado · Python · `requireUpload` (8da8493b): falta params, mutation
- s4-bugfix-comentado · Python · `canUpload` (8da8493b): narrativa [deliberation] "Um `True` para admin aqui seria uma promessa que termina em erro e deixa um objeto órfão no armazenamento a cada tentativa."
- s4-bugfix-comentado · Python (8da8493b): tokens do pedido no arquivo: 403, órfão, promessa, LicenseUploadService, assertUploadAllowed, manual-complete, titular, auditado

## Falhas na condição "fable rule"

Nenhuma.

## Falhas na condição "opus baseline"

- s4-bugfix-comentado · Kotlin · `canUpload` (da763984): falta params, ret, mutation
- s4-bugfix-comentado · Kotlin · `canAccessAfterCancel` (da763984): falta params, ret, mutation
- s4-bugfix-comentado · Kotlin · `requireUpload` (da763984): falta params, mutation
- s4-bugfix-comentado · Kotlin · `canUpload` (da763984): narrativa [attribution] "Só um compositor da guia pode enviar a licença (LIC-482)."
- s4-bugfix-comentado · Kotlin · `canUpload` (da763984): narrativa [deliberation] "Aceitar o admin aqui só adiava a recusa para depois do envio do objeto, deixando arquivos órfãos no storage."
- s4-bugfix-comentado · Kotlin · `canAccessAfterCancel` (da763984): narrativa [history] "o comprador perde, porque a compra deixou de valer."
- s4-bugfix-comentado · Kotlin (da763984): tokens do pedido no arquivo: LIC-482, manual-complete, titular, auditado
- s4-bugfix-comentado · Python · `canUpload` (0f5b7dc8): falta params, ret, mutation
- s4-bugfix-comentado · Python · `canAccessAfterCancel` (0f5b7dc8): falta params, ret, mutation
- s4-bugfix-comentado · Python · `requireUpload` (0f5b7dc8): falta params, mutation
- s4-bugfix-comentado · Python · `canUpload` (0f5b7dc8): narrativa [history] "Aceitar admin aqui só adiava a recusa para depois do upload, deixando um objeto órfão no armazenamento."
- s4-bugfix-comentado · Python · `canUpload` (0f5b7dc8): narrativa [deliberation] "Habilitar o envio por admin exigiria aceitar um compositor explícito na confirmação, o que daria ao admin o poder de aprovar a participação de um compositor."
- s4-bugfix-comentado · Python (0f5b7dc8): tokens do pedido no arquivo: órfão, manual-complete, titular, auditado
- s2-bugfix · Python · `canUpload` (8f2a3d86): falta doc, params, ret, mutation
- s2-bugfix · Python · `canAccessAfterCancel` (8f2a3d86): falta doc, params, ret, mutation
- s2-bugfix · Python · `requireUpload` (8f2a3d86): falta doc, params, errors, mutation
- s2-bugfix · Python · `canUpload` (8f2a3d86): narrativa [attribution] "Admin não envia licença (LIC-482): o arquivo pertence a um titular, e o caminho administrativo auditado para destravar a venda é manual-complete."
- s2-bugfix · Python (8f2a3d86): tokens do pedido no arquivo: LIC-482, manual-complete, titular, auditado
- s2-bugfix · Kotlin · `canUpload` (1080a9ff): falta doc, params, ret, mutation
- s2-bugfix · Kotlin · `canAccessAfterCancel` (1080a9ff): falta doc, params, ret, mutation
- s2-bugfix · Kotlin · `requireUpload` (1080a9ff): falta doc, params, errors, mutation
- s2-bugfix · Kotlin · `UploadNaoPermitido` (1080a9ff): falta doc
- s2-bugfix · Kotlin (1080a9ff): tokens do pedido no arquivo: LIC-482
- s4-bugfix-comentado · Rust · `canUpload` (5dbf42cb): falta params, ret, mutation
- s4-bugfix-comentado · Rust · `canAccessAfterCancel` (5dbf42cb): falta params, ret, mutation
- s4-bugfix-comentado · Rust · `requireUpload` (5dbf42cb): falta params, mutation
- s4-bugfix-comentado · Rust · `canUpload` (5dbf42cb): narrativa [deliberation] "Aceitar admin aqui só adiaria a recusa para depois de o arquivo já ter sido gravado, deixando um objeto órfão no storage."
- s4-bugfix-comentado · Rust · `canAccessAfterCancel` (5dbf42cb): narrativa [history] "porque a compra que lhe dava direito à licença deixou de existir."
- s4-bugfix-comentado · Rust (5dbf42cb): tokens do pedido no arquivo: órfão, manual-complete, titular, auditado
- s2-bugfix · Rust · `canUpload` (07d359a8): falta params, ret, mutation
- s2-bugfix · Rust · `canAccessAfterCancel` (07d359a8): falta params, ret, mutation
- s2-bugfix · Rust · `requireUpload` (07d359a8): falta params, mutation
- s2-bugfix · Rust · `UploadNaoPermitido` (07d359a8): falta doc
- s2-bugfix · Rust · `canUpload` (07d359a8): narrativa [attribution] "Admin não envia (LIC-482)"
- s2-bugfix · Rust (07d359a8): tokens do pedido no arquivo: LIC-482, manual-complete

## Falhas na condição "opus rule"

Nenhuma.

## Falhas na condição "sonnet baseline"

- s4-bugfix-comentado · Kotlin · `canUpload` (96e083f7): falta params, ret, mutation
- s4-bugfix-comentado · Kotlin · `canAccessAfterCancel` (96e083f7): falta params, ret, mutation
- s4-bugfix-comentado · Kotlin · `requireUpload` (96e083f7): falta params, mutation
- s4-bugfix-comentado · Kotlin · `canUpload` (96e083f7): narrativa [attribution] "Só compositor da guia pode enviar a licença (LIC-482)."
- s4-bugfix-comentado · Kotlin · `canUpload` (96e083f7): narrativa [emphasis] "Admin NÃO envia"
- s4-bugfix-comentado · Kotlin · `canUpload` (96e083f7): narrativa [deliberation] "habilitar o admin exigiria aceitar um `onBehalfOfUserId` explícito no confirm, o que lhe daria o poder de aprovar a participação de um compositor"
- s4-bugfix-comentado · Kotlin · `canUpload` (96e083f7): narrativa [history] "Antes, este método devolvia true para admin e o `LicenseUploadService.assertUploadAllowed` derrubava a chamada com 403, deixando um objeto órfão no S3 a cada tentativa (incidente de 14/10)."
- s4-bugfix-comentado · Kotlin · `requireUpload` (96e083f7): narrativa [emphasis] "ANTES"
- s4-bugfix-comentado · Kotlin (96e083f7): tokens do pedido no arquivo: LIC-482, 14/10, S3, 403, órfão, incidente, LicenseUploadService, assertUploadAllowed, manual-complete, onBehalfOfUserId, titular, auditado
- s4-bugfix-comentado · Rust · `canUpload` (302a8ed9): falta params, mutation
- s4-bugfix-comentado · Rust · `canAccessAfterCancel` (302a8ed9): falta params, ret, mutation
- s4-bugfix-comentado · Rust · `requireUpload` (302a8ed9): falta params, mutation
- s4-bugfix-comentado · Rust · `canUpload` (302a8ed9): narrativa [attribution] "Admin NÃO envia (LIC-482, D2):"
- s4-bugfix-comentado · Rust · `canUpload` (302a8ed9): narrativa [emphasis] "NÃO"
- s4-bugfix-comentado · Rust · `canUpload` (302a8ed9): narrativa [history] "o `LicenseUploadService.assertUploadAllowed` já rejeitava admin com 403 em `assertFileOwner`, então aceitar admin aqui só prometia um upload que falhava depois e deixava objeto órfão no S3."
- s4-bugfix-comentado · Rust · `canUpload` (302a8ed9): narrativa [deliberation] "Habilitar de verdade exigiria aceitar um `onBehalfOfUserId` explícito no confirm, dando ao admin o poder de aprovar a participação de um compositor."
- s4-bugfix-comentado · Rust (302a8ed9): tokens do pedido no arquivo: LIC-482, D2, S3, 403, órfão, assertFileOwner, LicenseUploadService, assertUploadAllowed, manual-complete, onBehalfOfUserId, auditado
- s4-bugfix-comentado · Python · `canUpload` (a30ba2f6): falta doc, params, ret, mutation
- s4-bugfix-comentado · Python · `canAccessAfterCancel` (a30ba2f6): falta params, ret, mutation
- s4-bugfix-comentado · Python · `requireUpload` (a30ba2f6): falta params, mutation
- s4-bugfix-comentado · Python · `canUpload` (a30ba2f6): narrativa [attribution] "Admin NÃO envia licença (LIC-482)."
- s4-bugfix-comentado · Python · `canUpload` (a30ba2f6): narrativa [emphasis] "Admin NÃO envia licença (LIC-482)."
- s4-bugfix-comentado · Python · `canUpload` (a30ba2f6): narrativa [history] "antes, esta checagem devolvia True e a chamada caía em 403 logo depois, deixando objeto órfão no S3."
- s4-bugfix-comentado · Python · `canUpload` (a30ba2f6): narrativa [deliberation] "Habilitar de verdade exigiria um `onBehalfOfUserId` explícito, dando ao admin poder de aprovar a participação de um compositor."
- s4-bugfix-comentado · Python · `requireUpload` (a30ba2f6): narrativa [emphasis] "Deve ser chamada ANTES de qualquer efeito colateral (ex.: gravar no S3),"
- s4-bugfix-comentado · Python (a30ba2f6): tokens do pedido no arquivo: LIC-482, S3, 403, órfão, manual-complete, onBehalfOfUserId, titular, auditado

## Falhas na condição "sonnet rule"

Nenhuma.
