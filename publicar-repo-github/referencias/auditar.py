# -*- coding: utf-8 -*-
"""
Auditoria de segredos e dados sensiveis antes de publicar um repositorio.

    python auditar.py                          # repo do diretorio atual
    python auditar.py /caminho/repo
    python auditar.py --extra=28224647,acme-interno.local

O que faz, em ordem:

  1. Lista exatamente os arquivos que entrariam no git (respeitando .gitignore).
  2. Deriva a lista de segredos do .env REAL do projeto e procura cada valor
     nos arquivos versionaveis e no historico inteiro.
  3. Deriva CPF/CNPJ e nomes das bases de dados reais (JSON/CSV ignorados pelo
     git) e procura no repositorio.
  4. Procura padroes genericos: chave privada, token, senha, caminho pessoal,
     sequencias longas de digitos (conta bancaria, documento).
  5. Repete tudo sobre `git log -p --all` — o historico e onde segredo se
     esconde depois que alguem "apagou" o arquivo.

Sai com codigo 1 se achar qualquer coisa. Nao corrige nada: so aponta.

Vantagem sobre gitleaks/trufflehog: estes adivinham por regex o que parece
segredo. Este script SABE quais sao os segredos deste projeto, porque le o
.env e as bases reais. Use os dois quando estiverem disponiveis.
"""
import io
import json
import os
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# Padroes genericos
# ---------------------------------------------------------------------------
PADROES = [
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "chave privada"),
    (r"-----BEGIN CERTIFICATE-----", "certificado"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key"),
    (r"\bgh[pousr]_[A-Za-z0-9]{20,}", "token do GitHub"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{10,}", "token do Slack"),
    (r"\bsk-[A-Za-z0-9]{20,}", "chave de API estilo OpenAI"),
    (r"\bey[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "JWT"),
    (r"(?i)\b(senha|password|passwd|secret|api[_-]?key)\s*[:=]\s*[\"'][^\"'\s]{6,}", "segredo literal"),
    (r"(?i)(mongodb|postgres|postgresql|mysql|redis)://[^/\s:]+:[^@\s]+@", "string de conexão com senha"),
    (r"C:\\\\Users\\\\[A-Za-z]", "caminho pessoal do Windows"),
    (r"/(?:home|Users)/[a-z][a-z0-9._-]{2,}/", "caminho pessoal do Unix"),
]

# Arquivos cujo conteudo e a FONTE dos dados sensiveis (nao devem estar no git;
# sao lidos so para saber o que procurar no que vai para o git).
FONTES_SEGREDO = [".env", ".env.local", ".env.production"]
EXT_BASES = (".json", ".csv")


def sh(*args, cwd=None):
    r = subprocess.run(args, capture_output=True, text=True,
                       encoding="utf-8", errors="ignore", cwd=cwd)
    return r.stdout or ""


def arquivos_versionaveis(repo):
    """
    Lista tudo que estaria no git: o ja rastreado (`git ls-files`) MAIS o que
    `git add -A` incluiria agora (`-n` = simulacao, nao commita nada).

    A uniao importa: com um arquivo novo pendente, `git add -A -n` lista SO
    esse arquivo. Usar so ele faria os arquivos de exemplo ja commitados serem
    confundidos com base de dados real, gerando alarme falso.
    """
    caminhos = {l.strip() for l in sh("git", "ls-files", cwd=repo).splitlines() if l.strip()}
    for linha in sh("git", "add", "-A", "-n", cwd=repo).splitlines():
        if linha.startswith("add "):
            caminhos.add(linha[4:].strip().strip("'").strip('"'))
    return sorted(caminhos)


def ler(caminho):
    try:
        return io.open(caminho, encoding="utf-8", errors="ignore").read()
    except Exception:
        return ""


def segredos_do_env(repo):
    """Valores do .env real que nao podem aparecer em lugar nenhum."""
    segredos = {}
    for nome in FONTES_SEGREDO:
        p = os.path.join(repo, nome)
        if not os.path.exists(p):
            continue
        for linha in ler(p).splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            k, v = linha.split("=", 1)
            v = v.strip().strip('"').strip("'")
            # valores curtos ou obviamente placeholder nao interessam
            if len(v) >= 8 and not re.fullmatch(r"[0Xx*\-\.]+", v):
                segredos[k.strip()] = v
    return segredos


def dados_reais(repo, versionaveis):
    """
    Documentos e nomes vindos de bases IGNORADAS pelo git — sao exatamente os
    dados que nao podem ter vazado para os arquivos que vao ser publicados.
    """
    docs, nomes = set(), set()
    versionaveis = {v.replace("\\", "/") for v in versionaveis}
    for raiz, dirs, arqs in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in
                   (".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build")]
        for a in arqs:
            if not a.endswith(EXT_BASES):
                continue
            full = os.path.join(raiz, a)
            rel = os.path.relpath(full, repo).replace("\\", "/")
            if rel in versionaveis:      # arquivo publicavel: nao e fonte
                continue
            txt = ler(full)
            if len(txt) > 8_000_000:
                continue
            try:
                dados = json.loads(txt)
            except Exception:
                continue
            for item in (dados if isinstance(dados, list) else [dados]):
                if not isinstance(item, dict):
                    continue
                for chave, valor in item.items():
                    if not isinstance(valor, str):
                        continue
                    ck = chave.lower()
                    if any(t in ck for t in ("cpf", "cnpj", "documento", "doc")):
                        d = re.sub(r"\D", "", valor)
                        if len(d) in (11, 14):
                            docs.add(d)
                    elif ck in ("nome", "name", "razaosocial", "razao_social"):
                        n = valor.strip().upper()
                        if len(n) > 12:
                            nomes.add(n)
    return docs, nomes


def auditar_texto(rotulo, texto, segredos, docs, nomes):
    achados = []
    for k, v in segredos.items():
        if v in texto:
            achados.append(f"[{rotulo}] valor de {k} (.env) presente")
    if docs:
        digitos = re.sub(r"\D", "", texto)
        for d in docs:
            if d in digitos:
                achados.append(f"[{rotulo}] documento real {d[:5]}… presente")
    up = texto.upper()
    for n in nomes:
        if n in up:
            achados.append(f"[{rotulo}] nome real '{n}' presente")
    for padrao, desc in PADROES:
        m = re.search(padrao, texto)
        if m:
            trecho = m.group(0)[:40].replace("\n", " ")
            achados.append(f"[{rotulo}] {desc}: {trecho}…")
    return achados


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    extras = []
    for a in sys.argv[1:]:
        if a.startswith("--extra="):
            extras = [x for x in a.split("=", 1)[1].split(",") if x.strip()]
    repo = os.path.abspath(args[0] if args else ".")
    if not os.path.isdir(os.path.join(repo, ".git")):
        print(f"! {repo} nao e um repositorio git (rode `git init` antes)")
        return 2

    versionaveis = arquivos_versionaveis(repo)
    segredos = segredos_do_env(repo)
    # strings passadas em --extra=a,b,c entram como se fossem segredos do .env
    # (conta bancaria embutida no codigo, nome de servidor interno, etc.)
    for i, e in enumerate(extras, 1):
        segredos[f"--extra[{i}]={e}"] = e.strip()
    docs, nomes = dados_reais(repo, versionaveis)

    print("=" * 72)
    print("AUDITORIA DE PUBLICACAO")
    print("=" * 72)
    print(f"repositorio            : {repo}")
    print(f"arquivos que iriam pro git: {len(versionaveis)}")
    print(f"segredos conhecidos (.env): {len(segredos)}")
    print(f"documentos reais na base  : {len(docs)}")
    print(f"nomes reais na base       : {len(nomes)}")
    print()
    print("-- arquivos que seriam publicados " + "-" * 38)
    for v in sorted(versionaveis):
        print(f"   {v}")
    print()

    achados = []

    # working tree
    for rel in versionaveis:
        full = os.path.join(repo, rel)
        if not os.path.isfile(full):
            continue
        achados += auditar_texto(rel, ler(full), segredos, docs, nomes)

    # historico completo
    hist = sh("git", "log", "-p", "--all", cwd=repo)
    if hist:
        achados += auditar_texto("HISTORICO", hist, segredos, docs, nomes)

    # sequencias longas de digitos: revisao manual
    print("-- sequencias de 8+ digitos (revisar uma a uma) " + "-" * 24)
    vistos = set()
    for rel in sorted(versionaveis):
        full = os.path.join(repo, rel)
        if not os.path.isfile(full):
            continue
        for m in re.finditer(r"\b\d{8,}\b", ler(full)):
            chave = (rel, m.group(0))
            if chave not in vistos:
                vistos.add(chave)
                print(f"   {rel}: {m.group(0)}")
    if not vistos:
        print("   (nenhuma)")
    print()

    print("=" * 72)
    if achados:
        print("*** NAO PUBLICAR — achados abaixo ***")
        for a in sorted(set(achados)):
            print("  !", a)
        print()
        print("Se algo ja esta no historico: ROTACIONE a credencial primeiro,")
        print("depois limpe com git filter-repo. `git rm` nao resolve.")
        return 1

    print("OK — nada encontrado.")
    print("  sem credenciais, sem documentos ou nomes reais,")
    print("  sem material criptografico e sem caminho pessoal,")
    print("  no working tree e no historico completo.")
    print()
    print("Confira ainda assim a lista de arquivos e os digitos acima.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
