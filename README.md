# Acervo de imagens para encarte

Banco de imagens de produto da comunidade Varejo Tech, para todo mundo montar encarte com foto de qualidade e o agente de encarte achar a imagem pelo código de barras.

## A regra principal

**Só entra produto com código de barras (EAN).** O nome do produto muda de loja para loja; o código de barras é o mesmo em qualquer lugar. Por isso a imagem se chama pelo código, e não pelo nome.

Produto de balança (carne, frios, padaria com etiqueta da loja) não entra, porque o código é interno de cada mercado.

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

## Conferência automática

Todo envio passa pelo `ferramentas/conferir.py`, que barra código de barras inválido (o último dígito confere os outros), imagem fora do padrão, pasta errada, imagem sem ficha e foto de terceiro sem autorização. Para rodar no seu computador:

```
pip install pillow
python3 ferramentas/conferir.py
```
