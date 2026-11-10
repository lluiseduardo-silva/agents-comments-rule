# Benchmark da rule de comentários

Este benchmark responde a duas perguntas:

1. **A rule funciona?** Com ela, os comentários atendem ao padrão (comportamento,
   mutação, parâmetros, retorno, erros, sem narrativa)?
2. **De onde vem a narrativa?** Sem a rule, o que faz o agente contar a história da
   mudança nos comentários: o modelo, o harness, o pedido ou o código que já existe?

A primeira já tem uma resposta parcial em [results/](../results/). A segunda está aberta
e é o motivo de este protocolo existir: ele foi escrito para ser repetido em outros
harnesses e modelos.

Requisito: Node 20 ou mais novo. Nenhuma dependência.

## Desenho

Cada execução é um **projeto de teste** descartável: um diretório com um arquivo de
código (ou nenhum), um `TASK.md` com o pedido do usuário e, na condição `rule`, a rule
no lugar onde o harness carrega instruções. A condição `baseline` é o mesmo projeto sem
a rule. O pedido nunca fala em padrão de comentário.

| Cenário | O que é | O que mede |
|---|---|---|
| `s1-greenfield` | módulo novo a partir de especificação, sem história no pedido | contrato completo, mutação, falha parcial |
| `s2-bugfix` | correção em arquivo sem comentários; o pedido traz ticket, incidente, nomes e decisão de produto | história do pedido vazando para o código |
| `s4-bugfix-comentado` | o `s2` terminando com "Deixe o código bem comentado." | o mesmo, com um pedido explícito de comentários |
| `s3-infested` | arquivo já cheio de comentários narrativos; pede-se alterar uma função e criar outra | imitação do estilo, limpeza da função alterada, o resto intacto |

Seis linguagens: Kotlin, Rust, TypeScript, Python, Go e C#. Cenários, pedidos, alvos e
tokens estão em [scenarios.mjs](scenarios.mjs); os arquivos de partida, em `seeds/`.

Há duas medidas, independentes uma da outra:

- **Avaliação cega por rubrica.** Um avaliador recebe os arquivos produzidos com um id
  aleatório, sem saber condição nem modelo, e pontua cada declaração-alvo segundo
  [RUBRIC.md](RUBRIC.md). Para cada alvo o cenário declara o que a documentação deveria
  cobrir (quais parâmetros, quais erros, o que é modificado), de modo que o avaliador
  conta itens em vez de dar nota.
- **Tokens plantados.** Os pedidos e as sementes carregam nomes de pessoas, times,
  tickets e datas inventados. O relatório procura esses tokens no arquivo final. Não
  depende de avaliador e não erra para menos: se o ticket está no arquivo, vazou.

## Passo a passo

### 1. Criar os projetos de teste

```bash
node bench/setup.mjs runs/minha-execucao --tag nome-do-modelo --harness claude
```

Imprime um diretório por projeto. O mapeamento entre diretório e condição fica em
`runs/minha-execucao/runs.json`; os nomes dos diretórios são opacos de propósito.

| Opção | Para que serve |
|---|---|
| `--harness` | onde a rule é gravada: `claude`, `agents`, `gemini`, `copilot`, `cursor` (os mesmos destinos do instalador) |
| `--rule-path <caminho>` | outro caminho dentro do projeto, para um harness que não está na lista |
| `--tag <nome>` | rótulo das execuções criadas; use o modelo, ou modelo e harness |
| `--context <pasta>` | copia o conteúdo da pasta para todos os projetos, nas duas condições; serve para medir a rule ao lado das instruções que o time já usa |
| `--conditions`, `--scenarios`, `--langs` | matriz parcial, valores separados por vírgula |
| `--append` | acrescenta a uma raiz existente; é assim que se põem vários modelos na mesma raiz |

Vários modelos na mesma raiz, para que o avaliador não saiba qual produziu cada arquivo:

```bash
node bench/setup.mjs runs/x --tag modelo-a
node bench/setup.mjs runs/x --tag modelo-b --append
```

### 2. Executar cada projeto

Uma sessão nova por projeto, no modelo indicado pela tag. Há dois modos; registre qual
foi usado, porque eles não medem a mesma coisa.

**Modo A, carga nativa (o preferido).** Abra o projeto no harness, de forma que ele
carregue as instruções do projeto do jeito dele, e envie o conteúdo de `TASK.md` como a
mensagem do usuário, sem acrescentar nada. É o que acontece no uso real. Antes de
confiar no resultado, confirme que o harness carregou a rule: numa sessão à parte, na
condição `rule`, pergunte quais instruções de projeto ele tem em contexto.

**Modo B, carga por leitura.** Um agente recebe o prompt de execução de
[PROMPTS.md](PROMPTS.md), que manda ler as instruções do projeto e depois executar
`TASK.md`. Serve quando o harness não carrega instruções de um diretório arbitrário, ou
quando a execução é feita por subagentes. Foi o modo dos resultados publicados. Ele
deixa o texto da rule mais recente no contexto do que estaria numa sessão de verdade.

Nos dois modos:

- O prompt é idêntico nas duas condições. Nada nele menciona comentários, documentação
  ou o benchmark.
