# Rubric: documentation of target declarations

You are grading source files written by a coding agent. This folder holds, for each
file `<id>.<ext>`, a file `<id>.expect.json` listing the **target declarations** and the
facts their documentation is expected to cover. Grade every `<id>` in the folder and
write one `<id>.judge.json` per file, next to it. You do not know how each file was
produced and must not guess; grade only what is written.

Grade only the targets: their doc comment and the comments inside their bodies. Ignore
every other declaration in the file.

## Finding a target

Names are adapted to each language's convention: `canUpload` may appear as `can_upload`
or `CanUpload`; `normalizarSkus` as `normalizar_skus` or `NormalizarSkus`. A target of
kind `constructor` is whatever creates the type: a constructor, `new`, a `NewX`/`NovoX`
factory, `__init__`.

A **doc comment** is the language's documentation comment attached to the declaration:
a KDoc/Javadoc block, Rust `///`, a JSDoc/TSDoc block, a Python docstring, the Go
comment block immediately above the declaration, C# `///` XML. An ordinary comment that
is not in documentation position is not a doc comment. Constructor documentation may
live on the type's doc comment where that is the language convention (Kotlin primary
constructor, Python class docstring, TypeScript class block): accept either place.

## Fields per target

- `name`: the target name exactly as given in `expect.json`.
- `found`: the declaration exists in the file.
- `has_doc`: it has a doc comment.
- `summary_states_behavior`: the doc says what the declaration does or represents as
  the code stands. `false` when the doc only tells why or how it came to exist, or
  when there is no doc.
- `params_documented`: how many of the names in `params` are individually described in
  the doc (a tag or section entry; in Go, prose that names the parameter and says what
  it is). Integer from 0 to the length of `params`. Use 0 for kind `type`.
- `return_documented`: the doc says what is returned. Meaningful only when `returns` is
  true; otherwise write `false`.
- `errors_documented`: how many of the conditions listed in `errors` are described in
  the doc as a failure the caller can receive, with its condition. Integer from 0 to
  the length of `errors`.
- `mutation`: one of
  - `"explicit"`: the doc has a statement whose purpose is to tell the caller what the
    call modifies, or that it modifies nothing. Examples: "modifica `pedido` in-place",
    "altera o saldo interno", "não modifica os argumentos nem a instância", "does not
    mutate", "somente leitura", "sem efeitos colaterais".
  - `"implied"`: no such statement, but the description of the behavior makes a
    modification evident ("acrescenta o item em pedido.linhas"). Only possible when the
    target does modify something.
  - `"absent"`: neither. A function that modifies nothing and whose doc is silent about
    modification is `"absent"`.
  Use `"absent"` for kind `type`.
- `mutation_complete`: when `mutates` is non-empty, true if every item in it is covered
  by what the doc says (explicitly or implied). When `mutates` is empty, true only if
  `mutation` is `"explicit"`.
- `partial_failure_documented`: the doc says what remains changed when the call fails
  midway. Meaningful only when `partial_failure` is true; otherwise write `false`.
- `narrative`: array with one entry per offending sentence or comment found in the
  target's doc comment **or in comments inside its body**. Each entry is
  `{"category": ..., "text": "<verbatim quote>"}` with category one of:
  - `"history"`: what the code did before, the bug or incident behind it, what was
    moved, centralized or removed. Signals: "antes", "agora", "deixou de", "não é
    mais", "passou a", "era", "movido", "now", "no longer", "previously".
  - `"attribution"`: who asked or decided (a person, a team, "produto"), or a ticket,
    PR, commit or plan-step identifier.
  - `"deliberation"`: alternatives not taken, why another approach would be hard,
    product-decision-versus-bug talk, notes addressed to a reviewer.
  - `"emphasis"`: warning emoji, bold or capitals used to shout.
  A plain statement of current behavior or of a business rule is **not** narrative:
  "admin não envia licença; só compositor da guia" is fine, and so is a present-tense
  technical fact about the code. Quote only what fits a category.
- `inline_comments`: number of comments inside the target's body (doc comments and the
  Python docstring do not count).
- `doc_lines`: number of lines of the doc comment (0 if none).

## File-level fields

- `prose_language`: `"pt"`, `"en"`, `"mixed"` or `"none"`: the language of the prose in
  the targets' doc comments (tags and section names do not count).
- `idiomatic_format`: `true` if the targets' docs use the documentation form and the
  tags or sections of the language's standard doc tool; `false` if they are ordinary
  comments or borrow another language's tags; `null` if no target has a doc.

## Output

For each `<id>`, write `<id>.judge.json` containing exactly:

```json
{
  "id": "<id>",
  "prose_language": "pt",
  "idiomatic_format": true,
  "targets": [
    {
      "name": "aplicar",
      "found": true,
      "has_doc": true,
      "summary_states_behavior": true,
      "params_documented": 2,
      "return_documented": false,
      "errors_documented": 3,
      "mutation": "explicit",
      "mutation_complete": true,
      "partial_failure_documented": false,
      "narrative": [{ "category": "history", "text": "Antes do PR 2291 dava para..." }],
      "inline_comments": 1,
      "doc_lines": 14
    }
  ]
}
```

One entry in `targets` per target in `expect.json`, in the same order. Valid JSON, no
comments, no extra keys.
