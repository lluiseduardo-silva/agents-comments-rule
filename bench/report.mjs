#!/usr/bin/env node
// Junta a avaliação cega (<raiz>/judge/<lote>/<id>.judge.json) com as checagens
// determinísticas (tokens plantados) e grava <raiz>/resumo.md e <raiz>/resumo.json.
// Funciona tanto numa raiz de execução quanto numa pasta publicada em results/.
//
//   node bench/report.mjs <raiz>

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { LANGS, SCENARIOS } from './scenarios.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(process.argv[2] ?? '');
const map = JSON.parse(readFileSync(join(root, 'judge-map.json'), 'utf8'));

const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const hasToken = (text, tok) =>
  new RegExp(`(?<![\\p{L}\\p{N}])${esc(tok)}(?![\\p{L}\\p{N}])`, 'iu').test(text);

const problems = [];
const runs = [];
for (const [id, raw] of Object.entries(map)) {
  // Com --tag no setup, o rótulo da condição passa a ser "<tag> <condição>".
  const { dir: _dir, ...rest } = raw;
  const cell = { ...rest, condition: raw.tag ? `${raw.tag} ${raw.condition}` : raw.condition };
  const sc = SCENARIOS[cell.scenario];
  const ext = extname(cell.file);
  // Raízes antigas agrupavam os arquivos por linguagem em vez de por lote.
  const folder = join(root, 'judge', cell.batch ?? cell.lang);
  const source = readFileSync(join(folder, id + ext), 'utf8');
  const seedPath = join(here, 'seeds', sc.seedFrom ?? cell.scenario, cell.lang, cell.file);
  const changed = sc.seeded ? readFileSync(seedPath, 'utf8') !== source : true;

  const leaks = {};
  for (const [group, toks] of Object.entries(sc.tokens)) {
    leaks[group] = toks.filter((t) => hasToken(source, t));
  }

  const judgePath = join(folder, `${id}.judge.json`);
  let judge = null;
  if (existsSync(judgePath)) {
    try {
      judge = JSON.parse(readFileSync(judgePath, 'utf8'));
    } catch (e) {
      problems.push(`${id}: judge.json inválido (${e.message})`);
    }
  } else {
    problems.push(`${id}: sem judge.json`);
  }

  const targets = sc.targets.map((exp) => {
    const got = judge?.targets?.find((t) => t.name === exp.name);
    if (judge && !got) problems.push(`${id}: alvo "${exp.name}" ausente na avaliação`);
    const g = got ?? {};
    const ok = Boolean(g.found && g.has_doc);
    const items = { doc: ok ? 1 : 0 };
    if (exp.kind !== 'type') {
      if (exp.params.length) {
        items.params = ok ? Math.min(g.params_documented ?? 0, exp.params.length) / exp.params.length : 0;
      }
      if (exp.returns) items.ret = ok && g.return_documented ? 1 : 0;
      if (exp.errors.length) {
        items.errors = ok ? Math.min(g.errors_documented ?? 0, exp.errors.length) / exp.errors.length : 0;
      }
      if (exp.kind === 'function') items.mutation = ok && g.mutation === 'explicit' ? 1 : 0;
      if (exp.partial_failure) items.partial = ok && g.partial_failure_documented ? 1 : 0;
    }
    const vals = Object.values(items);
    return {
      name: exp.name,
      kind: exp.kind,
      items,
      score: vals.reduce((a, b) => a + b, 0) / vals.length,
      mutation: ok ? g.mutation ?? 'absent' : 'absent',
      mutationComplete: Boolean(ok && g.mutation_complete),
      narrative: g.narrative ?? [],
      inlineComments: g.inline_comments ?? 0,
      docLines: g.doc_lines ?? 0,
    };
  });

  runs.push({
    id,
    ...cell,
    changed,
    judged: Boolean(judge),
    proseLanguage: judge?.prose_language ?? null,
    idiomatic: judge?.idiomatic_format ?? null,
    targets,
    narrative: targets.flatMap((t) => t.narrative.map((n) => ({ target: t.name, ...n }))),
    leaks,
  });
}

function agg(rs) {
  const ts = rs.flatMap((r) => r.targets);
  const fns = ts.filter((t) => t.kind === 'function');
  const sum = (arr, f) => arr.reduce((a, x) => a + f(x), 0);
  const ratio = (key) => {
    const withKey = ts.filter((t) => key in t.items);
    return [sum(withKey, (t) => t.items[key]), withKey.length];
  };
  return {
    runs: rs.length,
    targets: ts.length,
    doc: ratio('doc'),
    params: ratio('params'),
    ret: ratio('ret'),
    errors: ratio('errors'),
    mutExplicit: ratio('mutation'),
    mutComplete: [fns.filter((t) => t.mutationComplete).length, fns.length],
    partial: ratio('partial'),
    contract: [sum(ts, (t) => t.score), ts.length],
    narrative: sum(rs, (r) => r.narrative.length),
    runsNoNarrative: [rs.filter((r) => r.narrative.length === 0).length, rs.length],
    leaked: sum(rs, (r) => (r.leaks.pedido ?? []).length),
    runsNoLeak: [rs.filter((r) => (r.leaks.pedido ?? []).length === 0).length, rs.length],
    docLines: [sum(ts, (t) => t.docLines), ts.length],
  };
}

const pct = ([n, d]) => (d ? `${Math.round((n / d) * 100)}%` : 'n/a');
const frac = ([n, d]) => `${n}/${d}`;
const avg = ([n, d]) => (d ? (n / d).toFixed(1) : 'n/a');

