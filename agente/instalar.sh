#!/usr/bin/env bash
# Ensina o agente de encarte (Gondola) a usar o acervo compartilhado:
# busca a foto no acervo primeiro, gera pela IA só se não achar, e devolve ao acervo
# as fotos novas que o dono do mercado aprovar.
#
# Uso (de dentro da pasta do agente, a que tem .claude/ e .venv/):
#   bash ~/Documents/acervo-encarte/agente/instalar.sh "Nome do Mercado"
# Pode rodar de novo sem problema (por exemplo, depois de reinstalar o Gondola).
set -euo pipefail

say()  { printf "\033[1;32m==>\033[0m %s\n" "$*"; }
die()  { printf "\033[1;31m[x]\033[0m %s\n" "$*" >&2; exit 1; }

AQUI="$(cd "$(dirname "$0")" && pwd)"
AGENTE="$(pwd)"
SKILL_DIR="$AGENTE/.claude/skills/encarte-varejotech"
SKILL="$SKILL_DIR/SKILL.md"
ACERVO="$HOME/Documents/acervo-encarte"

[ -f "$SKILL" ] || die "Rode de dentro da pasta do agente de encarte (não achei .claude/skills/encarte-varejotech/SKILL.md aqui)."
[ -x "$AGENTE/.venv/bin/python" ] || die "Falta o .venv do agente — rode o ./setup.sh do Gondola antes."

MERCADO="${1:-}"
if [ -z "$MERCADO" ] && [ -f "$AGENTE/.acervo.json" ]; then
  MERCADO="$("$AGENTE/.venv/bin/python" -c 'import json;print(json.load(open(".acervo.json"))["mercado"])')"
fi
[ -n "$MERCADO" ] || die 'Diga o nome do mercado: bash .../instalar.sh "Nome do Mercado"'

if [ ! -d "$ACERVO/.git" ]; then
  say "Baixando o acervo em $ACERVO…"
  git clone -q https://github.com/andrebitaraes-hub/acervo-encarte.git "$ACERVO"
else
  git -C "$ACERVO" pull -q || true
fi

say "Copiando os scripts para o agente…"
mkdir -p "$SKILL_DIR/scripts"
cp "$AQUI"/buscar_acervo.py "$AQUI"/buscar_granel.py "$AQUI"/gerar_produto.py "$AQUI"/acervo_envio.py "$SKILL_DIR/scripts/"

say "Gravando o nome do mercado (.acervo.json)…"
printf '{"mercado": "%s"}\n' "$MERCADO" > "$AGENTE/.acervo.json"

say "Acrescentando a regra do acervo nas instruções do agente…"
"$AGENTE/.venv/bin/python" - "$SKILL" "$AQUI/trecho-skill.md" <<'PY'
import re, sys
skill, trecho = sys.argv[1], open(sys.argv[2], encoding='utf-8').read().strip() + '\n'
s = open(skill, encoding='utf-8').read()
s = re.sub(r'\n?<!-- ACERVO-VAREJOTECH:INICIO.*?ACERVO-VAREJOTECH:FIM -->\n?', '\n', s, flags=re.S)
m = re.search(r'^## Fluxo de trabalho.*$', s, flags=re.M)
s = (s[:m.start()] + trecho + '\n' + s[m.start():]) if m else (s.rstrip() + '\n\n' + trecho)
open(skill, 'w', encoding='utf-8').write(s)
PY

grep -q '^acervo-candidatos/' "$AGENTE/.gitignore" 2>/dev/null || printf 'acervo-candidatos/\n.acervo.json\n' >> "$AGENTE/.gitignore"

command -v gh >/dev/null || [ -x "$HOME/bin/gh" ] || \
  printf "\033[1;33m[!]\033[0m Para devolver fotos ao acervo, instale o GitHub CLI (https://cli.github.com) e rode: gh auth login\n"

say "Pronto ✅  Mercado: $MERCADO"
echo "   A partir de agora o agente procura a foto no acervo antes de gerar pela IA."
