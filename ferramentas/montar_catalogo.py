#!/usr/bin/env python3
"""Monta o catalogo.csv a partir das fichas (<ean>.txt) em imagens/.

Ninguém edita o catalogo.csv na mão: ele é refeito a cada envio aprovado.
Uso: python3 ferramentas/montar_catalogo.py
"""
import csv

from conferir import CAMPOS, FORMATOS, PASTA, RAIZ, ler_ficha

linhas = []
for ficha in sorted(PASTA.rglob("*.txt")):
    imagem = next((p for p in ficha.parent.glob(ficha.stem + ".*") if p.suffix.lower() in FORMATOS), None)
    dados = ler_ficha(ficha)
    linhas.append({
        "ean": ficha.stem,
        **{c: dados.get(c, "") for c in CAMPOS},
        "imagem": imagem.relative_to(RAIZ).as_posix() if imagem else "",
    })

with (RAIZ / "catalogo.csv").open("w", encoding="utf-8", newline="") as f:
    escritor = csv.DictWriter(f, fieldnames=["ean", *CAMPOS, "imagem"])
    escritor.writeheader()
    escritor.writerows(linhas)
print(f"catalogo.csv com {len(linhas)} produto(s).")