- O agente trabalha só dentro do diretório do projeto.
- Não rode os projetos de uma condição todos juntos e depois os da outra: siga a ordem
  de `runs.json`, que já vem embaralhada.
- Se o agente não alterar o arquivo, registre; não repita até dar certo.

### 3. Avaliar

```bash
node bench/collect.mjs runs/minha-execucao
```

Cria `judge/b01`, `b02`, ..., cada um com até seis arquivos de id aleatório, o
`<id>.expect.json` de cada um e uma cópia da rubrica. Um avaliador por lote recebe o
prompt de avaliação de [PROMPTS.md](PROMPTS.md) e grava um `<id>.judge.json` por
arquivo. O avaliador pode ser um modelo ou uma pessoa; o formato de saída é o mesmo.

Confira o avaliador antes de acreditar nele:

- Leia você mesmo pelo menos seis arquivos, de condições e linguagens diferentes, e
  compare com o `judge.json` correspondente.
- Compare a contagem de narrativa do avaliador com os tokens vazados do relatório. Se o
  relatório acusa tokens num arquivo e o avaliador diz zero frases narrativas, o
  avaliador está frouxo.
- Se der para pagar, avalie cada lote duas vezes, com avaliadores diferentes, e veja
  onde discordam.

### 4. Gerar o relatório

```bash
node bench/report.mjs runs/minha-execucao
```

Grava `resumo.md` e `resumo.json` na raiz. "contrato" é a média, por declaração-alvo,
dos itens aplicáveis: tem doc, parâmetros, retorno, erros, mutação explícita e falha
parcial. A lista de falhas no fim do relatório cita cada alvo incompleto e cada frase
narrativa, com o id do arquivo.

### 5. Publicar

```bash
node bench/export.mjs runs/minha-execucao results/2026-01-31-meu-harness
```

```bash
node bench/report.mjs results/2026-01-31-meu-harness
```

O `export` copia os dados brutos sem os caminhos da sua máquina, e o segundo comando
recalcula o relatório a partir do que foi publicado. Acrescente um `README.md` na pasta
com a ficha abaixo.

## Ficha da execução

Sem isso não dá para comparar resultados entre harnesses.

- Data.
- Harness e versão.
- Modelo exato de cada tag, e modelo do avaliador.
- Modo de execução: A (carga nativa) ou B (carga por leitura). No modo A, como foi
  confirmado que a rule estava carregada.
- Outras instruções presentes no projeto ou no usuário (arquivos de regras globais,
  system prompt customizado, memória). Se usou `--context`, o que havia nele.
- Versão da rule: o commit deste repositório.
- Matriz: cenários, linguagens, condições, repetições por célula.
- Desvios do protocolo e execuções descartadas, com o motivo.

## De onde vem a narrativa: o que variar

Cada fator abaixo pode ser isolado com o que já existe. Mude um por vez e mantenha o
resto.

| Fator | Como isolar |
|---|---|
| Modelo | mesma raiz, uma `--tag` por modelo, mesmo harness |
| Harness (system prompt, ferramentas) | mesmo modelo em dois harnesses, modo A, condição `baseline` |
| Pedido explícito de comentários | `s2-bugfix` contra `s4-bugfix-comentado`, que só diferem na última frase |
| História no pedido | `s1-greenfield` (nenhuma) contra `s2-bugfix` (muita) |
| Estilo do código existente | `s3-infested`, olhando a função nova `remover`, que nasce cercada de narrativa |
| Instruções vizinhas | com e sem `--context` |
| Modo de carga da rule | modo A contra modo B, condição `rule` |
| Sessão longa | não coberto: os cenários são de uma tarefa só |

O que os dados de 2026-11-09 sugerem, com amostra pequena e um harness só. São
hipóteses para testar, não conclusões:

- **O conteúdo da narrativa vem do pedido.** No `s1`, que não traz história, nenhuma
  execução escreveu narrativa, em nenhuma condição. Os tokens que aparecem no código do
  `s2` e do `s4` são os do pedido.
- **O modelo pesa.** No `s2`, sem pedir comentários e sem a rule, o Sonnet não levou
  história para o código em nenhuma de 6 execuções; o Opus levou em 3 de 3 e o Fable em
  3 de 3.
- **Pedir comentários dispara em qualquer modelo.** No `s4`, sem a rule, os três modelos
  levaram história para o código em 9 de 9 execuções.
- **Não apareceu imitação de estilo.** No `s3`, sem a rule, o Sonnet manteve a narrativa
  que já estava na função alterada, mas não escreveu narrativa nova na função criada;
  em 1 de 6 execuções pôs o ticket do pedido num comentário. Só o Sonnet rodou esse
  cenário.

## Limites do desenho

- Tarefas curtas, de um arquivo. A situação em que o problema mais aparece no uso real,
  sessão longa com plano, diagnóstico e muito contexto acumulado, não é medida.
- Pedidos em português. Não se sabe se o idioma do pedido muda o resultado.
- O avaliador por rubrica mede presença e cobertura da documentação, não se ela está
  correta em relação ao código.
- Nada é compilado nem testado. O benchmark mede comentários, não o código.
- Os tokens plantados pegam a história que cita nomes, tickets e datas. Uma frase
  narrativa sem nenhum deles só é pega pelo avaliador.
