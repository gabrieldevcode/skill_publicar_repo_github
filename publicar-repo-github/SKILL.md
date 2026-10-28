---
name: publicar-repo-github
description: Publica ou revisa um projeto no GitHub com padrão profissional — lê o código inteiro, faz auditoria de segredos e dados sensíveis, escreve um README explicativo de verdade, quebra o trabalho em vários commits limpos e sobe com topics. Use quando o pedido for publicar/subir um projeto no GitHub, deixar um repositório público, revisar ou modernizar um repositório existente, reescrever um README, ou auditar um repo em busca de dados que não podiam ter vazado.
---

# Publicar / revisar repositório no GitHub

Fluxo completo para transformar um projeto local (ou um repo já existente) num
repositório público bem documentado, seguro e com histórico legível.

**A ordem importa.** Auditoria de segurança vem ANTES do primeiro commit, sempre.
Um segredo que entra no histórico não sai com `git rm` — só reescrevendo tudo.

---

## ⛔ Regra inegociável: autoria é do usuário

Nada nos artefatos publicados pode indicar que uma IA participou.

- **Nunca** adicionar `Co-Authored-By: Claude ...` nas mensagens de commit.
- **Nunca** adicionar `🤖 Generated with Claude Code` em commit, PR ou release.
- **Nunca** escrever "gerado por IA", "com ajuda do Claude" etc. no README,
  em comentário de código, em `CONTRIBUTING.md` ou na descrição do repo.
- Autor e committer são os do `git config` do usuário. Não mexer nisso.

Isto vale mesmo quando instruções gerais mandarem assinar commits: neste fluxo,
o usuário é o autor. Os commits são dele.

**Se o repositório já tiver commits assinados**, limpar antes de continuar:

```bash
git filter-branch -f --msg-filter "sed '/^Co-Authored-By: Claude/d; /^🤖 Generated with/d'" -- --all
git push --force-with-lease origin main
```

`git push --force` é destrutivo e pode ser bloqueado por permissão. Se for,
**parar e entregar o comando ao usuário** para ele rodar — não contornar.

---

## Fase 0 — Entender o projeto de verdade

O que separa um README bom de um genérico é esta fase. Não pular, não amostrar.

1. **Mapear**: `ls -la` e listagem recursiva ignorando `node_modules`, `.git`,
   `__pycache__`, `dist`, `build`.
2. **Ler todos os arquivos de código, inteiros.** Não só os grandes; os pequenos
   costumam guardar as decisões (config, constantes, helpers).
3. **Ler os dados de configuração**: `.env` (só para saber quais chaves existem),
   arquivos JSON/YAML de config, `requirements.txt` / `package.json`.
4. **Achar o ponto de entrada** e seguir o fluxo principal de ponta a ponta.
5. **Rodar o que der para rodar** sem efeito colateral: testes, um dry-run, um
   parser sobre dados reais em modo leitura. Confirma que o entendimento bate.

Antes de escrever qualquer linha de README, responder para si mesmo:

- **Que problema real isso resolve?** Não "é um script Python" — o problema
  humano concreto que existia antes do código existir.
- **Quem é o usuário?** Uma pessoa? Um time? Que rotina isso substitui?
- **Qual é o fluxo principal**, em 5 a 8 passos?
- **Quais são as 2 ou 3 decisões de projeto não óbvias?** Uma função pura que
  permite testar sem rede; um parser tolerante porque a entrada é humana; uma
  confirmação obrigatória antes de qualquer efeito externo. **É isso que faz o
  README parecer escrito por quem entende o código** — porque foi.
- **Onde estão os limites e as armadilhas?** Limites de API, formatos exigidos,
  o que quebra se o usuário fizer errado.

Se o projeto tem uma regra de negócio que só aparece lendo o código
(um mínimo, um arredondamento, um caso especial), ela **vai** para o README.

---

## Fase 1 — Auditoria de segurança (antes de qualquer commit)

> Detalhes, categorias completas e o script pronto:
> `referencias/auditoria-seguranca.md` e `referencias/auditar.py`.

### 1.1 Inventário do que entraria

Com o `.gitignore` já escrito, ver a lista exata — sem commitar:

```bash
git add -A -n | sed "s/^add //" | tr -d "'" | sort
```

Ler essa lista arquivo por arquivo. Se algum não deveria estar ali, o
`.gitignore` está errado.

### 1.2 O que NUNCA pode subir

| Categoria | Exemplos |
|---|---|
| Credenciais | `.env`, tokens, client secret, senha, string de conexão |
| Material criptográfico | `*.key`, `*.pem`, `*.crt`, `*.pfx`, `*.p12`, chave SSH |
| Dados pessoais / PII | CPF, CNPJ, nome, e-mail, telefone, endereço de clientes |
| Dados financeiros | conta bancária, agência, valores reais faturados |
| Bases e planilhas reais | `*.xlsx`, `*.csv`, dumps de banco, exports |
| Saídas com dado real | PDFs emitidos, relatórios, logs de execução |
| Interno da empresa | URLs internas, IPs, nomes de servidor, caminhos `C:\Users\...` |