const HEAD =
  '| | execuções | doc | parâmetros | retorno | erros | mutação explícita | mutação completa | falha parcial | **contrato** | frases narrativas | exec. sem narrativa | tokens vazados | exec. sem vazamento | linhas/doc |\n' +
  '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|';
const row = (label, a) =>
  `| ${label} | ${a.runs} | ${pct(a.doc)} | ${pct(a.params)} | ${pct(a.ret)} | ${pct(a.errors)} | ${pct(a.mutExplicit)} | ${pct(a.mutComplete)} | ${pct(a.partial)} | **${pct(a.contract)}** | ${a.narrative} | ${frac(a.runsNoNarrative)} | ${a.leaked} | ${frac(a.runsNoLeak)} | ${avg(a.docLines)} |`;

const conditions = [...new Set(runs.map((r) => r.condition))].sort();
const scenarios = Object.keys(SCENARIOS).filter((s) => runs.some((r) => r.scenario === s));
const langs = Object.keys(LANGS).filter((l) => runs.some((r) => r.lang === l));
const sel = (f) => runs.filter(f);

const out = [];
out.push('# Benchmark da rule de comentários', '');
out.push(`${runs.length} execuções avaliadas.`, '');
out.push(
  '"baseline" é o projeto sem a rule; "rule" é o mesmo projeto com ela. As colunas de contrato vêm da avaliação cega (`bench/RUBRIC.md`); "tokens vazados" é a checagem determinística dos nomes, tickets e datas plantados no pedido. "contrato" é a média, por declaração-alvo, dos itens aplicáveis: doc, parâmetros, retorno, erros, mutação explícita e falha parcial.',
  '',
);
if (problems.length) {
  out.push('## Problemas na avaliação', '', ...problems.map((p) => `- ${p}`), '');
}
const unchanged = runs.filter((r) => !r.changed);
if (unchanged.length) {
  out.push('## Execuções que não alteraram o arquivo', '');
  for (const r of unchanged) out.push(`- ${r.condition} ${r.scenario} ${r.lang} (${r.id})`);
  out.push('');
}

out.push('## Geral', '', HEAD);
for (const c of conditions) out.push(row(c, agg(sel((r) => r.condition === c))));
out.push('', '## Por cenário', '', HEAD);
for (const s of scenarios) {
  for (const c of conditions) {
    const a = agg(sel((r) => r.scenario === s && r.condition === c));
    if (a.runs) out.push(row(`${s} · ${c}`, a));
  }
}
out.push('', '## Por linguagem', '', HEAD);
for (const l of langs) {
  for (const c of conditions) {
    const a = agg(sel((r) => r.lang === l && r.condition === c));
    if (a.runs) out.push(row(`${LANGS[l].name} · ${c}`, a));
  }
}

if (scenarios.includes('s3-infested')) {
  const tk = SCENARIOS['s3-infested'].tokens;
  out.push('', '## Cenário 3: o que aconteceu com a narrativa que já estava no arquivo', '');
  out.push(
    'Tokens restantes no arquivo final, somados nas execuções (restantes/possíveis). "alterada" deveria ir a zero; "intocada" deveria ficar inteira.',
    '',
    '| condição | função alterada (`aplicar`) | função intocada (`totalDeCupons`) | comentário da classe | vindos do pedido |',
    '|---|---|---|---|---|',
  );
  for (const c of conditions) {
    const rs = sel((r) => r.scenario === 's3-infested' && r.condition === c);
    if (!rs.length) continue;
    const g = (k) => `${rs.reduce((a, r) => a + r.leaks[k].length, 0)}/${rs.length * tk[k].length}`;
    out.push(`| ${c} | ${g('alterada')} | ${g('intocada')} | ${g('classe')} | ${g('pedido')} |`);
  }
}

out.push('', '## Formato e idioma', '', '| condição | formato idiomático | prosa |', '|---|---|---|');
for (const c of conditions) {
  const rs = sel((r) => r.condition === c);
  const idi = rs.filter((r) => r.idiomatic === true).length;
  const langCount = {};
  for (const r of rs) langCount[r.proseLanguage] = (langCount[r.proseLanguage] ?? 0) + 1;
  out.push(`| ${c} | ${idi}/${rs.length} | ${Object.entries(langCount).map(([k, v]) => `${k}: ${v}`).join(', ')} |`);
}

for (const c of conditions) {
  const rs = sel((r) => r.condition === c);
  out.push('', `## Falhas na condição "${c}"`, '');
  const lines = [];
  for (const r of rs) {
    for (const t of r.targets) {
      const miss = Object.entries(t.items).filter(([, v]) => v < 1).map(([k, v]) => (v === 0 ? k : `${k} (parcial)`));
      if (miss.length) lines.push(`- ${r.scenario} · ${LANGS[r.lang].name} · \`${t.name}\` (${r.id}): falta ${miss.join(', ')}`);
    }
    for (const n of r.narrative) {
      lines.push(`- ${r.scenario} · ${LANGS[r.lang].name} · \`${n.target}\` (${r.id}): narrativa [${n.category}] "${String(n.text).replace(/\s+/g, ' ').slice(0, 220)}"`);
    }
    if ((r.leaks.pedido ?? []).length) {
      lines.push(`- ${r.scenario} · ${LANGS[r.lang].name} (${r.id}): tokens do pedido no arquivo: ${r.leaks.pedido.join(', ')}`);
    }
  }
  out.push(...(lines.length ? lines : ['Nenhuma.']));
}

writeFileSync(join(root, 'resumo.md'), out.join('\n') + '\n', 'utf8');
writeFileSync(join(root, 'resumo.json'), JSON.stringify({ runs, problems }, null, 2), 'utf8');
console.log(out.join('\n'));
