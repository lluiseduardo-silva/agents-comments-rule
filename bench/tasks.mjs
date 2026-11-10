#!/usr/bin/env node
// Imprime o pedido (o conteúdo de TASK.md) de um cenário numa linguagem.
//
//   node bench/tasks.mjs                      lista cenários e linguagens
//   node bench/tasks.mjs s2-bugfix kotlin     imprime o pedido

import { LANGS, SCENARIOS } from './scenarios.mjs';

const [scenario, lang] = process.argv.slice(2);
if (!SCENARIOS[scenario] || !LANGS[lang]) {
  console.log(`cenários:   ${Object.keys(SCENARIOS).join(', ')}`);
  console.log(`linguagens: ${Object.keys(LANGS).join(', ')}`);
  process.exit(scenario ? 2 : 0);
}
console.log(SCENARIOS[scenario].task(lang, SCENARIOS[scenario].files[lang]));
