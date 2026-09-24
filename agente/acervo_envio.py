#!/usr/bin/env python3
"""Devolve ao acervo compartilhado as fotos novas — SÓ depois do OK do dono do mercado.

Com código de barras:
  preparar <EAN> <recorte.png> "<descricao>" "<marca>" "<conteudo>" <origem> ["<autorizacao>"]
  enviar <EAN> [<EAN> ...]        descartar <EAN> [<EAN> ...]
A granel (sem código de barras):
  preparar_granel <categoria> <recorte.png> "<nome>" "<apelido1; apelido2>" <origem> ["<autorizacao>"]
  enviar_granel <id> [<id> ...]   descartar_granel <id> [<id> ...]
Listar o que está esperando aprovação:
  listar

Rode a partir da pasta do agente de encarte (a que tem .claude/ e .venv/):
  .venv/bin/python .claude/skills/encarte-varejotech/scripts/acervo_envio.py <comando> ...
O nome do mercado vem de .acervo.json (criado pelo instalar.sh).
Quem é dono do acervo envia direto; os demais enviam por proposta (pull request), com o `gh`.
"""
import json
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[4]
CAND = RAIZ / 'acervo-candidatos'
CAND_G = CAND / 'granel'
ACERVO = Path.home() / 'Documents/acervo-encarte'
REPO = 'andrebitaraes-hub/acervo-encarte'
ORIGENS = {'propria', 'industria', 'site', 'a confirmar'}
ORIGENS_GRANEL = ORIGENS | {'ia'}
CATEGORIAS = {'acougue', 'aves', 'peixaria', 'hortifruti', 'frios', 'padaria', 'outros'}


def mercado():
    cfg = RAIZ / '.acervo.json'
    if not cfg.exists():
        sys.exit('Falta .acervo.json com o nome do mercado — rode o instalar.sh do acervo.')
    return json.loads(cfg.read_text())['mercado']


def git(*args, check=True, **kw):
    return subprocess.run(['git', '-C', str(ACERVO), *args], check=check, text=True, capture_output=True, **kw)


def gh():
    for c in (shutil.which('gh'), str(Path.home() / 'bin/gh'), '/opt/homebrew/bin/gh', '/usr/local/bin/gh'):
        if c and Path(c).exists():
            return c
    return None


def ean_valido(c):
    if not c.isdigit() or len(c) not in (8, 12, 13, 14):
        return False
    corpo, dv = c[:-1], int(c[-1])
    soma = sum(int(d) * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(corpo)))
    return (10 - soma % 10) % 10 == dv


def normaliza_ean(c):
    c = ''.join(ch for ch in c if ch.isdigit())
    if len(c) == 14 and c.startswith('0') and ean_valido(c[1:]):
        return c[1:]
    return c


def slug(t):
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


def padroniza(recorte, dest):
    im = Image.open(recorte).convert('RGBA')
    bbox = im.getchannel('A').getbbox()
    if bbox:
        im = im.crop(bbox)
    lado = max(im.size)
    alvo = min(max(lado, 800), 1500)
    if alvo != lado:
        k = alvo / lado
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    for q in (90, 80, 70, 60):
        im.save(dest, 'WEBP', quality=q, method=6)
        if dest.stat().st_size <= 1536 * 1024:
            break
    return im


def confere_origem(origem, validas, autorizacao):
    origem = origem.lower()
    if origem not in validas:
        sys.exit(f'origem deve ser uma de {sorted(validas)}')
    if origem in ('industria', 'site') and not autorizacao:
        sys.exit(f'origem "{origem}" precisa dizer quem autorizou')
    return origem


def preparar(ean, recorte, descricao, marca, conteudo, origem, autorizacao=''):
    ean = normaliza_ean(ean)
    if not ean_valido(ean) or (len(ean) == 13 and ean.startswith('2')):
        sys.exit(f'EAN inválido ou código interno de balança: {ean} (use preparar_granel)')
    origem = confere_origem(origem, ORIGENS, autorizacao)
    dest = CAND / f'{ean}.webp'
    im = padroniza(recorte, dest)
    dest.with_suffix('.txt').write_text(
        f'descricao: {descricao}\nmarca: {marca}\nconteudo: {conteudo}\norigem: {origem}\n'
        f'autorizacao: {autorizacao}\nenviado_por: {mercado()}\n', encoding='utf-8')
    print(f'CANDIDATA {dest} | {im.width}x{im.height} | {dest.stat().st_size // 1024} KB')


def preparar_granel(categoria, recorte, nome, apelidos, origem, autorizacao=''):
    if categoria not in CATEGORIAS:
        sys.exit(f'categoria deve ser uma de {sorted(CATEGORIAS)}')
    origem = confere_origem(origem, ORIGENS_GRANEL, autorizacao)
    dest = CAND_G / categoria / f'{slug(nome)}.webp'
    im = padroniza(recorte, dest)
    dest.with_suffix('.txt').write_text(
        f'nome: {nome}\napelidos: {apelidos}\norigem: {origem}\n'
        + (f'autorizacao: {autorizacao}\n' if autorizacao else '') + f'enviado_por: {mercado()}\n', encoding='utf-8')
    print(f'CANDIDATA {dest} | {im.width}x{im.height} | {dest.stat().st_size // 1024} KB')


def listar():
    for f in sorted(CAND.glob('*.webp')):
        print(f'{f.stem} | {f.with_suffix(".txt").read_text(encoding="utf-8").splitlines()[0].split(":", 1)[1].strip()} | {f}')
    for f in sorted(CAND_G.glob('*/*.webp')):
        print(f'granel:{f.stem} | {f.with_suffix(".txt").read_text(encoding="utf-8").splitlines()[0].split(":", 1)[1].strip()} | {f}')


