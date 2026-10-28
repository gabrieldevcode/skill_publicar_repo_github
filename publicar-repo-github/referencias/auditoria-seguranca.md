# Auditoria de segurança antes de publicar

Referência da Fase 1 da skill `publicar-repo-github`.

Premissa: **o que entra no histórico do git é permanente.** `git rm` apaga o
arquivo do próximo commit, não dos anteriores. Uma vez publicado, considere
copiado — GitHub indexa, bots clonam, forks preservam. Por isso a auditoria
acontece antes do primeiro commit, e não antes do push.

---

## O script

```bash
python ~/.claude/skills/publicar-repo-github/referencias/auditar.py .
python ~/.claude/skills/publicar-repo-github/referencias/auditar.py . --extra=28224647,servidor-interno.local
```

Sai com código 1 se achar algo. `--extra` recebe strings literais adicionais
que você sabe que são sensíveis mas não estão no `.env` (conta bancária, nome
de servidor, ID de cliente).

O script é melhor que um scanner genérico num ponto: scanners adivinham por
regex o que *parece* segredo; este **lê o `.env` real e as bases de dados
reais do projeto** e procura exatamente aqueles valores. Menos falso positivo,
e pega o que regex nenhuma pegaria (o nome de um cliente, um CNPJ específico).

Se `gitleaks` ou `trufflehog` estiverem instalados, rodar como segunda camada:

```bash
gitleaks detect --source . --log-opts="--all"
trufflehog git file://. --json
```

---

## Categorias

| Categoria | O que procurar |
|---|---|
| Credenciais | `.env`, token, client secret, senha, string de conexão, `Authorization:` fixo |
| Criptografia | `*.key`, `*.pem`, `*.crt`, `*.pfx`, `*.p12`, `id_rsa`, keystore |
| Dados pessoais | CPF, CNPJ, RG, nome, e-mail, telefone, endereço, data de nascimento |
| Financeiro | conta, agência, cartão, valores reais faturados, folha |
| Bases reais | `*.xlsx`, `*.csv`, dump SQL, export de CRM, backup |
| Saídas com dado real | PDF emitido, relatório, nota, log de execução, ledger |
| Interno da empresa | URL interna, IP, hostname, nome de projeto confidencial |
| Ambiente pessoal | `C:\Users\<nome>`, `/home/<nome>`, nome de máquina |

---

## As três armadilhas recorrentes

### 1. Default embutido no código

O `.env` está ignorado, mas o código faz:

```python
CONTA = os.getenv("CONTA_CORRENTE", "28224647")   # ← o valor real vaza aqui
```

Onde isso se esconde: default de `getenv`/`process.env`, constantes no topo,
**scripts legados que ninguém revisou** (o `main.py` antigo, o `deploy.sh`).

Busca:

```bash
grep -rnoE "[0-9]{8,}" --include=*.py --include=*.js --include=*.ts . | grep -v node_modules
grep -rnE "getenv\([^)]+,\s*[\"'][^\"']+[\"']\)" --include=*.py .
grep -rnE "process\.env\.[A-Z_]+\s*\|\|\s*[\"'][^\"']+" --include=*.js --include=*.ts .
```

Correção: tirar o default. O segredo vem só do ambiente, e o programa **checa
na subida** e avisa se faltar — nunca falha no meio de uma operação:

```python
def checar_credenciais():
    faltando = []
    if not CLIENT_ID:  faltando.append("CLIENT_ID ausente no .env")
    if not os.path.exists(CERT_FILE): faltando.append(f"certificado: {CERT_FILE}")
    return faltando
```

### 2. Config com dado real que não estava ignorado

Um `config.json` de regras de negócio com o CPF e o nome de um cliente numa
exceção. Ninguém pensa nele como "dado sensível" — ele é "configuração".

Correção, o padrão dos três arquivos:

```
config.json           → ignorado (o real, com dado de verdade)
config.example.json   → versionado, dados inventados
código                → se o real não existe, copia do exemplo na 1ª execução
```

```python
if not os.path.exists(ARQ) and os.path.exists(ARQ_EXEMPLO):
    shutil.copyfile(ARQ_EXEMPLO, ARQ)
```

