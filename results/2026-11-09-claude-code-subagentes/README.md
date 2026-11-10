# Execução de 2026-11-09: subagentes do Claude Code

120 execuções em três rodadas: 48 sem a rule e 72 com ela. Relatórios completos:
[rodada 1](rodada-1/resumo.md), [rodada 2](rodada-2/resumo.md) e
[rodada 3](rodada-3/resumo.md).

Nas rodadas 1 e 2 a rule foi medida dentro do pacote de regras de onde ela saiu. Na
rodada 3 ela foi medida sozinha, contra um projeto sem instrução nenhuma.

## Ficha

| | |
|---|---|
| Data | 2026-11-09 |
| Harness | Claude Code, app desktop; cada execução foi um subagente `general-purpose` criado pela ferramenta Agent |
| Modelos | apelidos `sonnet`, `opus` e `fable` do Claude Code nessa data. A sessão que orquestrou era `claude-fable-5-2`. A versão exata para a qual `sonnet` e `opus` resolveram não foi registrada |
| Avaliador | subagentes no apelido `sonnet`, um por lote |
| Modo de execução | B, carga por leitura: o agente foi instruído a ler as instruções do projeto e depois executar `TASK.md` |
| Linguagens | Kotlin, Rust, TypeScript, Python, Go, C# |
| Repetições | uma execução por célula |
| Execuções descartadas | nenhuma; as 120 criaram ou alteraram o arquivo pedido |

O que mudou de uma rodada para outra:

| Rodada | Projeto sem a rule | Prompt de execução ([PROMPTS.md](../../bench/PROMPTS.md)) | Rubrica | Texto da rule |
|---|---|---|---|---|
| 1 | pacote com duas outras instruções | modo B, "como foi usado" | versão inicial | anterior a um ajuste de uma frase |
| 2 | pacote com duas outras instruções | modo B, "como foi usado" | versão inicial | final |
| 3 | vazio, nenhuma instrução | modo B, "versão para qualquer harness" | versão atual | final |

A rubrica exatamente como cada avaliador a recebeu está copiada dentro de cada pasta de
`judge/`.

### Outras instruções presentes nas rodadas 1 e 2

As rodadas 1 e 2 foram feitas dentro de um pacote de regras maior. Nas **duas**
condições, `.claude/rules/` tinha outros dois arquivos, que não fazem parte deste
repositório (cerca de 4,5 mil tokens no total):

- um guia de fluxo de trabalho: triagem do pedido antes de agir, respostas em português
  do Brasil, e "escopo adjacente é listado, nunca tocado";
- um guia de engenharia: concorrência, acesso a dados, tratamento de falhas.

Nenhum dos dois fala de comentários de código. A única diferença entre as condições era
a presença de `comments.md`. Na rodada 3 nada disso existia: a condição sem a rule não
tinha `.claude/` e a condição com a rule tinha só `.claude/rules/comments.md`.

### Identificadores substituídos

O cenário de correção (`s2-bugfix` e `s4-bugfix-comentado`) foi modelado num caso real.
Antes de publicar, seis identificadores e dois rótulos desse caso foram trocados por
nomes genéricos: `canAccessAfterCancel`, `LicenseUploadService`, `assertUploadAllowed`,
`assertFileOwner`, `onBehalfOfUserId`, `manual-complete`, e os rótulos `D2` e `PR9`.

- Nas rodadas 1 e 2 os modelos receberam e escreveram os nomes originais. A troca foi
  feita depois, por substituição mecânica de texto, nos pedidos, nas sementes, nos
  arquivos gerados e nas notas do avaliador. Fora isso, os arquivos em `judge/` e
  `saidas/` estão como foram produzidos, e os relatórios recalculados depois da troca
  saíram idênticos.
- Na rodada 3 os modelos já receberam os nomes genéricos. Nada foi alterado depois.

### Texto da rule

As rodadas 2 e 3 usaram o texto de [rule/comments.md](../../rule/comments.md) como está
no primeiro commit deste repositório. A rodada 1 usou a versão anterior a um ajuste de
uma frase, feito depois de ver a linha de mutação aparecer em tipos e construtores.

Rodada 1:

> A section with nothing to say is omitted (no parameters, cannot fail). Mutation is
> never omitted on a function. Private helpers need at least summary and mutation.

Rodadas 2 e 3, e versão publicada:

> A section with nothing to say is omitted (no parameters, cannot fail). Mutation is
> never omitted on a function; a type declaration, and a constructor that only builds the
> new value, need no mutation line. Private helpers need at least summary and mutation.

## Rodada 1: Sonnet, dentro do pacote

Cenários 1, 2 e 3, seis linguagens, duas condições: 36 execuções. Avaliação em seis
lotes, um por linguagem.

