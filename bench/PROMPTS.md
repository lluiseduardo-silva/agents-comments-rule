# Prompts

Tudo o que foi dito aos agentes na execução publicada em
[results/2026-11-09-claude-code-subagentes/](../results/2026-11-09-claude-code-subagentes/README.md),
palavra por palavra, mais as versões generalizadas para outros harnesses.

## Pedido do usuário (`TASK.md`)

É gerado por [scenarios.mjs](scenarios.mjs), um por cenário e linguagem. Para ver
qualquer um:

```bash
node bench/tasks.mjs s2-bugfix kotlin
```

Abaixo, as versões em Kotlin. Nas outras linguagens só mudam o nome do arquivo, o nome
da linguagem e, no cenário 3, o nome do erro.

A primeira frase ("Mudança direta, já aprovada: faça agora, sem plano.") existe porque
a execução publicada tinha no projeto uma instrução de triagem que mandava planejar
antes de mexer em autorização ou dinheiro. Ela ficou no pedido para que as execuções
sejam comparáveis.

### `s1-greenfield`

```text
Mudança direta, já aprovada: faça agora, sem plano.

Crie o arquivo `Estoque.kt` em Kotlin com um controle de estoque em memória. Só a biblioteca padrão. Não crie testes nem outros arquivos.

- Tipo `Estoque`, criado com `limitePorSku` (inteiro; menor ou igual a zero é erro).
- `repor(sku, quantidade)`: soma a quantidade ao saldo do sku. Quantidade menor ou igual a zero é erro. Saldo resultante acima de `limitePorSku` é erro, e nesse caso o saldo não muda.
- `quantidade(sku)`: devolve o saldo atual do sku; zero se o sku não existir.
- `reservar(itens, pedido)`: `itens` é uma lista de {sku, quantidade}; `pedido` é um objeto mutável com uma lista `linhas`. Para cada item, na ordem: debita a quantidade do saldo e acrescenta o item em `pedido.linhas`. Quantidade menor ou igual a zero é erro de quantidade inválida. Saldo insuficiente é erro de estoque insuficiente. No primeiro erro a operação para; os itens anteriores continuam debitados e continuam em `pedido.linhas`.
- `normalizarSkus(skus)`: recebe uma lista mutável de textos e a altera no lugar: tira espaços das pontas, converte para maiúsculas e remove os que ficarem vazios. Devolve quantos foram removidos.

Use os nomes acima, adaptados à convenção de nomes da linguagem.
```

### `s2-bugfix`

```text
Mudança direta, já aprovada: faça agora, sem plano. Edite `LicencaAccessValidator.kt`. Não crie testes nem outros arquivos.

Contexto (ticket LIC-482, passo D2 do plano PR9): hoje `canUpload` devolve true para admin, mas logo em seguida o `LicenseUploadService.assertUploadAllowed` derruba a chamada com 403 em `assertFileOwner`, porque o arquivo pertence a um titular e o admin não é titular. Nunca existiu upload por admin funcionando: era só uma promessa que terminava em erro e, a cada tentativa, deixava um objeto órfão no S3. Foi isso que causou o incidente de 14/10 que a Marina, do time de Risco, reportou. Na reunião de quinta o time de Produto decidiu que admin não envia licença; habilitar de verdade exigiria aceitar um `onBehalfOfUserId` explícito no confirm, o que daria ao admin o poder de aprovar a participação de um compositor. O caminho administrativo para destravar uma venda já existe e é auditado: `manual-complete`.

O que fazer:
1. `canUpload`: admin deixa de ser aceito. Só compositor da guia pode enviar.
2. Nova função `canAccessAfterCancel(venda, userId)`: para venda cancelada, admin e compositor da guia mantêm o acesso; o comprador perde.
3. Nova função `requireUpload(venda, userId)`: não devolve nada; falha com o erro `UploadNaoPermitido` (crie o tipo) quando `canUpload` for falso.

Use os nomes acima, adaptados à convenção de nomes da linguagem.
```

Seis identificadores e dois rótulos deste pedido são nomes genéricos postos na
publicação; a execução de 2026-11-09 usou outros nas mesmas posições (detalhe na
[ficha](../results/2026-11-09-claude-code-subagentes/README.md)). Quem repetir o
benchmark usa o pedido como está aqui.

### `s4-bugfix-comentado`

O pedido do `s2-bugfix`, seguido de uma linha em branco e desta frase:

```text
Deixe o código bem comentado.
```

### `s3-infested`

