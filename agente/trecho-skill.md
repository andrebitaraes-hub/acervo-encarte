
<!-- ACERVO-VAREJOTECH:INICIO — acrescentado pelo instalar.sh do acervo-encarte; não editar à mão -->
## REGRA DA COMUNIDADE — foto de produto: acervo primeiro, IA só em último caso

Vale para **todo** encarte, cartaz ou arte com produto, **antes** do passo
"Imagens dos produtos". Objetivo: não pagar a API por foto que alguém do grupo
já tem, e devolver ao grupo toda foto nova.

**0. Atualize a cópia do acervo** no começo da rodada:
`git -C ~/Documents/acervo-encarte pull -q`

**1. Produto com código de barras** — busque pelo EAN (o do cadastro do ERP;
o script já testa sem os zeros à esquerda):
```
.venv/bin/python .claude/skills/encarte-varejotech/scripts/buscar_acervo.py <EAN> output/<brand>/<job>/ref/NN_nome
```
Se o briefing não trouxer o EAN, peça ao dono do mercado ou busque no ERP.

**2. Produto a granel** (carne, frango, peixe, hortifruti, frios, padaria —
sem código de barras) — busque pelo nome como veio na lista:
```
.venv/bin/python .claude/skills/encarte-varejotech/scripts/buscar_granel.py "<nome da lista>" output/<brand>/<job>/ref/NN_nome
```

`ACHOU` → use a foto **como está** (só recorte de fundo). O gerador **nunca**
redesenha um produto que veio do acervo.

**3. `NAO_ACHOU`** → só então gere pelo GPT Image 2:
```
set -a; . ./.env; set +a
.venv/bin/python .claude/skills/encarte-varejotech/scripts/gerar_produto.py "<nome, marca e gramatura>" output/<brand>/<job>/ref/NN_nome.png
.venv/bin/python .claude/skills/encarte-varejotech/scripts/gerar_produto.py --granel "<corte/fruta/verdura>" output/<brand>/<job>/ref/NN_nome.png
```
(Se o dono do mercado mandou foto do produto, use a foto dele em vez de gerar.)
**Mostre cada imagem gerada ao dono do mercado e só use as que ele aprovar**
— a IA costuma errar o texto da embalagem.

**4. Ao final, devolva ao acervo as fotos novas** (as que não vieram do
acervo), **só as que o dono do mercado aprovar**:
```
.venv/bin/python .claude/skills/encarte-varejotech/scripts/acervo_envio.py preparar <EAN> output/<brand>/<job>/cut/NN.png "<descrição legível>" "<marca>" "<conteúdo>" <origem>
.venv/bin/python .claude/skills/encarte-varejotech/scripts/acervo_envio.py preparar_granel <categoria> output/<brand>/<job>/cut/NN.png "<nome>" "<como veio na lista; outros nomes>" ia
.venv/bin/python .claude/skills/encarte-varejotech/scripts/acervo_envio.py listar
```
Mostre as candidatas (imagem + EAN/nome) e pergunte. Aprovadas →
`enviar <EAN> ...` / `enviar_granel <id> ...`; recusadas → `descartar ...`.
`origem`: `propria`, `ia` (só granel), `industria`/`site` (exigem quem
autorizou) ou `a confirmar`. Categorias de granel: `acougue`, `aves`,
`peixaria`, `hortifruti`, `frios`, `padaria`, `outros`. Nunca use recorte de
um cartaz/encarte pronto como foto de acervo (a arte costuma cobrir parte do
produto). Regras completas: README do acervo-encarte.
<!-- ACERVO-VAREJOTECH:FIM -->
