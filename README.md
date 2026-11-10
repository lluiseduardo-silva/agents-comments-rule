# agents-comments-rule

Uma rule para agentes de código (Claude Code, Codex, Cursor, Copilot, Gemini CLI e
semelhantes) que troca o comentário-diário pelo comentário-contrato.

Sem instrução, o agente tende a contar no código a história da mudança: o que estava
errado, quem pediu, o que foi decidido. Com esta rule, todo tipo e função que ele
escreve ou altera documenta o que quem chama precisa saber: comportamento, o que a
chamada modifica (ou que não modifica nada), parâmetros, retorno e erros. A história vai
para o commit.

A rule é um arquivo só: [rule/comments.md](rule/comments.md).

## O problema, em um exemplo

A mesma tarefa, o mesmo modelo, a mesma linguagem. O pedido trazia o contexto de um
ticket e terminava com "Deixe o código bem comentado." (arquivos completos em
[results/](results/2026-11-09-claude-code-subagentes/)).

Sem a rule:

```kotlin
/**
 * Só compositor da guia envia licença.
 *
 * Admin fica de fora de propósito: o arquivo pertence a um titular, e o admin não é titular.
 * Aceitá-lo exigiria informar em nome de qual compositor ele envia, o que lhe daria o poder
 * de aprovar a participação de um compositor. O caminho administrativo para destravar uma
 * venda é o `manual-complete`, que é auditado.
 *
 * Esta regra não pode ser mais permissiva que a checagem de titular feita em
 * `LicenseUploadService.assertUploadAllowed`: um `true` aqui para quem não é titular
 * termina em 403 lá e deixa um objeto órfão no storage.
 */
fun canUpload(venda: Venda, userId: Long?): Boolean
```

Com a rule:

```kotlin
/**
 * Indica se [userId] pode enviar a licença de [venda]: só compositor da guia da venda
 * pode, e ser admin não concede essa permissão.
 *
 * Não modifica seus argumentos nem o estado da instância.
 *
 * @param venda Venda cuja licença seria enviada.
 * @param userId Identificador de quem tenta o envio; `null` é aceito e representa a
 * ausência de usuário: o resultado é sempre `false`.
 * @return `true` se [userId] é compositor da guia de [venda]; `false` nos demais
 * casos, inclusive quando [userId] é `null`.
 */
fun canUpload(venda: Venda, userId: Long?): Boolean
```

## Instalar

Rode na raiz do projeto.

Windows (PowerShell):

```powershell
irm https://raw.githubusercontent.com/lluiseduardo-silva/agents-comments-rule/main/install.ps1 | iex
```

Linux e macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/lluiseduardo-silva/agents-comments-rule/main/install.sh | sh
```

O padrão instala para o Claude Code, em `.claude/rules/comments.md`. Para outro harness,
passe o nome:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/lluiseduardo-silva/agents-comments-rule/main/install.ps1))) -Harness agents
```

```bash
curl -fsSL https://raw.githubusercontent.com/lluiseduardo-silva/agents-comments-rule/main/install.sh | sh -s -- --harness agents
```

| Harness | Onde a rule é gravada | Como |
|---|---|---|
| `claude` (padrão) | `.claude/rules/comments.md` | arquivo próprio |
| `agents` | `AGENTS.md` | bloco gerenciado |
| `gemini` | `GEMINI.md` | bloco gerenciado |
| `copilot` | `.github/copilot-instructions.md` | bloco gerenciado |
| `cursor` | `.cursor/rules/comments.mdc` | arquivo próprio, com `alwaysApply: true` |

"Bloco gerenciado" quer dizer que o instalador escreve a rule entre dois marcadores
dentro do arquivo e não toca no resto. Reinstalar substitui só o bloco.

| Opção (`sh` / PowerShell) | Efeito |
|---|---|
| `--target <dir>` / `-Target` | raiz do projeto, quando não é o diretório atual |
| `--dest <arquivo>` / `-Dest` | grava a rule inteira nesse arquivo, para um harness que não está na tabela |
| `--block <arquivo>` / `-Block` | grava a rule como bloco gerenciado nesse arquivo |
| `--global` / `-Global` | com `claude`: instala em `~/.claude/rules`, valendo para todos os projetos |
| `--ref <ref>` / `-Ref` | baixa de outro branch ou tag |
| `--uninstall` / `-Uninstall` | remove o arquivo ou o bloco que o instalador criou |
| `--force` / `-Force` | sobrescreve um arquivo que não parece ser desta rule |