```text
Mudança direta, já aprovada: faça agora, sem plano. Edite `CupomService.kt`. Não crie testes nem outros arquivos.

O suporte abriu o PAG-1342: um cliente aplicou cupom vencido e o total do pedido ficou negativo. A Renata, do time de Checkout, pediu duas mudanças:
1. `aplicar`: cupom expirado passa a falhar com `CupomInvalidoException`; o mesmo cupom não pode ser aplicado duas vezes no mesmo pedido (mesmo erro); o total nunca fica abaixo de zero (trava em zero).
2. Nova função `remover(pedido, codigo)`: tira o código de `cuponsAplicados` e devolve se ele estava lá. Não mexe no total.

Use os nomes acima, adaptados à convenção de nomes da linguagem.
```

## Prompt de execução

### Modo A, carga nativa

Não há prompt além do pedido: o conteúdo de `TASK.md` é a mensagem do usuário, numa
sessão nova aberta no diretório do projeto.

### Modo B, carga por leitura, como foi usado nas rodadas 1 e 2

Um subagente por projeto, com este texto e o caminho do projeto no lugar de `<dir>`:

```text
Você está trabalhando no projeto que fica em `<dir>`.

1. Leia todos os arquivos de `.claude\rules\` dentro desse diretório. São as instruções deste projeto, do mesmo tipo que o Claude Code carrega no início de uma sessão: valem para todo o trabalho e devem ser seguidas exatamente como estão escritas.
2. Leia `TASK.md` nesse diretório e execute o que ele pede. É o pedido do usuário.

Trabalhe só dentro desse diretório e não leia nada fora dele. Não há toolchain instalada: não tente compilar nem rodar nada. Resposta final em até 5 linhas.
```

Nessas rodadas, `.claude\rules\` existia nas duas condições, porque havia outras
instruções de projeto além da rule.

### Modo B, versão para qualquer harness (usada na rodada 3)

Com os projetos criados por `setup.mjs` deste repositório, a condição `baseline` não tem
nenhum arquivo de instruções. Para o prompt continuar idêntico nas duas condições, o
passo 1 vira condicional. Troque `<instruções>` pelo caminho que o `setup.mjs` informou
(por exemplo `.claude/rules/`, `AGENTS.md`, `.cursor/rules/`). Na rodada 3 o caminho foi
`.claude/rules/`:

```text
Você está trabalhando no projeto que fica em `<dir>`.

1. Se existir `<instruções>` nesse diretório, leia tudo o que houver ali. São as instruções deste projeto, do mesmo tipo que o harness carrega no início de uma sessão: valem para todo o trabalho e devem ser seguidas exatamente como estão escritas.
2. Leia `TASK.md` nesse diretório e execute o que ele pede. É o pedido do usuário.

Trabalhe só dentro desse diretório e não leia nada fora dele. Não há toolchain instalada: não tente compilar nem rodar nada. Resposta final em até 5 linhas.
```

## Prompt de avaliação

Um avaliador por lote, com o caminho do lote no lugar de `<lote>`. A rubrica que ele
segue é [RUBRIC.md](RUBRIC.md), copiada para dentro de cada lote.

### Rodadas 2 e 3 (lotes mistos; a versão a usar)

```text
You are grading documentation comments in source files. Work only inside this folder and read nothing outside it:

`<lote>`

1. Read `RUBRIC.md` in that folder and follow it exactly.
2. The folder has 6 files named `<id>.expect.json`. For each one, read it and the matching source file `<id>.<ext>` (the `file` field of the expect file names it; languages are mixed), then write `<id>.judge.json` in the same folder, in the format the rubric defines.

Grade each file on its own, strictly by what is written in it. Be literal about the rubric's definitions (for example, `mutation` is "explicit" only when the doc has a statement about what is or is not modified). Check every sentence of each target's doc comment and every comment inside its body against the four narrative categories, and quote each offending one verbatim. Final reply: one line saying how many judge files you wrote.
```

### Rodada 1 (um lote por linguagem)

Igual, com duas diferenças: o passo 2 citava a extensão da linguagem do lote
(`<id>.kt`, `<id>.rs`, ...) em vez de `<id>.<ext>`, e o último parágrafo era mais curto:

```text
Grade each file on its own, strictly by what is written in it. Be literal about the rubric's definitions (for example, `mutation` is "explicit" only when the doc has a statement about what is or is not modified). Quote narrative verbatim. Final reply: one line saying how many judge files you wrote.
```

## O que os agentes não receberam

- Nenhuma menção a comentários, documentação, rule ou benchmark no prompt de execução.
- Nenhuma informação sobre condição ou modelo no prompt de avaliação, nos nomes de
  arquivo ou nos caminhos.
- Nenhum exemplo de saída esperada além do que está na própria rule.