### 3. `#` no início de linha do `.gitignore` é comentário

Um arquivo `###notas.txt` **não** é ignorado pela linha `###notas.txt` — ela é
lida como comentário. Precisa escapar a primeira `#`:

```gitignore
\###notas.txt
```

Mesma família de pegadinha: `!` no início precisa de `\!`, espaço no fim precisa
de `\ `. **Sempre conferir com `git add -A -n`**, nunca confiar na leitura.

---

## `.gitignore` de partida

Agressivo de propósito: bloqueia por extensão além de por caminho, para nada
real entrar por acidente meses depois.

```gitignore
# Segredos
.env
.env.local
.env.*.local
certs/
*.key
*.pem
*.crt
*.pfx
*.p12

# Dados reais (os *.exemplo.* / *.example.* ficam)
dados/*
!dados/*.exemplo.json
config.json

# Entradas e saídas com dado real
entrada/
saida/
execucoes/
*.xlsx
*.xls
*.csv
*.pdf
*.sqlite
*.db

# Lixo local
__pycache__/
*.py[cod]
node_modules/
.venv/
venv/
dist/
build/
.idea/
.vscode/
*.log
~$*
```

Ajustar aos nomes reais do projeto — mas manter os bloqueios por extensão.

---

## Se um segredo já está no histórico

Nesta ordem. Inverter não adianta.

**1. Rotacionar a credencial.** Um segredo que chegou a um repositório público
está comprometido, mesmo que ninguém tenha aberto. Gerar nova, revogar a
antiga, atualizar onde é usada. **Isto é decisão do usuário** — avisar e
esperar, não sair revogando.

**2. Limpar o histórico.**

```bash
pip install git-filter-repo

# substituir o valor em todos os commits
echo "valor-do-segredo==>REMOVIDO" > /tmp/troca.txt
git filter-repo --replace-text /tmp/troca.txt

# ou remover o arquivo inteiro de toda a história
git filter-repo --path caminho/do/arquivo --invert-paths
```

`git-filter-repo` é o substituto recomendado do BFG e do `filter-branch`.
Para o caso simples de tirar um trailer de mensagem, `filter-branch --msg-filter`
resolve sem instalar nada.

**3. Force-push e avisar quem tiver clone.**

```bash
git push --force-with-lease origin main
```

Comando destrutivo — pode ser bloqueado por permissão. Se for, **entregar o
comando ao usuário**, não contornar.

**4. Verificar do lado do GitHub**, lendo de volta:

```bash
gh api repos/<user>/<repo>/commits -q '.[].commit.message'
gh api repos/<user>/<repo>/git/trees/main?recursive=1 -q '.tree[].path'
```

> Atenção: commits antigos podem continuar acessíveis por SHA direto e em
> forks. Por isso a rotação da credencial é o passo 1, não o 3.

---

## Verificação final

```bash
# 1. o que exatamente iria para o git
git add -A -n | sed "s/^add //" | tr -d "'" | sort

# 2. auditoria completa (working tree + histórico)
python ~/.claude/skills/publicar-repo-github/referencias/auditar.py .

# 3. depois do push: conferir o que CHEGOU, não o que foi enviado
gh api repos/<user>/<repo>/git/trees/main?recursive=1 -q '.tree[] | select(.type=="blob") | .path' | sort
```

A lista do passo 3 tem que ser idêntica à do passo 1.

---

## Fontes consultadas

- [How to detect and clean up leaked secrets in your Git repositories — BlakYaks](https://www.blakyaks.com/resources/how-to-detect-and-clean-up-leaked-secrets-in-your-git-repositories)
- [Secrets Scanning with Gitleaks, TruffleHog, and GitHub (2026)](https://www.decryptiondigest.com/blog/secrets-scanning-pre-commit-ci-enforcement)
- [BFG & git-filter-repo: Cleaning Leaked Secrets from History](https://www.elegantsoftwaresolutions.com/blog/bfg-git-filter-repo-cleaning-leaked-secrets-from-history)
- [GitHub Community — How can I prevent secrets from being exposed in a public repository?](https://github.com/orgs/community/discussions/187601)