| | execuções | contrato | mutação explícita | frases narrativas | execuções sem narrativa | tokens do pedido no código |
|---|---|---|---|---|---|---|
| sem a rule | 18 | 20% | 15% | 30 | 12/18 | 1 |
| com a rule | 18 | 100% | 100% | 0 | 18/18 | 0 |

Cenário 3, tokens da narrativa que já estava no arquivo e continuam no arquivo final:

| | função alterada | função intocada | comentário da classe |
|---|---|---|---|
| sem a rule | 36/36 | 30/30 | 12/12 |
| com a rule | 0/36 | 30/30 | 12/12 |

As 30 frases narrativas sem a rule são todas do cenário 3: 29 são a narrativa que já
estava na função alterada e foi mantida, e uma é nova (o ticket do pedido num
comentário, em Rust). No cenário 2, o Sonnet sem a rule não escreveu narrativa nova; só
deixou as funções sem documentação (contrato de 7%). Por isso a rodada 2.

## Rodada 2: três modelos, dentro do pacote

36 execuções, avaliadas em seis lotes mistos.

| Modelo | Cenário | Sem a rule | Com a rule |
|---|---|---|---|
| Sonnet | `s4-bugfix-comentado` | Kotlin, Rust, Python | as seis linguagens |
| Sonnet | `s1-greenfield` | | Kotlin, Go, Python |
| Opus | `s4-bugfix-comentado` | Kotlin, Rust, Python | as seis linguagens |
| Opus | `s2-bugfix` | Kotlin, Rust, Python | |
| Fable | `s4-bugfix-comentado` | Kotlin, Rust, Python | as seis linguagens |
| Fable | `s2-bugfix` | Kotlin, Rust, Python | |

O `s2-bugfix` sem a rule nos modelos fortes mede se eles levam a história para o código
sem ninguém pedir comentários. O `s1-greenfield` no Sonnet confere se o ajuste de texto
da rule não quebrou o cenário de código novo.

| | execuções | contrato | mutação explícita | tokens do pedido no código | execuções sem vazamento |
|---|---|---|---|---|---|
| Fable sem a rule | 6 | 46% | 0% | 26 | 0/6 |
| Fable com a rule | 6 | 100% | 100% | 0 | 6/6 |
| Opus sem a rule | 6 | 33% | 0% | 19 | 0/6 |
| Opus com a rule | 6 | 100% | 100% | 0 | 6/6 |
| Sonnet sem a rule | 3 | 50% | 0% | 31 | 0/3 |
| Sonnet com a rule | 9 | 100% | 100% | 0 | 9/9 |

Sem a rule, as 15 execuções levaram para os comentários algum token do pedido: o
ticket, o incidente, o "objeto órfão", o caminho administrativo que não foi tomado.

## Rodada 3: a rule sozinha

48 execuções, avaliadas em oito lotes mistos. A condição sem a rule é um projeto sem
nenhuma instrução; a condição com a rule tem só `.claude/rules/comments.md`.

| Cenário | Sem a rule, por modelo | Com a rule, por modelo |
|---|---|---|
| `s4-bugfix-comentado` | Kotlin, Rust, Python | as seis linguagens |
| `s3-infested` | Kotlin, Go | Kotlin, Go, TypeScript |
| `s1-greenfield` | | Python, C# |

| | execuções | contrato | mutação explícita | frases narrativas | execuções sem narrativa |
|---|---|---|---|---|---|
| Fable sem a rule | 5 | 56% | 8% | 17 | 0/5 |
| Fable com a rule | 11 | 100% | 100% | 0 | 11/11 |
| Opus sem a rule | 5 | 45% | 8% | 13 | 1/5 |
| Opus com a rule | 11 | 100% | 100% | 0 | 11/11 |
| Sonnet sem a rule | 5 | 41% | 0% | 18 | 0/5 |
| Sonnet com a rule | 11 | 100% | 100% | 0 | 11/11 |

Cenário 4, tokens do pedido no código:

| | execuções | tokens | execuções sem vazamento |
|---|---|---|---|
| Fable sem a rule | 3 | 15 | 0/3 |
| Opus sem a rule | 3 | 14 | 0/3 |
| Sonnet sem a rule | 3 | 33 | 0/3 |
| os três com a rule | 18 | 0 | 18/18 |

Cenário 3, tokens da narrativa que já estava no arquivo e continuam no arquivo final
(o resultado foi o mesmo nos três modelos):

| | função alterada | função intocada | comentário da classe |
|---|---|---|---|
| sem a rule, cada modelo | 12/12 | 10/10 | 4/4 |
| com a rule, cada modelo | 0/18 | 15/15 | 6/6 |

