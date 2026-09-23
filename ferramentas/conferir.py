#!/usr/bin/env python3
"""Confere o acervo: código de barras válido, imagem no lugar certo,
tamanho dentro do padrão e cada imagem cadastrada no catalogo.csv.

Uso: python3 ferramentas/conferir.py
Sai com erro (código 1) se achar qualquer problema.
"""
import csv
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "imagens"
CATALOGO = RAIZ / "catalogo.csv"

FORMATOS = {".png", ".jpg", ".jpeg", ".webp"}
PESO_MAX_KB = 500
LADO_MIN = 800
LADO_MAX = 1500
COLUNAS = ["ean", "descricao", "marca", "conteudo", "enviado_por", "data"]


def ean_valido(codigo: str) -> bool:
    """GTIN-8, 12, 13 ou 14 com dígito verificador certo."""
    if not codigo.isdigit() or len(codigo) not in (8, 12, 13, 14):
        return False
    corpo, dv = codigo[:-1], int(codigo[-1])
    soma = sum(int(d) * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(corpo)))
    return (10 - soma % 10) % 10 == dv


def pasta_do(ean: str) -> str:
    return ean[:7]


def main() -> int:
    erros = []

    with CATALOGO.open(encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        if leitor.fieldnames != COLUNAS:
            erros.append(f"catalogo.csv: cabeçalho deve ser {','.join(COLUNAS)}")
        linhas = list(leitor)

    cadastrados = {}
    for n, linha in enumerate(linhas, start=2):
        ean = (linha.get("ean") or "").strip()
        if not ean_valido(ean):
            erros.append(f"catalogo.csv linha {n}: código de barras inválido '{ean}'")
        elif ean in cadastrados:
            erros.append(f"catalogo.csv linha {n}: {ean} repetido (já está na linha {cadastrados[ean]})")
        else:
            cadastrados[ean] = n
        if not (linha.get("descricao") or "").strip():
            erros.append(f"catalogo.csv linha {n}: falta a descrição")

    com_imagem = set()
    for arq in sorted(PASTA.rglob("*")):
        if arq.is_dir() or arq.name == ".gitkeep":
            continue
        rel = arq.relative_to(RAIZ)
        ean, ext = arq.stem, arq.suffix.lower()

        if ext not in FORMATOS:
            erros.append(f"{rel}: formato não aceito (use png, jpg ou webp)")
            continue
        if not ean_valido(ean):
            erros.append(f"{rel}: o nome do arquivo tem que ser o código de barras, e esse não é válido")
            continue
        if arq.parent != PASTA / pasta_do(ean):
            erros.append(f"{rel}: está na pasta errada, deveria estar em imagens/{pasta_do(ean)}/")
        if ean in com_imagem:
            erros.append(f"{rel}: já existe outra imagem para {ean}")
        com_imagem.add(ean)

        kb = arq.stat().st_size / 1024
        if kb > PESO_MAX_KB:
            erros.append(f"{rel}: {kb:.0f} KB, o máximo é {PESO_MAX_KB} KB")
        try:
            with Image.open(arq) as img:
                lado = max(img.size)
        except Exception:
            erros.append(f"{rel}: não consegui abrir a imagem")
            continue
        if not LADO_MIN <= lado <= LADO_MAX:
            erros.append(f"{rel}: lado maior tem {lado}px, tem que ficar entre {LADO_MIN} e {LADO_MAX}px")

        if ean not in cadastrados:
            erros.append(f"{rel}: falta cadastrar {ean} no catalogo.csv")

    for ean, n in cadastrados.items():
        if ean not in com_imagem:
            erros.append(f"catalogo.csv linha {n}: {ean} cadastrado sem imagem")

    if erros:
        print(f"{len(erros)} problema(s):")
        for e in erros:
            print(" -", e)
        return 1
    print(f"Tudo certo: {len(com_imagem)} imagem(ns) no acervo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
