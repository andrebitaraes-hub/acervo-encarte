#!/usr/bin/env python3
"""Busca a foto do produto no acervo compartilhado (github.com/andrebitaraes-hub/acervo-encarte).

Uso: .venv/bin/python .claude/skills/encarte-varejotech/scripts/buscar_acervo.py <EAN> <saida.png>
Saída: "ACHOU <caminho>" (exit 0) ou "NAO_ACHOU <EAN>" (exit 1).
Usa a cópia local em ~/Documents/acervo-encarte (rode `git pull` nela antes da rodada);
sem cópia local, baixa do GitHub.
"""
import shutil
import sys
from pathlib import Path

import requests

LOCAL = Path.home() / 'Documents/acervo-encarte'
RAW = 'https://raw.githubusercontent.com/andrebitaraes-hub/acervo-encarte/main/imagens/{pre}/{ean}.{ext}'
EXTS = ('webp', 'png', 'jpg')


def candidatos(ean):
    ean = ''.join(ch for ch in ean if ch.isdigit())
    vistos = [ean]
    sem_zeros = ean.lstrip('0')
    if sem_zeros and sem_zeros not in vistos:
        vistos.append(sem_zeros)
    if len(ean) == 14 and ean[1:] not in vistos:
        vistos.append(ean[1:])
    return vistos


def main():
    ean, saida = sys.argv[1], Path(sys.argv[2])
    saida.parent.mkdir(parents=True, exist_ok=True)
    for e in candidatos(ean):
        pre = e[:7]
        for ext in EXTS:
            f = LOCAL / 'imagens' / pre / f'{e}.{ext}'
            if f.exists():
                destino = saida.with_suffix(f'.{ext}')
                shutil.copy(f, destino)
                print(f'ACHOU {destino}')
                return 0
        if not LOCAL.exists():
            for ext in EXTS:
                r = requests.get(RAW.format(pre=pre, ean=e, ext=ext), timeout=20)
                if r.status_code == 200:
                    destino = saida.with_suffix(f'.{ext}')
                    destino.write_bytes(r.content)
                    print(f'ACHOU {destino}')
                    return 0
    print(f'NAO_ACHOU {ean}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