O que a rodada 3 acrescenta:

- **A narrativa não vinha do pacote.** Num projeto sem instrução nenhuma, as 9
  execuções do cenário 4 levaram a história do pedido para os comentários.
- **A rule sozinha basta.** 33 execuções e 126 declarações sem nenhuma falha de contrato
  nem narrativa, nos três modelos.
- **O que é levado para o código depende do modelo.** Sem a rule, Opus e Fable deixaram
  de fora o ticket, a data e os nomes de pessoas, mas escreveram o motivo e o caminho
  alternativo ("objeto órfão", `manual-complete`, "auditado"). O Sonnet escreveu o ticket
  nas 3 execuções e, numa delas, também o passo do plano e a data do incidente.
- **Deixar intacto o que não foi tocado não dependia do pacote.** Com a rule sozinha,
  os comentários das declarações não tocadas ficaram inteiros nos três modelos.
- **Não apareceu imitação de estilo em nenhum modelo.** No cenário 3 sem a rule, a
  função nova `remover` nasceu sem narrativa nas 6 execuções: com uma doc de 1 a 4
  linhas em Opus e Fable, e sem doc no Sonnet. A narrativa que já estava em `aplicar`
  foi mantida.
- **O idioma se manteve.** Sem a instrução de responder em português, que vinha do
  pacote, os comentários continuaram em português nas duas condições.

## Conferência do avaliador

- Nove arquivos foram lidos diretamente e comparados com as notas do avaliador: seis nas
  rodadas 1 e 2 (com a rule; Kotlin, Go e Rust; cenários 1, 2, 3 e 4) e três na rodada 3
  (Fable com a rule no cenário 3, Opus com a rule no cenário 4, Sonnet sem a rule no
  cenário 4). Sem divergência.
- Varredura por palavras-sinal de narrativa ("agora", "antes", "deixou de", "decidiu",
  ticket, ênfase) nos comentários dos 72 arquivos com a rule: só falsos positivos
  ("foi negado", "identificador do produto") e a narrativa pré-existente nas declarações
  não tocadas do cenário 3.
- Sem a rule, a contagem do avaliador ficou abaixo da checagem de tokens. Na rodada 2
  ele apontou zero frases narrativas em 3 das 15 execuções em que havia token do pedido
  no arquivo: em duas, o ticket estava num comentário comum (`//`) logo acima da função,
  que a rubrica inicial não cobria; na terceira, uma frase sobre o caminho administrativo
  alternativo não foi classificada como deliberação. Na rodada 3, já com a rubrica
  corrigida, isso aconteceu em 1 das 9: um bloco de comentários `#` em Python que o
  avaliador não contou. A contagem de "frases narrativas" sem a rule deve ser lida como
  piso; a de tokens é a medida firme.
- Não houve dupla avaliação.

## Observações fora da métrica

- Com a rule, implementações de trait ou interface (por exemplo `Display::fmt`, `Error()`)
  às vezes ganharam documentação completa, embora a rule dispense o override que não
  acrescenta nada ao contrato.
- Com a rule, os agentes passaram a dizer na resposta final que o contexto do ticket
  "fica para a mensagem de commit" e a listar os comentários narrativos das declarações
  que não tocaram. As respostas finais não foram arquivadas.
- Nas rodadas 1 e 2, vários agentes acrescentaram lock ou mutex que o pedido não pedia,
  por causa do guia de engenharia do pacote.
- A documentação com a rule tem de 10 a 15 linhas por declaração em média; sem a rule,
  de 1 a 5.

## Limites desta execução

- Modo B: a rule foi lida segundos antes da tarefa, por instrução explícita. Numa sessão
  real ela é carregada no início e pode estar a muitos turnos de distância.
- Uma execução por célula. O resultado com a rule é uniforme nas 72 execuções, mas
  nenhuma combinação de modelo, cenário e linguagem tem repetição.
- Uma família de modelos, um harness.
- Tarefas curtas, de um arquivo só.
- Nada foi compilado.

## Conteúdo das pastas

```
rodada-N/
  resumo.md        relatório gerado por bench/report.mjs
  resumo.json      os mesmos dados, por execução e por declaração-alvo
  judge-map.json   id -> modelo, condição, cenário, linguagem
  judge/           arquivos como o avaliador os viu (id aleatório), a expectativa de
                   cada um (<id>.expect.json) e as notas (<id>.judge.json)
  saidas/          os mesmos arquivos, por modelo/condição/cenário/linguagem
```

Para recalcular um relatório a partir dos dados publicados:

```bash
node bench/report.mjs results/2026-11-09-claude-code-subagentes/rodada-3
```
