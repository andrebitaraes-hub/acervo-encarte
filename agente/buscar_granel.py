#!/usr/bin/env python3
"""Busca a foto de um produto a granel (sem código de barras) na pasta granel/ do acervo.

Uso: .venv/bin/python buscar_granel.py "<nome do produto como veio na lista>" <saida_sem_extensao>
Acha pelo nome ou pelos apelidos da ficha. Saída: "ACHOU <caminho> (<nome>)" ou "NAO_ACHOU".
Rode `git -C ~/Documents/acervo-encarte pull -q` antes da rodada.
"""
import re
import shutil
import sys
import unicodedata
from pathlib import Path

GRANEL = Path.home() / 'Documents/acervo-encarte/granel'
FORMATOS = ('.webp', '.png', '.jpg', '.jpeg')
VAZIAS = {'de', 'da', 'do', 'ou', 'e', 'kg', 'resfriado', 'resfriada', 'congelado', 'congelada', 'peca', 'pedaco'}


def slug(t):
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


def palavras(t):
    return {p for p in slug(t).split('-') if p and p not in VAZIAS}


def fichas():
    for f in sorted(GRANEL.glob('*/*.txt')):
        dados = {}
        for linha in f.read_text(encoding='utf-8').splitlines():
            if ':' in linha:
                k, v = linha.split(':', 1)
                dados[k.strip().lower()] = v.strip()
        nomes = [dados.get('nome', f.stem)] + [a.strip() for a in dados.get('apelidos', '').split(';') if a.strip()]
        yield f, dados.get('nome', f.stem), nomes


def main():
    pedido, saida = sys.argv[1], Path(sys.argv[2])
    alvo, alvo_p = slug(pedido), palavras(pedido)
    exato, parecido = None, []
    for f, nome, nomes in fichas():
        if any(slug(n) == alvo for n in nomes):
            exato = (f, nome)
            break
        melhor = max((len(alvo_p & palavras(n)) / max(len(palavras(n)), 1) for n in nomes), default=0)
        if melhor == 1:
            parecido.append((f, nome))
    achado = exato or (parecido[0] if len(parecido) == 1 else None)
    if not achado:
        if len(parecido) > 1:
            print('NAO_ACHOU (ambíguo: ' + ', '.join(n for _, n in parecido) + ')')
        else:
            print('NAO_ACHOU')
        return 1
    f, nome = achado
    img = next((f.with_suffix(e) for e in FORMATOS if f.with_suffix(e).exists()), None)
    if not img:
        print('NAO_ACHOU (ficha sem imagem)')
        return 1
    destino = saida.with_suffix(img.suffix)
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(img, destino)
    print(f'ACHOU {destino} ({nome})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
