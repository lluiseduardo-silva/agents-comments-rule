#!/usr/bin/env node
// Cria um projeto de teste por célula (condição × cenário × linguagem).
//
//   node bench/setup.mjs <raiz> [--tag nome] [--harness claude|agents|gemini|copilot|cursor]
//                               [--rule-path caminho] [--context pasta]
//                               [--conditions baseline,rule] [--scenarios a,b] [--langs x,y]
//                               [--append]
//
// baseline: projeto sem a rule. rule: o mesmo projeto com rule/comments.md gravada onde o
// harness carrega instruções (--harness, ou --rule-path para um caminho qualquer dentro
// do projeto).
//
// --context copia o conteúdo de uma pasta para a raiz de TODOS os projetos, nas duas
// condições: serve para medir a rule ao lado das instruções que o time já usa.
// --tag marca as execuções criadas (por exemplo, com o modelo que vai executá-las) e vira
// parte do rótulo no relatório. --append acrescenta a uma raiz que já existe.
//
// Os diretórios têm nomes opacos para que o caminho não revele a condição a quem executa
// a tarefa; o mapeamento fica em <raiz>/runs.json.

import { appendFileSync, cpSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { randomBytes } from 'node:crypto';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { LANGS, SCENARIOS } from './scenarios.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const rule = readFileSync(resolve(here, '..', 'rule', 'comments.md'), 'utf8');

// Os mesmos destinos dos instaladores (install.sh / install.ps1).
const LAYOUTS = {
  claude: { path: '.claude/rules/comments.md' },
  agents: { path: 'AGENTS.md' },
  gemini: { path: 'GEMINI.md' },
  copilot: { path: '.github/copilot-instructions.md' },
  cursor: {
    path: '.cursor/rules/comments.mdc',
    front: '---\ndescription: Code comment standard - contract docs, mutation stated, no narrative\nalwaysApply: true\n---\n\n',
  },
};

const args = process.argv.slice(2);
const root = args[0] && !args[0].startsWith('--') ? resolve(args[0]) : null;
if (!root) {
  console.error('uso: setup.mjs <raiz> [--tag ...] [--harness ...] [--rule-path ...] [--context ...] [--conditions ...] [--scenarios ...] [--langs ...] [--append]');
  process.exit(2);
}
const value = (name) => {
  const i = args.indexOf(`--${name}`);
  return i === -1 ? null : args[i + 1];
};
const list = (name, all) => (value(name) ? value(name).split(',') : all);

const conditions = list('conditions', ['baseline', 'rule']);
const scenarios = list('scenarios', Object.keys(SCENARIOS));
const langs = list('langs', Object.keys(LANGS));
const tag = value('tag');
const context = value('context') ? resolve(value('context')) : null;
const harness = value('harness') ?? 'claude';
if (!LAYOUTS[harness]) {
  console.error(`harness desconhecido: ${harness} (use ${Object.keys(LAYOUTS).join(', ')} ou --rule-path)`);
  process.exit(2);
}
const layout = value('rule-path') ? { path: value('rule-path') } : LAYOUTS[harness];
const append = args.includes('--append');
const runsPath = join(root, 'runs.json');

if (existsSync(runsPath) && !append) {
  console.error(`${root} já tem runs.json; use uma raiz nova ou --append.`);
  process.exit(2);
}
const previous = existsSync(runsPath) ? JSON.parse(readFileSync(runsPath, 'utf8')) : [];

const runs = [];
for (const condition of conditions) {
  for (const scenario of scenarios) {
    for (const lang of langs) {
      const sc = SCENARIOS[scenario];
      const file = sc.files[lang];
      const dir = join(root, `p-${randomBytes(4).toString('hex')}`);
      mkdirSync(dir, { recursive: true });
      if (context) cpSync(context, dir, { recursive: true });
      if (condition === 'rule') {
        const dest = join(dir, layout.path);
        mkdirSync(dirname(dest), { recursive: true });
        // Se o contexto já trouxe esse arquivo, a rule entra no fim dele.
        if (existsSync(dest)) appendFileSync(dest, `\n${rule}`, 'utf8');
        else writeFileSync(dest, (layout.front ?? '') + rule, 'utf8');
      }
      if (sc.seeded) cpSync(join(here, 'seeds', sc.seedFrom ?? scenario, lang, file), join(dir, file));
      writeFileSync(join(dir, 'TASK.md'), sc.task(lang, file) + '\n', 'utf8');
      runs.push({ ...(tag ? { tag } : {}), condition, scenario, lang, dir, file, rulePath: layout.path });
    }
  }
}

// Ordem embaralhada: quem dispara os executores não os agrupa por condição.
runs.sort(() => Math.random() - 0.5);
mkdirSync(root, { recursive: true });
writeFileSync(runsPath, JSON.stringify([...previous, ...runs], null, 2), 'utf8');
console.log(`${runs.length} projetos de teste criados em ${root}${tag ? ` (tag ${tag})` : ''}; rule em ${layout.path}`);
for (const r of runs) console.log(r.dir);
