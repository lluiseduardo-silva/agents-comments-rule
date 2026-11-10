#!/usr/bin/env node
// Copia uma raiz de execução para uma pasta publicável, sem caminhos da máquina de quem
// rodou:
//   <destino>/judge/           arquivos cegos, expectativas e notas do avaliador
//   <destino>/judge-map.json   id -> modelo, condição, cenário, linguagem
//   <destino>/saidas/          os mesmos arquivos, organizados para leitura humana
// Depois, `node bench/report.mjs <destino>` recalcula resumo.md a partir do que foi
// publicado.
//
//   node bench/export.mjs <raiz> <destino> [--tag nome-para-execuções-sem-tag]

import { cpSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { extname, join, resolve } from 'node:path';

const [rootArg, destArg] = process.argv.slice(2);
if (!rootArg || !destArg) {
  console.error('uso: export.mjs <raiz> <destino> [--tag nome]');
  process.exit(2);
}
const root = resolve(rootArg);
const dest = resolve(destArg);
const tagAt = process.argv.indexOf('--tag');
const defaultTag = tagAt === -1 ? null : process.argv[tagAt + 1];

const map = JSON.parse(readFileSync(join(root, 'judge-map.json'), 'utf8'));
mkdirSync(dest, { recursive: true });
cpSync(join(root, 'judge'), join(dest, 'judge'), { recursive: true });

const clean = {};
let copied = 0;
for (const [id, cell] of Object.entries(map)) {
  const { dir: _dir, ...rest } = cell;
  const tag = cell.tag ?? defaultTag;
  clean[id] = { ...(tag ? { tag } : {}), ...rest };
  const blind = join(root, 'judge', cell.batch ?? cell.lang, id + extname(cell.file));
  if (!existsSync(blind)) continue;
  const out = join(dest, 'saidas', tag ?? 'sem-tag', cell.condition, cell.scenario, cell.lang);
  mkdirSync(out, { recursive: true });
  cpSync(blind, join(out, cell.file));
  copied++;
}
writeFileSync(join(dest, 'judge-map.json'), JSON.stringify(clean, null, 2), 'utf8');
console.log(`${copied} execuções exportadas para ${dest}`);