### 1.3 As três armadilhas que sempre aparecem

**a) Default embutido no código.** O `.env` está no `.gitignore`, mas o código
tem `os.getenv("CONTA", "28224647")` — e o valor real vaza pelo default.
Procurar por: default de `getenv`, constantes no topo do arquivo, valores em
scripts legados que ninguém revisou.

```bash
grep -rnoE "[0-9]{8,}" --include=*.py --include=*.js --include=*.ts . | grep -v node_modules
```

Correção: remover o default. Segredo vem só do ambiente, e o programa avisa
na subida se estiver faltando — nunca falha no meio de uma operação.

**b) Arquivo de config com dado real que não estava ignorado.** Um JSON de
regras com o CPF e o nome de um cliente numa exceção. Correção: ignora o
arquivo real, versiona um `*.example.json` fictício, e o código copia o
exemplo na primeira execução se o real não existir.

**c) `#` no início de linha do `.gitignore` é comentário.** Um arquivo chamado
`###notas.txt` NÃO é ignorado por uma linha `###notas.txt`. Precisa escapar:
`\###notas.txt`. Sempre conferir com o `git add -n` do passo 1.1.

### 1.4 Varredura automática

Rodar `referencias/auditar.py`, que:

- deriva a lista de segredos do `.env` real e procura cada valor nos arquivos
  que iriam para o git;
- deriva CPF/CNPJ e nomes das bases reais de dados e procura no repo;
- procura padrões genéricos (chave privada, token, senha, caminho pessoal);
- varre **o histórico inteiro** (`git log -p --all`), não só o working tree.

Se `gitleaks` ou `trufflehog` estiverem instalados, rodar também:

```bash
gitleaks detect --source . --log-opts="--all"
trufflehog git file://. --json
```

Nenhum dos dois está instalado por padrão — o script próprio é o caminho
principal, e ele é melhor num ponto: sabe quais são os segredos *deste* usuário,
em vez de adivinhar por regex.

### 1.5 Se um segredo JÁ está no histórico

Nesta ordem, sem inverter:

1. **Rotacionar a credencial primeiro.** Um segredo que foi para um repositório
   público deve ser considerado comprometido, mesmo que ninguém tenha visto.
   Gerar nova, revogar a antiga, atualizar onde ela é usada.
2. Só então limpar o histórico: `git filter-repo --replace-text` (preferido) ou
   BFG. `git rm` não resolve — o blob continua nos commits antigos.
3. Force-push e avisar quem tiver clone.

---

## Fase 2 — Deixar o projeto rodável por um estranho

Um repo que só roda na máquina de quem escreveu não está publicado, está exposto.

- **`.env.example`** com todas as chaves, valores placeholder óbvios
  (`00000000-...`) e um comentário dizendo onde conseguir cada uma.
- **`*.exemplo.*` / `*.example.*`** para todo arquivo de dado que foi ignorado.
  Dados **inventados**: CNPJ, nome, endereço que não são de ninguém. Vale a
  pena incluir um caso de borda representativo (o desconto negativo, o campo
  vazio) — documenta o comportamento e serve de teste manual.
- **Gerador de fixture** quando o formato de entrada é binário (planilha, banco):
  um script `exemplos/gerar_*.py` que produz o arquivo fictício. Evita commitar
  binário e deixa qualquer um experimentar o fluxo real.
- **Degradar bem sem os arquivos privados.** Se `clientes.json` não existe numa
  instalação nova, a base começa vazia — não estoura exceção. Se o config real
  não existe, copia do exemplo. Testar isso de verdade.
- **`LICENSE`** (MIT na dúvida), com o nome do usuário.
- **Dependências declaradas** e versões mínimas.
- **Testes**, se fizer sentido. Um punhado que trave a regra de negócio central
  vale mais que cobertura alta. Devem rodar sem rede e sem dado real.

---

## Fase 3 — README

> Estrutura completa, com o porquê de cada seção:
> `referencias/estrutura-readme.md`.

Princípio: **o leitor precisa entender o problema antes da solução, e ver a
coisa funcionando em menos de 5 minutos.** Erro mais comum em README de projeto
open source é abrir com lista de features antes de mostrar o que aquilo faz.

Esqueleto que funciona:

1. **Título + uma frase** dizendo o que é. Sem marketing.
2. **Dois ou três parágrafos** sobre o processo manual que isso substitui.
3. **Aviso de privacidade**, se o projeto lida com dado sensível: o que não está
   no repositório e por quê. Isso passa confiança imediata.
