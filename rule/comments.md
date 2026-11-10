# Code comments

## What a comment is for

A doc comment is the **contract of a declaration, written for whoever calls or changes
it later**. That reader has the code in front of them and nothing else: not this
conversation, the plan, the ticket, the diff, or the previous version of the code.
Every sentence must be true of the code as it stands and useful to that reader.

The explanation of a change (what was wrong, what the code used to do, who asked, what
was decided or rejected) is addressed to whoever reviews the diff. It goes in the reply
to the user, the commit message, or the plan. Never in the code.

## Every type and function you write or change gets a doc comment

Use the documentation form the language's doc tool renders (what shows on IDE hover),
with its own tags or sections. Content, in this order:

1. **Summary.** One sentence: what it does or represents. A business rule the code
   enforces is behavior, so state the rule itself ("the buyer loses access once the
   sale is cancelled"), not the reasoning or the story behind it.
2. **Mutation, always, in both directions.** Say what the call changes: its arguments,
   the receiver's own state, anything external (storage, files, network, globals). When
   it changes nothing, say so explicitly ("does not modify its arguments or the
   instance"). When it can fail midway, say what is left changed.
3. **Parameters.** One entry each: meaning, plus any constraint the type does not
   express (range, unit, whether null/empty is accepted and what it means).
4. **Return.** What comes back, including the meaning of each special value (null,
   empty, false).
5. **Errors.** Every exception, error value or panic the caller can receive, each with
   the condition that produces it.
6. **Preconditions** the caller must guarantee and the signature cannot express (an
   open transaction, a held lock, a relation already loaded, call order).

Types: what the type represents, its fields or properties, and the constructor's
parameters and errors. Enum variants and error cases: one line each, saying when it
occurs.

A section with nothing to say is omitted (no parameters, cannot fail). Mutation is
never omitted on a function; a type declaration, and a constructor that only builds the
new value, need no mutation line. Private helpers need at least summary and mutation.
Test functions are exempt, and so is an override that adds nothing to the contract of
the member it overrides.

## What never goes in a comment

- **History:** what the code did before, the bug or incident behind the change, what
  was moved, centralized or removed. Words like "now", "no longer", "previously",
  "used to", "was" are the signal.
- **Attribution and tracking:** who asked or decided (a person, a team, "product"), and
  ticket, PR, commit or plan-step identifiers.
- **Deliberation:** alternatives not taken, why something else would be hard, whether
  this is a product decision or a bug fix, anything addressed to a reviewer.
- **Emphasis:** warning emoji, bold or capitals used to stress a point. State the fact
  plainly.

Test each sentence: would it still be true, and still matter, to a reader who never saw
the previous code or this task? A sentence about how the code came to be, rather than
what it does, requires or guarantees now, does not belong.

## Comments inside a function body

Default to none: the doc comment carries the contract and the code carries the how.
Write one only for a technical fact the code cannot show and a maintainer would
otherwise get wrong (an invariant, a required ordering, how an external system
behaves), stated in the present tense as a fact about the code. Never to narrate the
change, restate the next line, or credit a request.

## Existing code

- The doc comment of a declaration you modify is part of the change: bring it to this
  standard and delete the narrative it carries. Reasoning that still matters moves to
  the commit message.
- Existing comments in another style are not a template. What you write follows this
  file, not the surrounding comments.
- Comments on declarations you did not touch are adjacent scope: list them, do not
  rewrite them.

## Form

- Prose in the language the codebase's comments already use; Brazilian Portuguese when
  there are none. Tags and section names stay as the doc tool defines them.
- Follow the codebase's existing doc convention when it has one, otherwise the
  language's standard. Illustrative: KDoc/Javadoc `@param` `@return` `@throws`
  `@property` `@constructor`; rustdoc `# Arguments` `# Returns` `# Errors` `# Panics`;
  JSDoc/TSDoc `@param` `@returns` `@throws`; Python docstring `Args:` `Returns:`
  `Raises:`; C# XML `<summary>` `<param>` `<returns>` `<exception>`; Go: prose that
  starts with the declaration's name and covers the same content.

Illustrative shape (Kotlin; the same content applies in any language):

```kotlin
/**
 * Soma [valor] a cada elemento de [destino].
 *
 * Modifica [destino] in-place: cada posição é sobrescrita com o resultado. Se uma
 * exceção ocorrer no meio, os elementos anteriores já terão sido alterados. Não
 * modifica o estado da instância.
 *
 * @param destino Lista mutável cujos elementos serão atualizados.
 * @param valor Valor somado a cada elemento.
 * @throws ArithmeticException Se alguma soma estourar o intervalo de [Int].
 * @throws IllegalStateException Se alguma soma ultrapassar [limite].
 */
fun somarEmCada(destino: MutableList<Int>, valor: Int)
```