def publica(novos, conferidor, msg):
    """Confere, salva a versão e sobe: direto se tiver permissão, senão por proposta."""
    r = subprocess.run([sys.executable, f'ferramentas/{conferidor}'], cwd=ACERVO, capture_output=True, text=True)
    print(r.stdout.strip()[-600:])
    if r.returncode != 0:
        for f in novos:
            f.unlink()
        sys.exit(f'{conferidor} reprovou — nada foi enviado. Corrija e tente de novo.')
    rels = [str(f.relative_to(ACERVO)) for f in novos]
    git('add', *rels)
    git('commit', '-q', '-m', msg)
    git('pull', '-q', '--rebase', 'origin', 'main')
    if git('push', '-q', 'origin', 'HEAD:main', check=False).returncode == 0:
        print('Enviado direto para o acervo.')
        return
    g = gh()
    if not g:
        git('reset', '-q', '--hard', 'origin/main')
        sys.exit('Sem permissão para enviar direto e o `gh` não está instalado. Instale o GitHub CLI '
                 '(https://cli.github.com), rode `gh auth login` e tente de novo.')
    subprocess.run([g, 'auth', 'setup-git'], capture_output=True, text=True)
    ramo = f'{slug(mercado())}-{time.strftime("%Y%m%d-%H%M%S")}'
    subprocess.run([g, 'repo', 'fork', REPO, '--remote', '--remote-name', 'meu', '--clone=false'],
                   cwd=ACERVO, capture_output=True, text=True)
    if git('remote', 'get-url', 'meu', check=False).returncode != 0:
        login = subprocess.run([g, 'api', 'user', '-q', '.login'], capture_output=True, text=True).stdout.strip()
        git('remote', 'add', 'meu', f'https://github.com/{login}/acervo-encarte.git')
    git('push', '-q', 'meu', f'HEAD:refs/heads/{ramo}')
    login = subprocess.run([g, 'api', 'user', '-q', '.login'], capture_output=True, text=True).stdout.strip()
    pr = subprocess.run([g, 'pr', 'create', '-R', REPO, '--head', f'{login}:{ramo}', '--base', 'main',
                         '--title', msg, '--body', f'Enviado pelo agente de encarte de {mercado()}.'],
                        capture_output=True, text=True)
    git('reset', '-q', '--hard', 'origin/main')
    print(pr.stdout.strip() or pr.stderr.strip())
    print('Proposta aberta: entra sozinha se a sua conta estiver na lista de confiança; senão, espera aprovação.')


def enviar(eans):
    git('pull', '-q', '--rebase')
    novos = []
    for e in map(normaliza_ean, eans):
        img = CAND / f'{e}.webp'
        if not img.exists():
            print(f'[PULEI] {e}: não há candidata preparada')
            continue
        pasta = ACERVO / 'imagens' / e[:7]
        if any((pasta / f'{e}.{x}').exists() for x in ('webp', 'png', 'jpg')):
            print(f'[PULEI] {e}: já existe no acervo')
            continue
        pasta.mkdir(parents=True, exist_ok=True)
        shutil.copy(img, pasta / img.name)
        shutil.copy(img.with_suffix('.txt'), pasta / f'{e}.txt')
        novos += [pasta / img.name, pasta / f'{e}.txt']
    if not novos:
        print('Nada para enviar.')
        return
    n = len(novos) // 2
    publica(novos, 'conferir.py', f'{mercado()}: {n} foto(s) nova(s)')
    for f in novos:
        if f.suffix == '.webp':
            for x in ('webp', 'txt'):
                (CAND / f'{f.stem}.{x}').unlink(missing_ok=True)


def enviar_granel(ids):
    git('pull', '-q', '--rebase')
    novos = []
    for i in ids:
        img = next(CAND_G.glob(f'*/{i}.webp'), None)
        if not img:
            print(f'[PULEI] {i}: não há candidata preparada')
            continue
        pasta = ACERVO / 'granel' / img.parent.name
        if any(pasta.glob(f'{i}.*')):
            print(f'[PULEI] {i}: já existe no acervo')
            continue
        pasta.mkdir(parents=True, exist_ok=True)
        shutil.copy(img, pasta / img.name)
        shutil.copy(img.with_suffix('.txt'), pasta / f'{i}.txt')
        novos += [pasta / img.name, pasta / f'{i}.txt']
    if not novos:
        print('Nada para enviar.')
        return
    n = len(novos) // 2
    publica(novos, 'conferir_granel.py', f'{mercado()}: {n} foto(s) de granel')
    for f in novos:
        if f.suffix == '.webp':
            for c in CAND_G.glob(f'*/{f.stem}.*'):
                c.unlink()


def descartar(eans):
    for e in map(normaliza_ean, eans):
        for x in ('webp', 'txt'):
            (CAND / f'{e}.{x}').unlink(missing_ok=True)
        print(f'DESCARTADA {e}')


def descartar_granel(ids):
    for i in ids:
        for c in CAND_G.glob(f'*/{i}.*'):
            c.unlink()
        print(f'DESCARTADA {i}')


if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    {'preparar': lambda: preparar(*args), 'preparar_granel': lambda: preparar_granel(*args),
     'enviar': lambda: enviar(args), 'enviar_granel': lambda: enviar_granel(args),
     'descartar': lambda: descartar(args), 'descartar_granel': lambda: descartar_granel(args),
     'listar': listar}[cmd]()