Se preferir ler antes de executar, baixe o script, abra e rode localmente; ou clone o
repositório e rode `./install.sh` ou `.\install.ps1` de dentro dele, que aí nada é
baixado.

Os instaladores foram testados em Windows PowerShell 5.1 e em `sh` (bash e dash). O
PowerShell 7 e os shells do macOS não foram testados aqui. Só o caminho do Claude Code
passou pelo benchmark: os outros destinos seguem a convenção de cada harness, e vale
conferir na documentação dele se o arquivo é carregado em toda sessão.

## O que a rule exige

- **Todo tipo e função escrito ou alterado ganha doc**, no formato da linguagem (KDoc,
  rustdoc, TSDoc, docstring, XML do C#, prosa do Go).
- **Conteúdo, nesta ordem:** resumo do comportamento, mutação, parâmetros, retorno,
  erros e pré-condições.
- **Mutação nunca é omitida em função**, nos dois sentidos: o que a chamada modifica, ou
  "não modifica seus argumentos nem a instância". Se pode falhar no meio, diz o que fica
  alterado.
- **Fica fora do código:** história ("antes", "agora", o bug que motivou), atribuição
  (pessoa, time, ticket, PR, passo de plano), deliberação (alternativas, "decisão de
  produto") e ênfase (⚠, negrito, caixa alta).
- **Código existente:** a doc da declaração alterada é reescrita no padrão; comentários
  de declarações não tocadas são listados na resposta, não reescritos.

O texto da rule está em inglês; a prosa dos comentários segue o idioma que o código já
usa, e português do Brasil quando não há comentário nenhum. Para outro idioma padrão,
edite a seção "Form" depois de instalar.

## Evidência

72 execuções em Kotlin, Rust, TypeScript, Python, Go e C#, metade sem a rule, com três
modelos da família Claude rodando como subagentes do Claude Code. Avaliação cega por
rubrica, mais uma checagem determinística de nomes, tickets e datas plantados nos
pedidos.

| Rodada | Condição | Execuções | Contrato completo | Mutação explícita | Execuções com história do pedido no código |
|---|---|---|---|---|---|
| 1 (Sonnet) | sem a rule | 18 | 20% | 15% | 1 |
| 1 (Sonnet) | com a rule | 18 | 100% | 100% | 0 |
| 2 (Sonnet, Opus, Fable) | sem a rule | 15 | 33% a 50% | 0% | 15 |
| 2 (Sonnet, Opus, Fable) | com a rule | 21 | 100% | 100% | 0 |

Ficha completa, tabelas por linguagem e por cenário, todos os arquivos gerados e as
notas do avaliador: [results/2026-11-09-claude-code-subagentes/](results/2026-11-09-claude-code-subagentes/README.md).

O que esses números **não** provam:

- As rules foram lidas pelo agente no começo da tarefa, por instrução, e não carregadas
  pelo harness. O texto estava mais fresco do que estaria numa sessão longa.
- As tarefas são curtas e de um arquivo só.
- Há uma execução por combinação de modelo, cenário e linguagem.
- Nas duas condições havia outras duas instruções de projeto, sem relação com
  comentários, que não fazem parte deste repositório. A rule sozinha ainda não foi
  medida.
- Só uma família de modelos e um harness.

## Testar em outro harness ou modelo

O benchmark é reproduzível e foi feito para ser repetido fora do Claude Code:
[bench/README.md](bench/README.md) traz o protocolo, [bench/PROMPTS.md](bench/PROMPTS.md)
os prompts usados, e [bench/RUBRIC.md](bench/RUBRIC.md) a rubrica de avaliação. A
pergunta em aberto é de onde vem a tendência de escrever história nos comentários: do
modelo, do harness, do pedido ou do código que já existe. O protocolo lista os fatores
e como isolar cada um.

Resultados de outras execuções entram em `results/<data>-<harness>/`, no mesmo formato.

## Estrutura

```
rule/comments.md   a rule
install.ps1        instalador para PowerShell
install.sh         instalador para Linux e macOS
bench/             benchmark: cenários, sementes, scripts, protocolo, prompts, rubrica
results/           execuções publicadas, com dados brutos e relatório
```