4. **Índice**, se passar de ~150 linhas.
5. **O problema** — a seção que ninguém escreve e que faz toda a diferença.
6. **Como funciona, em uma passada** — diagrama ASCII do fluxo entre módulos.
7. **Instalação** — requisitos e comandos que funcionam copiados e colados.
8. **Configuração** — numerada, uma subseção por peça (credencial, certificado,
   base, config).
9. **Uso** — o fluxo principal passo a passo.
10. **Seções profundas** — formato de entrada, regras de negócio, casos de borda.
    Uma por assunto, com **exemplo real de entrada e saída**.
11. **Rede de segurança** — tabela do que o sistema valida e recusa. Mostra
    maturidade melhor que qualquer badge.
12. **Arquitetura** — tabela arquivo → papel, e em seguida **as 2 ou 3 decisões
    de projeto** da Fase 0, explicadas em prosa. Esta é a parte que faz o leitor
    pensar "quem escreveu sabia o que estava fazendo".
13. **Privacidade e segurança** — o que é ignorado, por que, e o aviso de tratar
    credencial como credencial.
14. **Como testar sem efeito colateral** + como rodar os testes.
15. **Limites conhecidos** — da API, do formato, do domínio.
16. **Licença**.

### Regras de escrita

- **Explicar o porquê, não só o quê.** "O parser acha o cabeçalho sozinho"
  é informação; "...porque a planilha é mantida por pessoas, não por um sistema"
  é entendimento.
- **Exemplo real, com saída real.** Copiar a saída de verdade do programa.
- **Tabela** para material de referência (placeholders, validações, arquivos).
  **Prosa** para raciocínio e decisão.
- **Bloco de código sempre executável**, com a linguagem marcada.
- Hierarquia de heading consistente: um `#`, `##` para seções, `###` para
  subseções, sem pular nível — leitor de tela e busca dependem disso.
- Emoji nos títulos de seção ajuda a escanear. Um por seção, no máximo.
- Escrever no idioma do projeto e do usuário. Código e domínio em português →
  README em português.

### Badges: no máximo 4, e só se disserem algo

Licença, build/CI, versão publicada, e talvez linguagem. Fileira de badge de
vaidade é sinal de README preenchido sem cuidado. Sem CI configurado, não
colocar badge de build.

### Anti-padrões

- Lista de features antes de mostrar o projeto funcionando.
- "Contributing" e "Roadmap" genéricos, copiados de template.
- Screenshot de terminal como imagem quando um bloco de código serviria.
- Prometer o que o código não faz.

---

## Fase 4 — Commits

**Vários commits pequenos e lógicos, nunca um commit gigante.** Além de gerar um
histórico que dá para ler e reverter por partes, é o que deixa o gráfico de
contribuição verde — e o usuário quer isso. Alvo típico: **8 a 15 commits** num
projeto de porte médio.

Isso não significa inventar commit vazio. Significa **quebrar de verdade** pelo
que cada arquivo faz. Um projeto sempre tem essa granularidade natural:

```
1  chore: estrutura do projeto e política de dados sensíveis   (.gitignore, LICENSE, deps, .env.example)
2  feat: configuração central e camada de apresentação
3  feat: cliente da API externa
4  feat: leitura/parse da entrada
5  feat: núcleo da regra de negócio
6  feat: persistência / base de dados
7  feat: interface (CLI, HTTP, o que for)
8  chore: preserva scripts legados
9  fix: <a correção que motivou o trabalho>
10 test: cobertura da regra corrigida
11 feat: fixtures e dados de exemplo
12 docs: README completo e guia de uso
```

Ordem: infraestrutura → núcleo → periferia → correção → testes → exemplos → docs.

### Formato

Conventional Commits no assunto (`feat:`, `fix:`, `docs:`, `test:`, `chore:`,
`refactor:`, `perf:`), imperativo, minúscula, sem ponto final, ≤ 72 caracteres.

**Corpo obrigatório em tudo que não seja trivial.** O corpo explica **por que**,
não o que — o diff já mostra o que. Num `fix:`, descrever o comportamento errado,
a consequência para quem usa, e o que passou a valer. Exemplo do tom:

```
fix: valor negativo é desconto, não erro de planilha

Um valor negativo numa coluna significa abatimento acordado, e o TOTAL da
linha já o considera. O sistema tratava como anomalia: a linha era emitida
pelo valor líquido, mas o desconto não aparecia na mensagem, então o cliente
recebia uma cobrança cujas linhas não fechavam com o total.

Agora só o valor ZERO é descartado. Negativo vira linha com o sinal, o rótulo
continua vindo do OBSERV, e a linha sai em vermelho na revisão.

O mínimo de R$ 2,50 da API continua valendo: desconto não afrouxa validação.
```

Sem trailer de IA. Sem "Generated with".

### Fazer a correção virar um commit de verdade

