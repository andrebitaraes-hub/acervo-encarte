# Acervo de imagens para encarte

Banco de imagens de produto da comunidade Varejo Tech, para todo mundo montar encarte com foto de qualidade e o agente de encarte achar a imagem pelo código de barras.

## A regra principal

**Só entra produto com código de barras (EAN).** O nome do produto muda de loja para loja; o código de barras é o mesmo em qualquer lugar. Por isso a imagem se chama pelo código, e não pelo nome.

Produto de balança (carne, frios, padaria com etiqueta da loja) não entra, porque o código é interno de cada mercado.

## Como mandar uma imagem

1. Nome do arquivo = código de barras, sem espaço nem traço. Ex.: `7891000100103.png`
2. Coloque em `imagens/` dentro da pasta com os **7 primeiros dígitos** do código. Ex.: `imagens/7891000/7891000100103.png`
3. Acrescente uma linha no `catalogo.csv`:

   ```
   ean,descricao,marca,conteudo,enviado_por,data
   7891000100103,Leite condensado Moça lata,Nestlé,395 g,Mercopaulo,2026-09-23
   ```

## Padrão da imagem

- Formato **PNG** (de preferência com fundo transparente), JPG ou WEBP
- Lado maior entre **800 e 1500 pixels**
- No máximo **500 KB**
- Só o produto, de frente, sem preço, sem logo de loja e sem marca d'água
- Uma imagem por código de barras. Achou uma melhor que a atual? Substitua o arquivo e explique no envio.

## Embalagem nova

Quando a marca muda o visual da embalagem, o código de barras continua o mesmo e a foto do acervo fica velha. Mande a foto nova com o **mesmo nome de arquivo**, na mesma pasta, e ela substitui a antiga. Atualize a `data` da linha no `catalogo.csv` e diga no envio que é troca de embalagem.

Se mudou o peso ou o volume (ex.: 400 g virou 395 g), normalmente o código de barras também muda. Aí é produto novo: arquivo novo e linha nova no catálogo.

## Conferência automática

Todo envio passa pelo `ferramentas/conferir.py`, que barra código de barras inválido (o último dígito confere os outros), imagem fora do padrão, pasta errada e imagem sem cadastro. Para rodar no seu computador:

```
pip install pillow
python3 ferramentas/conferir.py
```
