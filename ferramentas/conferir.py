#!/usr/bin/env python3
"""Confere o acervo: código de barras válido, imagem no lugar certo,
tamanho dentro do padrão e cada imagem com a sua ficha (<ean>.txt) do lado.

Uso: python3 ferramentas/conferir.py
Sai com erro (código 1) se achar qualquer problema.
"""
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "imagens"

FORMATOS = {".png", ".jpg", ".jpeg", ".webp"}
PESO_MAX_KB = 1536
LADO_MIN = 800
LADO_MAX = 1500
CAMPOS = ["descricao", "marca", "conteudo", "origem", "autorizacao", "enviado_por"]
OBRIGATORIOS = ["descricao", "origem", "enviado_por"]
ORIGENS = {"propria", "industria", "site"}
# Aceito só durante o teste da ferramenta: entra, mas aparece como pendência.
A_CONFIRMAR = "a confirmar"


def ean_valido(codigo: str) -> bool:
    """GTIN-8, 12, 13 ou 14 com dígito verificador certo."""
    if not codigo.isdigit() or len(codigo) not in (8, 12, 13, 14):
        return False
    corpo, dv = codigo[:-1], int(codigo[-1])
    soma = sum(int(d) * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(corpo)))
    return (10 - soma % 10) % 10 == dv


def pasta_do(ean: str) -> str:
    return ean[:7]


def ler_ficha(arq: Path) -> dict:
    """Lê linhas 'campo: valor'. Ignora linha vazia e comentário (#)."""
    ficha = {}
    for linha in arq.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or ":" not in linha:
            continue
        campo, valor = linha.split(":", 1)
        ficha[campo.strip().lower()] = valor.strip()
    return ficha


def conferir_ficha(arq: Path, rel: Path) -> list:
    erros = []
    ficha = ler_ficha(arq)
    for campo in OBRIGATORIOS:
        if not ficha.get(campo):
            erros.append(f"{rel}: falta preencher '{campo}'")
    origem = ficha.get("origem", "").lower()
    if origem == A_CONFIRMAR:
        return erros
    if origem and origem not in ORIGENS:
        erros.append(f"{rel}: origem '{origem}' não vale, use propria, industria ou site")
    elif origem in ("industria", "site") and not ficha.get("autorizacao"):
        erros.append(f"{rel}: foto de {origem} precisa dizer em 'autorizacao' quem autorizou")
    return erros


def main() -> int:
    erros = []
    com_imagem, com_ficha = {}, set()

    for arq in sorted(PASTA.rglob("*")):
        if arq.is_dir() or arq.name == ".gitkeep":
            continue
        rel = arq.relative_to(RAIZ)
        ean, ext = arq.stem, arq.suffix.lower()

        if ext != ".txt" and ext not in FORMATOS:
            erros.append(f"{rel}: formato não aceito (use webp, png ou jpg)")
            continue
        if not ean_valido(ean):
            erros.append(f"{rel}: o nome do arquivo tem que ser o código de barras, e esse não é válido")
            continue
        if arq.parent != PASTA / pasta_do(ean):
            erros.append(f"{rel}: está na pasta errada, deveria estar em imagens/{pasta_do(ean)}/")

        if ext == ".txt":
            com_ficha.add(ean)
            erros += conferir_ficha(arq, rel)
            continue

        if ean in com_imagem:
            erros.append(f"{rel}: já existe outra imagem para {ean} ({com_imagem[ean]})")
        com_imagem[ean] = rel

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

    for ean, rel in com_imagem.items():
        if ean not in com_ficha:
            erros.append(f"{rel}: falta a ficha {ean}.txt do lado da imagem")
    for ean in com_ficha - com_imagem.keys():
        erros.append(f"imagens/{pasta_do(ean)}/{ean}.txt: ficha sem imagem")

    pendentes = sum(1 for f in PASTA.rglob("*.txt") if ler_ficha(f).get("origem", "").lower() == A_CONFIRMAR)
    if pendentes:
        print(f"Aviso: {pendentes} foto(s) com origem 'a confirmar'.")
    if erros:
        print(f"{len(erros)} problema(s):")
        for e in erros:
            print(" -", e)
        return 1
    print(f"Tudo certo: {len(com_imagem)} imagem(ns) no acervo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
