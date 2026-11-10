#!/usr/bin/env sh
# Instala a rule de comentarios no projeto atual. Linux e macOS.
#
#   curl -fsSL https://raw.githubusercontent.com/lluiseduardo-silva/agents-comments-rule/main/install.sh | sh
#   curl -fsSL https://raw.githubusercontent.com/lluiseduardo-silva/agents-comments-rule/main/install.sh | sh -s -- --harness agents
#   ./install.sh --harness cursor --target /caminho/do/projeto
#   ./install.sh --uninstall
set -eu

REPO="lluiseduardo-silva/agents-comments-rule"
START="<!-- agents-comments-rule:start"
END="<!-- agents-comments-rule:end"

usage() {
  cat <<'EOF'
uso: install.sh [opcoes]

  --harness <nome>   onde gravar a rule (padrao: claude)
                       claude   .claude/rules/comments.md
                       agents   bloco gerenciado em AGENTS.md
                       gemini   bloco gerenciado em GEMINI.md
                       copilot  bloco gerenciado em .github/copilot-instructions.md
                       cursor   .cursor/rules/comments.mdc (alwaysApply)
  --target <dir>     raiz do projeto (padrao: diretorio atual)
  --dest <arquivo>   grava a rule inteira nesse arquivo, para qualquer harness
  --block <arquivo>  grava a rule como bloco gerenciado dentro desse arquivo
  --global           com --harness claude: instala em ~/.claude/rules (todos os projetos)
  --ref <ref>        branch ou tag de onde baixar (padrao: main)
  --force            sobrescreve um arquivo que nao parece ser desta rule
  --uninstall        remove o que este script instalou
EOF
}

harness=claude
target=.
ref=main
dest=""
block=""
global=0
force=0
uninstall=0
while [ $# -gt 0 ]; do
  case "$1" in
    --harness) harness=${2:?--harness precisa de um valor}; shift 2 ;;
    --target) target=${2:?--target precisa de um valor}; shift 2 ;;
    --dest) dest=${2:?--dest precisa de um valor}; shift 2 ;;
    --block) block=${2:?--block precisa de um valor}; shift 2 ;;
    --ref) ref=${2:?--ref precisa de um valor}; shift 2 ;;
    --global) global=1; shift ;;
    --force) force=1; shift ;;
    --uninstall) uninstall=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "opcao desconhecida: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[ -d "$target" ] || { echo "diretorio nao encontrado: $target" >&2; exit 1; }

# mode=file grava um arquivo so da rule; mode=block mantem um bloco dentro de um arquivo compartilhado.
mode=file
front=""
if [ -n "$dest" ]; then
  path=$dest
elif [ -n "$block" ]; then
  path=$block
  mode=block
else
  case "$harness" in
    claude)
      if [ "$global" = 1 ]; then path="$HOME/.claude/rules/comments.md"; else path=".claude/rules/comments.md"; fi ;;
    agents) path="AGENTS.md"; mode=block ;;
    gemini) path="GEMINI.md"; mode=block ;;
    copilot) path=".github/copilot-instructions.md"; mode=block ;;
    cursor) path=".cursor/rules/comments.mdc"; front=cursor ;;
    *) echo "harness desconhecido: $harness" >&2; usage >&2; exit 2 ;;
  esac
fi
case "$path" in
  /*) full=$path ;;
  *) full="$target/$path" ;;
esac

# Imprime o arquivo $1 sem o bloco gerenciado e sem linhas em branco no fim.
without_block() {
  awk -v s="$START" -v e="$END" '
    index($0, s) == 1 { skip = 1; next }
    index($0, e) == 1 { skip = 0; next }
    skip { next }
    /^[[:space:]]*$/ { pending = pending $0 "\n"; next }
    { printf "%s", pending; pending = ""; print }
  ' "$1"
}

is_ours() { grep -q '^# Code comments' "$1"; }

if [ "$uninstall" = 1 ]; then
  if [ ! -f "$full" ]; then echo "nada instalado em $full"; exit 0; fi
  if [ "$mode" = block ]; then
    rest=$(mktemp)
    without_block "$full" > "$rest"
    if [ -s "$rest" ]; then cat "$rest" > "$full"; echo "bloco removido de $full"
    else rm -f "$full"; echo "removido  $full"; fi
    rm -f "$rest"
  else
    if is_ours "$full" || [ "$force" = 1 ]; then
      rm -f "$full"; echo "removido  $full"
      # Remove as pastas que ficaram vazias (rmdir nao toca em pasta com conteudo).
      parent=$(dirname "$full")
      rmdir "$parent" 2>/dev/null && rmdir "$(dirname "$parent")" 2>/dev/null || true
    else
      echo "$full nao parece ser esta rule; use --force para remover mesmo assim." >&2; exit 1
    fi
  fi
  exit 0
fi

# Fonte: o arquivo ao lado deste script quando roda de um clone; senao, download.
tmp=""
cleanup() { [ -n "$tmp" ] && rm -f "$tmp"; return 0; }
trap cleanup EXIT
here=$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd || true)
if [ -n "$here" ] && [ -f "$here/rule/comments.md" ] && [ -f "$here/install.sh" ]; then
  src="$here/rule/comments.md"
else
  url="https://raw.githubusercontent.com/$REPO/$ref/rule/comments.md"
  tmp=$(mktemp)
  if command -v curl >/dev/null 2>&1; then curl -fsSL "$url" -o "$tmp"
  elif command -v wget >/dev/null 2>&1; then wget -qO "$tmp" "$url"
  else echo "precisa de curl ou wget para baixar a rule" >&2; exit 1; fi
  src=$tmp
fi
is_ours "$src" || { echo "o conteudo obtido nao e a rule esperada (ref: $ref)" >&2; exit 1; }

mkdir -p "$(dirname "$full")"
if [ "$mode" = block ]; then
  rest=$(mktemp)
  if [ -f "$full" ]; then without_block "$full" > "$rest"; else : > "$rest"; fi
  {
    if [ -s "$rest" ]; then cat "$rest"; printf '\n'; fi
    printf '%s (gerenciado por install.sh; edite fora deste bloco) -->\n' "$START"
    cat "$src"
    printf '%s -->\n' "$END"
  } > "$full.tmp"
  mv "$full.tmp" "$full"
  rm -f "$rest"
  echo "instalado bloco em $full"
else
  if [ -f "$full" ] && ! is_ours "$full" && [ "$force" != 1 ]; then
    echo "$full ja existe e nao parece ser esta rule. Use --block para acrescentar a ele, ou --force para sobrescrever." >&2
    exit 1
  fi
  {
    if [ "$front" = cursor ]; then
      printf '%s\n' '---' 'description: Code comment standard - contract docs, mutation stated, no narrative' 'alwaysApply: true' '---' ''
    fi
    cat "$src"
  } > "$full.tmp"
  mv "$full.tmp" "$full"
  echo "instalado $full"
fi
