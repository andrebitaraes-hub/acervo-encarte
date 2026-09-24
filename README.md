# Acervo de imagens para encarte

Banco de imagens de produto da comunidade Varejo Tech, para todo mundo montar encarte com foto de qualidade e o agente de encarte achar a imagem pelo código de barras.

**Usa o agente de encarte (Gondola)?** Instale o [`agente/`](agente/README.md): ele faz o agente procurar a foto aqui antes de gastar com a IA, e devolver ao acervo as fotos novas que você aprovar. Um comando só.

## A regra principal

**Só entra produto com código de barras (EAN).** O nome do produto muda de loja para loja; o código de barras é o mesmo em qualquer lugar. Por isso a imagem se chama pelo código, e não pelo nome.

Produto de balança (carne, frios, padaria com etiqueta da loja) não entra em `imagens/`, porque o código é interno de cada mercado. Ele tem a pasta própria `granel/`, explicada mais abaixo.

## Como mandar uma imagem

Cada produto tem **dois arquivos**, lado a lado, com o código de barras como nome:

```
imagens/7891000/7891000100103.webp   ← a foto
imagens/7891000/7891000100103.txt    ← a ficha
```

1. Nome do arquivo = código de barras, sem espaço nem traço.
2. Os dois vão na pasta com os **7 primeiros dígitos** do código. Ex.: `imagens/7891000/`
3. A ficha é um texto simples, assim:

   ```
   descricao: Leite condensado Moça lata
   marca: Nestlé
   conteudo: 395 g
   origem: propria
   enviado_por: Mercopaulo
   ```

Cada um manda só os próprios arquivos, então vários mercados podem enviar ao mesmo tempo sem um atrapalhar o outro. O `catalogo.csv` com a lista de tudo é montado sozinho a cada envio aprovado; **não edite ele na mão**.

## Direito de uso da foto

O repositório é público, então só entra foto que pode ser usada:

- `origem: propria` — foto que você mesmo tirou ou tratou.
- `origem: industria` ou `origem: site` — só com autorização. Nesse caso preencha também `autorizacao:` dizendo quem autorizou (ex.: `autorizacao: vendedor Fulano, Pif Paf, por e-mail em 23/09/2026`).

Foto do Cosmos, de portal de indústria ou de site de fornecedor sem autorização não entra.

**Durante o teste da ferramenta**, também é aceito `origem: a confirmar`. A foto entra, mas fica marcada como pendência no catálogo até alguém preencher a origem certa.

## Padrão da imagem

- Formato **WEBP com fundo transparente** (recomendado: fica bem menor), PNG ou JPG
- Lado maior entre **800 e 1500 pixels**
- No máximo **1,5 MB**
- Só o produto, de frente, sem preço, sem logo de loja e sem marca d'água
- Uma imagem por código de barras. Achou uma melhor que a atual? Substitua a foto (mesmo nome) e explique no envio.

## Embalagem nova

Quando a marca muda o visual da embalagem, o código de barras continua o mesmo e a foto do acervo fica velha. Mande a foto nova com o **mesmo nome de arquivo**, na mesma pasta, e ela substitui a antiga. Diga no envio que é troca de embalagem.

Se mudou o peso ou o volume (ex.: 400 g virou 395 g), normalmente o código de barras também muda. Aí é produto novo: foto e ficha novas.

## Produto a granel (sem código de barras)

Carne, frango, peixe, fruta, verdura, frios fatiados, pão francês: não têm código de barras, mas aparecem em todo encarte. Eles ficam na pasta `granel/`, separados por categoria, e o nome do arquivo vem do **nome do produto**:

```
granel/acougue/file-de-peito-resfriado.webp   ← a foto
granel/acougue/file-de-peito-resfriado.txt    ← a ficha
```

Categorias: `acougue`, `aves`, `peixaria`, `hortifruti`, `frios`, `padaria`, `outros`.

O nome do arquivo é o campo `nome` da ficha em minúsculo, sem acento e com hífen no lugar do espaço ("Filé de peito resfriado" → `file-de-peito-resfriado`). A ficha:

```
nome: Filé de peito resfriado
apelidos: Filé de frango; Peito de frango sem osso
origem: ia
enviado_por: Mercopaulo
```

- **`apelidos`**: outros nomes pelos quais o mesmo produto aparece nas listas de oferta, separados por ponto e vírgula. Cada mercado chama o corte de um jeito ("acém", "peito reserva", "paleta"); é pelo nome e pelos apelidos que o agente acha a foto. Um apelido não pode repetir em dois produtos.
- **`origem`**: `propria` (foto sua), `ia` (gerada por IA e conferida por quem enviou), `industria` ou `site` (só com `autorizacao:`). Durante o teste, `a confirmar` também vale.
- **Padrão da imagem**: o mesmo das fotos com código de barras (fundo transparente, lado maior entre 800 e 1500 px, até 1,5 MB, WEBP de preferência). Só o produto, pode ser sobre tábua ou bandeja, sem preço e sem logo de loja.
- **Conferir antes de mandar**: `python3 ferramentas/conferir_granel.py`. O `catalogo_granel.csv` é montado sozinho, como o `catalogo.csv`.

## Conferência automática

Todo envio passa pelo `ferramentas/conferir.py`, que barra código de barras inválido (o último dígito confere os outros), imagem fora do padrão, pasta errada, imagem sem ficha e foto de terceiro sem autorização. Para rodar no seu computador:

```
pip install pillow
python3 ferramentas/conferir.py
```

## Quando o envio entra sozinho

O envio entra no acervo sem esperar aprovação quando cumpre **tudo** isto:

- vem de uma conta da lista de confiança (`.github/contas-confiaveis.txt`);
- só **acrescenta** fotos e fichas em `imagens/` ou `granel/`, sem trocar nem apagar nada que já existe;
- nenhuma ficha nova tem origem `a confirmar`;
- passa na conferência oficial. Ela roda sempre as ferramentas do repositório, nunca uma versão que venha junto com o envio.

Qualquer outro envio fica para o André aprovar: troca de embalagem, exclusão, conta fora da lista, mudança nas regras. Quem quiser entrar na lista de confiança é só pedir.
