#!/usr/bin/env bash
# Decide se um envio pode entrar sozinho. Roda dentro da cópia do envio,
# com a versão oficial (main) em ../base. Nunca executa nada do envio.
# Uso: AUTOR=<login> BASE_SHA=<sha> bash ../base/ferramentas/regras_envio.sh
# Escreve automatico=true|false em $GITHUB_OUTPUT (ou na tela).
set -euo pipefail
LISTA=${LISTA:-../base/.github/contas-confiaveis.txt}
SAIDA=${GITHUB_OUTPUT:-/dev/stdout}
motivos=()

grep -qxF -- "$AUTOR" "$LISTA" || motivos+=("a conta $AUTOR não está na lista de contas de confiança")

mudancas=$(git diff --name-status --no-renames "$BASE_SHA...HEAD")
fora=$(printf '%s\n' "$mudancas" | awk -F'\t' 'NF && ($1 != "A" || $2 !~ /^(imagens|granel)\//)')
[ -z "$fora" ] || motivos+=("troca, apaga ou mexe fora de imagens/ e granel/: $(printf '%s' "$fora" | tr '\t\n' ' ;')")

if git diff --summary "$BASE_SHA...HEAD" | grep -q ' mode 120000 '; then
  motivos+=("tem atalho (symlink)")
fi

pendente=""
while IFS=$'\t' read -r st arq; do
  if [ "$st" = A ] && [[ "$arq" == *.txt ]] && [ -f "$arq" ] \
     && grep -qiE '^[[:space:]]*origem:[[:space:]]*a confirmar' -- "$arq"; then
    pendente+="$arq "
  fi
done <<< "$mudancas"
[ -z "$pendente" ] || motivos+=("ficha com origem 'a confirmar': $pendente")

if [ ${#motivos[@]} -eq 0 ]; then
  echo "automatico=true" >> "$SAIDA"
  echo "Envio pode entrar sozinho." >&2
else
  echo "automatico=false" >> "$SAIDA"
  echo "Fica para o André aprovar:" >&2
  printf ' - %s\n' "${motivos[@]}" >&2
fi
