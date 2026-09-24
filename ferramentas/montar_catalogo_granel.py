#!/usr/bin/env python3
"""Monta o catalogo_granel.csv a partir das fichas em granel/.

Ninguém edita o catalogo_granel.csv na mão: ele é refeito a cada envio aprovado.
Uso: python3 ferramentas/montar_catalogo_granel.py
"""
import csv

from conferir_granel import CAMPOS, FORMATOS, PASTA, RAIZ, ler_ficha

linhas = []
for ficha in sorted(PASTA.rglob("*.txt")) if PASTA.exists() else []:
    imagem = next((p for p in ficha.parent.glob(ficha.stem + ".*") if p.suffix.lower() in FORMATOS), None)
    dados = ler_ficha(ficha)
    linhas.append({
        "id": ficha.stem,
        "categoria": ficha.parent.name,
        **{c: dados.get(c, "") for c in CAMPOS},
        "imagem": imagem.relative_to(RAIZ).as_posix() if imagem else "",
    })

with (RAIZ / "catalogo_granel.csv").open("w", encoding="utf-8", newline="") as f:
    escritor = csv.DictWriter(f, fieldnames=["id", "categoria", *CAMPOS, "imagem"])
    escritor.writeheader()
    escritor.writerows(linhas)
print(f"catalogo_granel.csv com {len(linhas)} produto(s).")