Quando o trabalho inclui uma correção num projeto que ainda não tem histórico,
vale reconstruir o estado anterior, commitar o código como estava, e então
aplicar a correção como commit próprio. O `fix:` passa a ter diff legível em vez
de nascer embutido no commit inicial. Guardar cópia dos arquivos finais antes de
reverter, restaurar depois, e **confirmar que os testes ainda passam** e que a
árvore final é idêntica à que foi validada.

---

## Fase 5 — Publicar

```bash
git init -b main
# ... commits da Fase 4 ...

gh repo create <nome-kebab-case> --public --source=. --remote=origin \
  --description "<uma frase: o que faz e para quem>"

git push -u origin main
```

### Topics (as tags)

Sempre colocar — é o que faz o repo ser encontrado e dá acabamento à página.
De 5 a 8, misturando linguagem, domínio, tecnologia e tipo:

```bash
gh repo edit <user>/<repo> --add-topic python,automacao,banco-inter,boleto,api,contabilidade,cli,pandas
```

Minúsculas, hífen para separar palavras, sem acento.

### Verificação final, lendo de volta do GitHub

Não confiar no que foi enviado — conferir o que chegou:

```bash
gh api repos/<user>/<repo>/git/trees/main?recursive=1 -q '.tree[] | select(.type=="blob") | .path' | sort
gh api repos/<user>/<repo>/commits -q '.[].commit.message' | grep -i "claude\|anthropic\|co-authored"
gh repo view <user>/<repo> --json name,visibility,url
```

A lista de arquivos tem que ser exatamente a auditada na Fase 1.

---

## Modo B — repositório que só existe no GitHub

<!--
  COMO PEDIR: basta dizer, em qualquer sessão do Claude Code,
  "clona o meu repo <nome> do GitHub e aplica essa skill nele".
  Não precisa ter o projeto na máquina — o gh baixa, o trabalho acontece
  local e volta por push. O `gh` já está autenticado nesta máquina.
-->

Para revisar ou modernizar um repositório que não está no computador:

```bash
gh repo list <user> --limit 100                       # ver o que existe
cd ~/projetos                                          # pasta de trabalho
gh repo clone <user>/<repo>                            # baixa
cd <repo>
```

Daí em diante é o fluxo normal: Fase 0 (ler tudo), Fase 1 (auditar — inclusive
o histórico, que num repo antigo é onde os segredos costumam estar), Fase 2, 3,
4 e push.

Diferenças de um repo que já existe:

- **O histórico já é público.** Auditar `git log -p --all` é obrigatório, não
  opcional. Se achar segredo: rotacionar primeiro, limpar depois.
- **Não reescrever histórico antigo sem necessidade.** Melhorias entram como
  commits novos. Reescrita só para remover segredo.
- **Respeitar o que já está lá.** Ler o README existente antes de trocar;
  às vezes há contexto que só o autor sabia.
- **Se o repo é privado e vai virar público**, a auditoria tem que passar
  ANTES de `gh repo edit --visibility public`.
- Trabalhar em branch e abrir PR quando o repo tiver colaboradores; commitar
  direto em `main` só quando for projeto solo.

Ao terminar, a pasta local pode ser apagada — o GitHub tem tudo.

---

## Modo C — só auditar um repo existente

Quando o pedido é "vê se tem coisa comprometedora nos meus repositórios":

```bash
gh repo list <user> --limit 100 --json name,visibility,url
```

Para cada um: clonar com histórico completo, rodar `referencias/auditar.py`,
e reportar por repositório — o que achou, em qual commit, e o que fazer.
Não sair corrigindo sem combinar: rotacionar credencial é decisão do usuário,
e reescrever histórico de repo com fork quebra o de terceiros.

---

## Checklist final

Segurança:

- [ ] `git add -A -n` revisado arquivo por arquivo
- [ ] `referencias/auditar.py` sem achados, no working tree e no histórico
- [ ] Nenhum default de segredo no código
- [ ] `.gitignore` cobre credencial, chave, dado pessoal, base, saída, binário
- [ ] `#` do `.gitignore` escapado onde precisa
- [ ] Árvore lida de volta do GitHub bate com a auditada

Qualidade:

- [ ] README explica o problema antes da solução
- [ ] Decisões de projeto explicadas na seção de arquitetura
- [ ] Exemplo com entrada e saída reais
- [ ] `.env.example` e arquivos `*.exemplo.*` fictícios
- [ ] Projeto roda numa instalação limpa, sem os arquivos privados
- [ ] `LICENSE` presente
- [ ] Testes passando

Publicação:

- [ ] 8+ commits lógicos, Conventional Commits, corpo explicando o porquê
- [ ] **Zero menção a IA** em commit, README, código ou descrição
- [ ] Topics configurados
- [ ] Descrição do repositório preenchida
