#!/usr/bin/env python3
"""Último recurso: gera a foto de um produto pelo gpt-image-2 (fundo branco) e recorta.

Uso: set -a; . ./.env; set +a
     .venv/bin/python gerar_produto.py "<descrição completa com marca e gramatura>" <saida_ref.png> [foto_referencia.jpg]
     .venv/bin/python gerar_produto.py --granel "<carne/fruta/verdura>" <saida_ref.png>   (a granel: tábua, sem texto)
Sai o PNG de fundo branco em <saida_ref.png>. Recorte com cutout.py depois.
A embalagem pode sair com texto errado: SEMPRE mostrar ao dono do mercado antes de usar ou enviar ao acervo.
"""
import base64
import os
import sys
from pathlib import Path

import requests

PROMPT = ('Foto de estúdio, realista, de um único produto de supermercado: {desc}. '
          'Produto inteiro, de frente, centralizado, ocupando cerca de 80% da altura, '
          'sobre fundo branco liso (#FFFFFF), sem sombra no fundo, sem outros objetos, sem texto fora da embalagem. '
          'Reproduza fielmente a embalagem real da marca: logotipo, cores e textos do rótulo escritos corretamente.')
PROMPT_GRANEL = ('Foto de estúdio, realista e apetitosa, de um produto a granel de supermercado: {desc}. '
                 'Produto inteiro, visto levemente de cima, centralizado, sobre uma tábua de madeira clara (ou bandeja, se fizer mais sentido), '
                 'com poucas folhas de salsinha como enfeite; fundo branco liso (#FFFFFF), sem sombra no fundo, '
                 'sem nenhum texto, etiqueta, preço, logo ou embalagem.')


def main():
    granel = '--granel' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--granel']
    desc, saida = args[0], Path(args[1])
    ref = args[2] if len(args) > 2 else None
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        sys.exit('OPENAI_API_KEY não carregada (rode: set -a; . ./.env; set +a)')
    h = {'Authorization': f'Bearer {key}'}
    data = {'model': 'gpt-image-2', 'prompt': (PROMPT_GRANEL if granel else PROMPT).format(desc=desc), 'size': '1024x1024', 'quality': 'high'}
    if ref:
        with open(ref, 'rb') as f:
            r = requests.post('https://api.openai.com/v1/images/edits', headers=h, data=data,
                              files={'image[]': (Path(ref).name, f, 'image/png')}, timeout=300)
    else:
        r = requests.post('https://api.openai.com/v1/images/generations', headers=h, json=data, timeout=300)
    if r.status_code != 200:
        sys.exit(f'ERRO API {r.status_code}: {r.text[:400]}')
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_bytes(base64.b64decode(r.json()['data'][0]['b64_json']))
    print(f'GERADO {saida} (mostrar ao dono do mercado antes de usar)')


if __name__ == '__main__':
    main()
