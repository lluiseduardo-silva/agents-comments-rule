# Benchmark da rule de comentários

36 execuções avaliadas.

"baseline" é o projeto sem a rule; "rule" é o mesmo projeto com ela. As colunas de contrato vêm da avaliação cega (`bench/RUBRIC.md`); "tokens vazados" é a checagem determinística dos nomes, tickets e datas plantados no pedido. "contrato" é a média, por declaração-alvo, dos itens aplicáveis: doc, parâmetros, retorno, erros, mutação explícita e falha parcial.

## Geral

| | execuções | doc | parâmetros | retorno | erros | mutação explícita | mutação completa | falha parcial | **contrato** | frases narrativas | exec. sem narrativa | tokens vazados | exec. sem vazamento | linhas/doc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sonnet baseline | 18 | 36% | 6% | 30% | 8% | 15% | 26% | 83% | **20%** | 30 | 12/18 | 1 | 17/18 | 0.9 |
| sonnet rule | 18 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 18/18 | 0 | 18/18 | 10.5 |

## Por cenário

| | execuções | doc | parâmetros | retorno | erros | mutação explícita | mutação completa | falha parcial | **contrato** | frases narrativas | exec. sem narrativa | tokens vazados | exec. sem vazamento | linhas/doc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| s1-greenfield · sonnet baseline | 6 | 39% | 10% | 50% | 8% | 21% | 46% | 83% | **25%** | 0 | 6/6 | 0 | 6/6 | 0.8 |
| s1-greenfield · sonnet rule | 6 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 6/6 | 0 | 6/6 | 10.1 |
| s2-bugfix · sonnet baseline | 6 | 13% | 0% | 0% | 17% | 0% | 0% | n/a | **7%** | 0 | 6/6 | 0 | 6/6 | 0.2 |
| s2-bugfix · sonnet rule | 6 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 6/6 | 0 | 6/6 | 9.6 |
| s3-infested · sonnet baseline | 6 | 75% | 4% | 50% | 0% | 25% | 25% | n/a | **32%** | 30 | 0/6 | 1 | 5/6 | 2.8 |
| s3-infested · sonnet rule | 6 | 100% | 100% | 100% | 100% | 100% | 100% | n/a | **100%** | 0 | 6/6 | 0 | 6/6 | 13.4 |

## Por linguagem

| | execuções | doc | parâmetros | retorno | erros | mutação explícita | mutação completa | falha parcial | **contrato** | frases narrativas | exec. sem narrativa | tokens vazados | exec. sem vazamento | linhas/doc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kotlin · sonnet baseline | 3 | 25% | 0% | 20% | 0% | 11% | 22% | 100% | **12%** | 5 | 2/3 | 0 | 3/3 | 0.8 |
| Kotlin · sonnet rule | 3 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 3/3 | 0 | 3/3 | 10.7 |
| Rust · sonnet baseline | 3 | 33% | 0% | 40% | 0% | 22% | 33% | 100% | **18%** | 6 | 2/3 | 1 | 2/3 | 0.7 |
| Rust · sonnet rule | 3 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 3/3 | 0 | 3/3 | 11.1 |
| TypeScript · sonnet baseline | 3 | 25% | 0% | 20% | 0% | 11% | 22% | 100% | **12%** | 4 | 2/3 | 0 | 3/3 | 0.8 |
| TypeScript · sonnet rule | 3 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 3/3 | 0 | 3/3 | 9.9 |
| Python · sonnet baseline | 3 | 25% | 0% | 20% | 0% | 11% | 22% | 100% | **12%** | 4 | 2/3 | 0 | 3/3 | 0.8 |
| Python · sonnet rule | 3 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 3/3 | 0 | 3/3 | 12.8 |
| Go · sonnet baseline | 3 | 92% | 35% | 60% | 50% | 22% | 44% | 100% | **61%** | 6 | 2/3 | 0 | 3/3 | 1.7 |
| Go · sonnet rule | 3 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 3/3 | 0 | 3/3 | 8.8 |
| C# · sonnet baseline | 3 | 17% | 0% | 20% | 0% | 11% | 11% | 0% | **8%** | 5 | 2/3 | 0 | 3/3 | 0.8 |
| C# · sonnet rule | 3 | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** | 0 | 3/3 | 0 | 3/3 | 9.7 |

