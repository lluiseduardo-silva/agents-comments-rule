# Execução de 2026-11-09: subagentes do Claude Code

72 execuções em duas rodadas: 33 sem a rule e 39 com ela. Relatórios completos:
[rodada 1](rodada-1/resumo.md) e [rodada 2](rodada-2/resumo.md).

## Ficha

| | |
|---|---|
| Data | 2026-11-09 |
| Harness | Claude Code, app desktop; cada execução foi um subagente `general-purpose` criado pela ferramenta Agent |
| Modelos | apelidos `sonnet`, `opus` e `fable` do Claude Code nessa data. A sessão que orquestrou era `claude-fable-5-2`. A versão exata para a qual `sonnet` e `opus` resolveram não foi registrada |
| Avaliador | subagentes no apelido `sonnet`, um por lote |
| Modo de execução | B, carga por leitura: o agente foi instruído a ler `.claude\rules\` e depois executar `TASK.md` ([prompt](../../bench/PROMPTS.md)) |
| Linguagens | Kotlin, Rust, TypeScript, Python, Go, C# |
| Repetições | uma execução por célula |
| Execuções descartadas | nenhuma; as 72 criaram ou alteraram o arquivo pedido |

### Outras instruções presentes

Esta execução foi feita dentro de um pacote de regras maior, do qual a rule de
comentários foi extraída. Nas **duas** condições, `.claude/rules/` tinha outros dois
arquivos, que não fazem parte deste repositório (cerca de 4,5 mil tokens no total):

- um guia de fluxo de trabalho: triagem do pedido antes de agir, respostas em português
  do Brasil, e "escopo adjacente é listado, nunca tocado";
- um guia de engenharia: concorrência, acesso a dados, tratamento de falhas.

Nenhum dos dois fala de comentários de código. A única diferença entre as condições era
a presença de `comments.md`. Três efeitos prováveis desse contexto:

- os comentários saíram em português também sem a rule;
- deixar intactos os comentários de declarações não tocadas (cenário 3) já era
  instrução do guia de fluxo, e aconteceu nas duas condições;
- vários agentes acrescentaram lock ou mutex que o pedido não pedia, por causa do guia
  de engenharia.

**A rule sozinha, num projeto sem outras instruções, não foi medida.**

### Identificadores substituídos

O cenário de correção (`s2-bugfix` e `s4-bugfix-comentado`) foi modelado num caso real.
Antes de publicar, seis identificadores e dois rótulos desse caso foram trocados por
nomes genéricos, por substituição mecânica de texto, nos pedidos, nas sementes, nos
arquivos gerados e nas notas do avaliador: `canAccessAfterCancel`,
`LicenseUploadService`, `assertUploadAllowed`, `assertFileOwner`, `onBehalfOfUserId`,
`manual-complete`, e os rótulos `D2` e `PR9`. Os modelos receberam e escreveram os nomes
originais. Fora essa troca, os arquivos em `judge/` e `saidas/` estão como foram
produzidos. Os relatórios foram recalculados depois da troca e saíram idênticos.

### Texto da rule

A rodada 2 usou o texto de [rule/comments.md](../../rule/comments.md) como está no
primeiro commit deste repositório. A rodada 1 usou a versão anterior a um ajuste de uma
frase, feito depois de ver a linha de mutação aparecer em tipos e construtores.

Rodada 1:

> A section with nothing to say is omitted (no parameters, cannot fail). Mutation is
> never omitted on a function. Private helpers need at least summary and mutation.

Rodada 2 e versão publicada:

> A section with nothing to say is omitted (no parameters, cannot fail). Mutation is
> never omitted on a function; a type declaration, and a constructor that only builds the
> new value, need no mutation line. Private helpers need at least summary and mutation.

## Rodada 1

Sonnet, cenários 1, 2 e 3, seis linguagens, duas condições: 36 execuções. Avaliação em
seis lotes, um por linguagem.

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

## Rodada 2

Três modelos, 36 execuções, avaliadas em seis lotes mistos.

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

## Conferência do avaliador

- Seis arquivos da condição com a rule foram lidos diretamente e comparados com as
  notas do avaliador (Kotlin, Go e Rust; cenários 1, 2, 3 e 4). Sem divergência.
- Varredura por palavras-sinal de narrativa ("agora", "antes", "deixou de", "decidiu",
  ticket, ênfase) nos comentários dos 39 arquivos com a rule: só falsos positivos
  ("foi negado", "identificador do produto") e a narrativa pré-existente nas declarações
  não tocadas do cenário 3.
- Na condição sem a rule, a contagem do avaliador ficou abaixo da checagem de tokens: na
  rodada 2 ele apontou zero frases narrativas em 3 das 15 execuções em que havia token
  do pedido no arquivo. Em duas, o ticket estava num comentário comum (`//`) logo acima
  da função, que a rubrica usada não cobria (ela olhava o doc comment e os comentários
  de dentro do corpo). Na terceira, uma frase sobre o caminho administrativo alternativo
  não foi classificada como deliberação. A contagem de "frases narrativas" sem a rule
  deve ser lida como piso; a de tokens é a medida firme.
- Depois desta execução, [bench/RUBRIC.md](../../bench/RUBRIC.md) passou a contar também
  o comentário comum logo acima da declaração. A rubrica exatamente como foi usada está
  copiada dentro de cada pasta de `judge/`.
- Não houve dupla avaliação.

## Observações fora da métrica

- Com a rule, implementações de trait ou interface (por exemplo `Display::fmt`, `Error()`)
  às vezes ganharam documentação completa, embora a rule dispense o override que não
  acrescenta nada ao contrato.
- Com a rule, os agentes passaram a dizer na resposta final que o contexto do ticket
  "fica para a mensagem de commit" e a listar os comentários narrativos das declarações
  que não tocaram. As respostas finais não foram arquivadas.
- A documentação com a rule tem de 10 a 15 linhas por declaração em média; sem a rule,
  de 1 a 5.

## Limites desta execução

- Modo B: a rule foi lida segundos antes da tarefa, por instrução explícita. Numa sessão
  real ela é carregada no início e pode estar a muitos turnos de distância.
- Uma execução por célula. O resultado com a rule é uniforme nas 39 execuções, mas
  nenhuma combinação de modelo, cenário e linguagem tem repetição.
- Uma família de modelos, um harness.
- O cenário 3 só rodou no Sonnet, e só na rodada 1.
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
node bench/report.mjs results/2026-11-09-claude-code-subagentes/rodada-2
```
