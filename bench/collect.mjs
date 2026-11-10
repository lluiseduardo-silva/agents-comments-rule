#!/usr/bin/env node
// Prepara a avaliação cega: copia o arquivo produzido em cada projeto de teste para
// <raiz>/judge/<lote>/<id>.<ext>, com um id aleatório, junto de <id>.expect.json (o que
// cada declaração-alvo deveria documentar). Os lotes misturam condições, cenários e
// linguagens em ordem aleatória. Quem avalia vê só esses arquivos; o vínculo
// id -> condição fica em <raiz>/judge-map.json.
//
//   node bench/collect.mjs <raiz> [--batch 6]

import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { randomBytes } from 'node:crypto';
import { dirname, extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { LANGS, SCENARIOS } from './scenarios.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(process.argv[2] ?? '');
const batchAt = process.argv.indexOf('--batch');
const batchSize = batchAt === -1 ? 6 : Number(process.argv[batchAt + 1]);
const runs = JSON.parse(readFileSync(join(root, 'runs.json'), 'utf8'));

const present = runs.filter((r) => existsSync(join(r.dir, r.file)));
const missing = runs.filter((r) => !present.includes(r));
present.sort(() => Math.random() - 0.5);

const map = {};
const batches = new Set();
present.forEach((run, i) => {
  const batch = `b${String(Math.floor(i / batchSize) + 1).padStart(2, '0')}`;
  const dir = join(root, 'judge', batch);
  mkdirSync(dir, { recursive: true });
  batches.add(batch);
  const id = randomBytes(4).toString('hex');
  const file = id + extname(run.file);
  copyFileSync(join(run.dir, run.file), join(dir, file));
  const expect = { id, language: LANGS[run.lang].name, file, targets: SCENARIOS[run.scenario].targets };
  writeFileSync(join(dir, `${id}.expect.json`), JSON.stringify(expect, null, 2), 'utf8');
  map[id] = { ...run, batch };
});
for (const batch of batches) copyFileSync(join(here, 'RUBRIC.md'), join(root, 'judge', batch, 'RUBRIC.md'));

writeFileSync(join(root, 'judge-map.json'), JSON.stringify(map, null, 2), 'utf8');
console.log(`${present.length} arquivos em ${batches.size} lotes: ${join(root, 'judge')}`);
for (const batch of batches) console.log(join(root, 'judge', batch));
if (missing.length) {
  console.log(`SEM ARQUIVO (${missing.length}):`);
  for (const m of missing) console.log(`  ${m.tag ?? ''} ${m.condition} ${m.scenario} ${m.lang} ${m.dir}`);
}