## Cenário 3: o que aconteceu com a narrativa que já estava no arquivo

Tokens restantes no arquivo final, somados nas execuções (restantes/possíveis). "alterada" deveria ir a zero; "intocada" deveria ficar inteira.

| condição | função alterada (`aplicar`) | função intocada (`totalDeCupons`) | comentário da classe | vindos do pedido |
|---|---|---|---|---|
| sonnet baseline | 36/36 | 30/30 | 12/12 | 1/18 |
| sonnet rule | 0/36 | 30/30 | 12/12 | 0/18 |

## Formato e idioma

| condição | formato idiomático | prosa |
|---|---|---|
| sonnet baseline | 12/18 | pt: 12, none: 6 |
| sonnet rule | 18/18 | pt: 18 |

## Falhas na condição "sonnet baseline"

- s3-infested · Kotlin · `aplicar` (99974351): falta params, errors, mutation
- s3-infested · Kotlin · `remover` (99974351): falta doc, params, ret, mutation
- s3-infested · Kotlin · `aplicar` (99974351): narrativa [emphasis] "⚠ **NÃO remover o limite.**"
- s3-infested · Kotlin · `aplicar` (99974351): narrativa [history] "Antes do PR 2291 dava para empilhar cupom à vontade e o Financeiro reclamou do prejuízo em novembro."
- s3-infested · Kotlin · `aplicar` (99974351): narrativa [attribution] "A Carla decidiu travar pelo `maxCuponsPorPedido` em vez de validar no front, que era a outra opção discutida."
- s3-infested · Kotlin · `aplicar` (99974351): narrativa [deliberation] "em vez de validar no front, que era a outra opção discutida"
- s3-infested · Kotlin · `aplicar` (99974351): narrativa [attribution] "Limite pedido pelo Financeiro"
- s1-greenfield · Kotlin · `Estoque` (85012b59): falta doc
- s1-greenfield · Kotlin · `construtor de Estoque` (85012b59): falta doc, params, errors
- s1-greenfield · Kotlin · `repor` (85012b59): falta doc, params, errors, mutation
- s1-greenfield · Kotlin · `quantidade` (85012b59): falta doc, params, ret, mutation
- s1-greenfield · Kotlin · `reservar` (85012b59): falta params, errors, mutation
- s1-greenfield · Kotlin · `normalizarSkus` (85012b59): falta params
- s3-infested · Go · `aplicar` (5deaa301): falta params, errors, mutation
- s3-infested · Go · `remover` (5deaa301): falta params (parcial)
- s3-infested · Go · `aplicar` (5deaa301): narrativa [emphasis] "⚠ **NÃO remover o limite.**"
- s3-infested · Go · `aplicar` (5deaa301): narrativa [history] "Antes do PR 2291 dava para empilhar cupom à vontade"
- s3-infested · Go · `aplicar` (5deaa301): narrativa [attribution] "o Financeiro reclamou do prejuízo em novembro"
- s3-infested · Go · `aplicar` (5deaa301): narrativa [attribution] "A Carla decidiu travar pelo maxCuponsPorPedido"
- s3-infested · Go · `aplicar` (5deaa301): narrativa [deliberation] "em vez de validar no front, que era a outra opção discutida"
- s3-infested · Go · `aplicar` (5deaa301): narrativa [attribution] "Limite pedido pelo Financeiro"
- s2-bugfix · Kotlin · `canUpload` (a171941b): falta doc, params, ret, mutation
- s2-bugfix · Kotlin · `canAccessAfterCancel` (a171941b): falta doc, params, ret, mutation
- s2-bugfix · Kotlin · `requireUpload` (a171941b): falta doc, params, errors, mutation
- s2-bugfix · Kotlin · `UploadNaoPermitido` (a171941b): falta doc
- s3-infested · Rust · `aplicar` (391f37a5): falta params, errors, mutation
- s3-infested · Rust · `remover` (391f37a5): falta params
- s3-infested · Rust · `aplicar` (391f37a5): narrativa [emphasis] "⚠ **NÃO remover o limite.**"
- s3-infested · Rust · `aplicar` (391f37a5): narrativa [history] "Antes do PR 2291 dava para empilhar cupom à vontade e o Financeiro reclamou do prejuízo em novembro."
- s3-infested · Rust · `aplicar` (391f37a5): narrativa [attribution] "A Carla decidiu travar pelo `max_cupons_por_pedido`"
- s3-infested · Rust · `aplicar` (391f37a5): narrativa [deliberation] "em vez de validar no front, que era a outra opção discutida."
- s3-infested · Rust · `aplicar` (391f37a5): narrativa [attribution] "Limite pedido pelo Financeiro"
- s3-infested · Rust · `aplicar` (391f37a5): narrativa [attribution] "PAG-1342: o total nunca fica abaixo de zero"
- s3-infested · Rust (391f37a5): tokens do pedido no arquivo: PAG-1342
- s3-infested · Python · `aplicar` (d6e94bda): falta params, errors, mutation
- s3-infested · Python · `remover` (d6e94bda): falta doc, params, ret, mutation
- s3-infested · Python · `aplicar` (d6e94bda): narrativa [emphasis] "⚠ **NÃO remover o limite.**"
- s3-infested · Python · `aplicar` (d6e94bda): narrativa [history] "Antes do PR 2291 dava para empilhar cupom à vontade e o Financeiro reclamou do prejuízo em novembro."
- s3-infested · Python · `aplicar` (d6e94bda): narrativa [attribution] "A Carla decidiu travar pelo `max_cupons_por_pedido` em vez de validar no front, que era a outra opção discutida."
- s3-infested · Python · `aplicar` (d6e94bda): narrativa [attribution] "# Limite pedido pelo Financeiro"
- s1-greenfield · Rust · `Estoque` (5d2b1262): falta doc
- s1-greenfield · Rust · `construtor de Estoque` (5d2b1262): falta doc, params, errors
- s1-greenfield · Rust · `repor` (5d2b1262): falta doc, params, errors, mutation
- s1-greenfield · Rust · `quantidade` (5d2b1262): falta doc, params, ret, mutation
- s1-greenfield · Rust · `reservar` (5d2b1262): falta params, errors, mutation
- s1-greenfield · Rust · `normalizarSkus` (5d2b1262): falta params
- s1-greenfield · TypeScript · `Estoque` (774db09e): falta doc
- s1-greenfield · TypeScript · `construtor de Estoque` (774db09e): falta doc, params, errors
- s1-greenfield · TypeScript · `repor` (774db09e): falta doc, params, errors, mutation
- s1-greenfield · TypeScript · `quantidade` (774db09e): falta doc, params, ret, mutation
- s1-greenfield · TypeScript · `reservar` (774db09e): falta params, errors, mutation
- s1-greenfield · TypeScript · `normalizarSkus` (774db09e): falta params
- s1-greenfield · Python · `Estoque` (b02d340f): falta doc
- s1-greenfield · Python · `construtor de Estoque` (b02d340f): falta doc, params, errors
- s1-greenfield · Python · `repor` (b02d340f): falta doc, params, errors, mutation
- s1-greenfield · Python · `quantidade` (b02d340f): falta doc, params, ret, mutation
- s1-greenfield · Python · `reservar` (b02d340f): falta params, errors, mutation
- s1-greenfield · Python · `normalizarSkus` (b02d340f): falta params
- s2-bugfix · C# · `canUpload` (a3687b81): falta doc, params, ret, mutation
- s2-bugfix · C# · `canAccessAfterCancel` (a3687b81): falta doc, params, ret, mutation
- s2-bugfix · C# · `requireUpload` (a3687b81): falta doc, params, errors, mutation
- s2-bugfix · C# · `UploadNaoPermitido` (a3687b81): falta doc
- s2-bugfix · Go · `canUpload` (b57a5629): falta doc, params, ret, mutation
- s2-bugfix · Go · `canAccessAfterCancel` (b57a5629): falta params, ret, mutation
- s2-bugfix · Go · `requireUpload` (b57a5629): falta params, mutation
- s1-greenfield · C# · `Estoque` (d3fe4f9a): falta doc
- s1-greenfield · C# · `construtor de Estoque` (d3fe4f9a): falta doc, params, errors
- s1-greenfield · C# · `repor` (d3fe4f9a): falta doc, params, errors, mutation
- s1-greenfield · C# · `quantidade` (d3fe4f9a): falta doc, params, ret, mutation
- s1-greenfield · C# · `reservar` (d3fe4f9a): falta doc, params, errors, mutation, partial
- s1-greenfield · C# · `normalizarSkus` (d3fe4f9a): falta doc, params, ret, mutation
- s1-greenfield · Go · `construtor de Estoque` (4e29ac77): falta params
- s1-greenfield · Go · `repor` (4e29ac77): falta errors (parcial), mutation
- s1-greenfield · Go · `quantidade` (4e29ac77): falta mutation
- s1-greenfield · Go · `reservar` (4e29ac77): falta errors, mutation
- s1-greenfield · Go · `normalizarSkus` (4e29ac77): falta params
- s2-bugfix · Python · `canUpload` (8ce00a95): falta doc, params, ret, mutation
- s2-bugfix · Python · `canAccessAfterCancel` (8ce00a95): falta doc, params, ret, mutation
- s2-bugfix · Python · `requireUpload` (8ce00a95): falta doc, params, errors, mutation
- s2-bugfix · Python · `UploadNaoPermitido` (8ce00a95): falta doc
- s2-bugfix · Rust · `canUpload` (3ce02d37): falta doc, params, ret, mutation
- s2-bugfix · Rust · `canAccessAfterCancel` (3ce02d37): falta doc, params, ret, mutation
- s2-bugfix · Rust · `requireUpload` (3ce02d37): falta doc, params, errors, mutation
- s2-bugfix · Rust · `UploadNaoPermitido` (3ce02d37): falta doc
- s2-bugfix · TypeScript · `canUpload` (3982d655): falta doc, params, ret, mutation
- s2-bugfix · TypeScript · `canAccessAfterCancel` (3982d655): falta doc, params, ret, mutation
- s2-bugfix · TypeScript · `requireUpload` (3982d655): falta doc, params, errors, mutation
- s2-bugfix · TypeScript · `UploadNaoPermitido` (3982d655): falta doc
- s3-infested · C# · `aplicar` (714e49f4): falta params, errors, mutation
- s3-infested · C# · `remover` (714e49f4): falta params
- s3-infested · C# · `aplicar` (714e49f4): narrativa [emphasis] "⚠ **NÃO remover o limite.**"
- s3-infested · C# · `aplicar` (714e49f4): narrativa [history] "Antes do PR 2291 dava para empilhar cupom à vontade e o Financeiro reclamou do prejuízo em novembro."
- s3-infested · C# · `aplicar` (714e49f4): narrativa [attribution] "A Carla decidiu travar pelo <c>_maxCuponsPorPedido</c>"
- s3-infested · C# · `aplicar` (714e49f4): narrativa [deliberation] "em vez de validar no front, que era a outra opção discutida."
- s3-infested · C# · `aplicar` (714e49f4): narrativa [attribution] "// Limite pedido pelo Financeiro"
- s3-infested · TypeScript · `aplicar` (9bab0fd6): falta params, errors, mutation
- s3-infested · TypeScript · `remover` (9bab0fd6): falta doc, params, ret, mutation
- s3-infested · TypeScript · `aplicar` (9bab0fd6): narrativa [emphasis] "⚠ **NÃO remover o limite.**"
- s3-infested · TypeScript · `aplicar` (9bab0fd6): narrativa [history] "Antes do PR 2291 dava para empilhar cupom à vontade e o Financeiro reclamou do prejuízo em novembro."
- s3-infested · TypeScript · `aplicar` (9bab0fd6): narrativa [attribution] "A Carla decidiu travar pelo `maxCuponsPorPedido` em vez de validar no front, que era a outra opção discutida."
- s3-infested · TypeScript · `aplicar` (9bab0fd6): narrativa [attribution] "// Limite pedido pelo Financeiro"

## Falhas na condição "sonnet rule"

Nenhuma.
