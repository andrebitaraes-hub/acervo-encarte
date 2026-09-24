#!/usr/bin/env python3
"""Confere a pasta granel/: produto sem código de barras (açougue, hortifruti, frios, padaria...).

Cada produto tem uma foto e uma ficha com o mesmo nome, dentro da pasta da categoria:
  granel/acougue/file-de-peito-resfriado.webp
  granel/acougue/file-de-peito-resfriado.txt

Uso: python3 ferramentas/conferir_granel.py
Sai com erro (código 1) se achar qualquer problema.
"""
import re
import sys
import unicodedata
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "granel"

CATEGORIAS = {"acougue", "aves", "peixaria", "hortifruti", "frios", "padaria", "outros"}
FORMATOS = {".png", ".jpg", ".jpeg", ".webp"}
PESO_MAX_KB = 1536
LADO_MIN = 800
LADO_MAX = 1500
CAMPOS = ["nome", "apelidos", "origem", "autorizacao", "enviado_por"]
OBRIGATORIOS = ["nome", "origem", "enviado_por"]
ORIGENS = {"propria", "ia", "industria", "site"}
A_CONFIRMAR = "a confirmar"
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def slug(texto: str) -> str:
    """Nome do produto → nome de arquivo: minúsculo, sem acento, com hífen."""
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def ler_ficha(arq: Path) -> dict:
    ficha = {}
    for linha in arq.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or ":" not in linha:
            continue
        campo, valor = linha.split(":", 1)
        ficha[campo.strip().lower()] = valor.strip()
    return ficha


def apelidos(ficha: dict) -> list:
    return [a.strip() for a in ficha.get("apelidos", "").split(";") if a.strip()]


def conferir_ficha(arq: Path, rel: Path) -> list:
    erros = []
    ficha = ler_ficha(arq)
    for campo in OBRIGATORIOS:
        if not ficha.get(campo):
            erros.append(f"{rel}: falta preencher '{campo}'")
    if ficha.get("nome") and slug(ficha["nome"]) != arq.stem:
        erros.append(f"{rel}: o nome do arquivo tem que ser '{slug(ficha['nome'])}' (vem do campo 'nome')")
    origem = ficha.get("origem", "").lower()
    if origem == A_CONFIRMAR:
        return erros
    if origem and origem not in ORIGENS:
        erros.append(f"{rel}: origem '{origem}' não vale, use propria, ia, industria ou site")
    elif origem in ("industria", "site") and not ficha.get("autorizacao"):
        erros.append(f"{rel}: foto de {origem} precisa dizer em 'autorizacao' quem autorizou")
    return erros


def main() -> int:
    if not PASTA.exists():
        print("Tudo certo: pasta granel/ ainda vazia.")
        return 0
    erros = []
    imagens, fichas = {}, {}
    nomes_usados = {}

    for arq in sorted(PASTA.rglob("*")):
        if arq.is_dir() or arq.name in (".gitkeep", "README.md"):
            continue
        rel = arq.relative_to(RAIZ)
        if arq.parent.parent != PASTA or arq.parent.name not in CATEGORIAS:
            erros.append(f"{rel}: tem que ficar direto numa destas pastas: {', '.join(sorted(CATEGORIAS))}")
            continue
        ext = arq.suffix.lower()
        if ext != ".txt" and ext not in FORMATOS:
            erros.append(f"{rel}: formato não aceito (use webp, png ou jpg)")
            continue
        if not SLUG.match(arq.stem):
            erros.append(f"{rel}: nome do arquivo só com letra minúscula sem acento, número e hífen")
            continue

        if ext == ".txt":
            fichas[arq.stem] = rel
            erros += conferir_ficha(arq, rel)
            ficha = ler_ficha(arq)
            for n in [ficha.get("nome", "")] + apelidos(ficha):
                s = slug(n)
                if s and s in nomes_usados and nomes_usados[s] != arq.stem:
                    erros.append(f"{rel}: o nome/apelido '{n}' já é usado por '{nomes_usados[s]}'")
                elif s:
                    nomes_usados[s] = arq.stem
            continue

        if arq.stem in imagens:
            erros.append(f"{rel}: já existe outra imagem para '{arq.stem}' ({imagens[arq.stem]})")
        imagens[arq.stem] = rel
        kb = arq.stat().st_size / 1024
        if kb > PESO_MAX_KB:
            erros.append(f"{rel}: {kb / 1024:.1f} MB, o máximo é 1,5 MB (em WEBP fica bem menor)")
        try:
            with Image.open(arq) as img:
                lado = max(img.size)
        except Exception:
            erros.append(f"{rel}: não consegui abrir a imagem")
            continue
        if not LADO_MIN <= lado <= LADO_MAX:
            erros.append(f"{rel}: lado maior tem {lado}px, tem que ficar entre {LADO_MIN} e {LADO_MAX}px")

    for s, rel in imagens.items():
        if s not in fichas:
            erros.append(f"{rel}: falta a ficha {s}.txt do lado da imagem")
    for s, rel in fichas.items():
        if s not in imagens:
            erros.append(f"{rel}: ficha sem imagem")

    if erros:
        print(f"{len(erros)} problema(s) no granel:")
        for e in erros:
            print(" -", e)
        return 1
    print(f"Tudo certo: {len(imagens)} imagem(ns) de granel.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
