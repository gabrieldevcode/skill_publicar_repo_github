# Estrutura de README que funciona

Referência da Fase 3 da skill `publicar-repo-github`. Não é template para
preencher em branco — é o esqueleto e, mais importante, **o porquê de cada
seção**. README bom não é o que tem mais seção; é o que responde as perguntas
do leitor na ordem em que ele as faz.

## As perguntas do leitor, em ordem

1. O que é isso? *(uma frase)*
2. Por que existe? Que dor resolve? *(o problema)*
3. Como funciona por cima? *(o fluxo)*
4. Como eu faço rodar? *(instalar, configurar, usar)*
5. Como eu uso de verdade, no meu caso? *(formato de entrada, regras)*
6. Dá para confiar? *(validações, testes, privacidade)*
7. Como isso foi construído? *(arquitetura, decisões)*
8. O que não dá para fazer? *(limites)*

Um README que segue essa ordem parece escrito para quem chega. Um que começa
com lista de features parece escrito para quem já conhece — e é o erro mais
comum em projeto open source.

---

## Esqueleto

```markdown
# <emoji> Nome do Projeto — <contexto em 3 palavras>

<Uma frase dizendo o que faz. Sem adjetivo de marketing.>

<Dois ou três parágrafos: o processo manual que isso substitui, com números
se houver. "Cem clientes por mês, todo mês" vale mais que "economiza tempo".>

> **Aviso de privacidade**, se o projeto lida com dado sensível: o que NÃO
> está no repositório e por quê. Vem logo no topo — é o que faz o leitor
> confiar antes de ler o resto.

---

## 📑 Índice          <!-- só se passar de ~150 linhas -->

## 🎯 O problema
    A seção que quase ninguém escreve e que muda tudo. Descreva a situação
    real: quem, com que frequência, por que era difícil, o que dava errado.
    Termine explicando o que o projeto faz com isso.

## ⚙️ Como funciona, em uma passada
    Diagrama ASCII do fluxo entre os módulos, com uma linha de papel para
    cada um. O leitor entende a arquitetura antes de ver uma linha de código.

## 📦 Instalação
    Requisitos (versão da linguagem, contas/serviços necessários) e os
    comandos. Devem funcionar copiados e colados.

## 🔐 Configuração
    Numerada, uma subseção por peça: credenciais, certificados, base, config.
    Diga ONDE conseguir cada credencial. Mostre o .env.example.

## ▶️ Uso
    O fluxo principal, passo a passo numerado, do jeito que a pessoa vai viver.

## 📊 <Formato de entrada>
    Tabela de exemplo com dados FICTÍCIOS. Depois, em lista, o que o parser
    tolera e por quê. Um caso de borda representativo em destaque.

## 🧩 <Regra de negócio central>
    Como a entrada vira saída. Tabela de placeholders/opções. Exemplo real
    de entrada → saída, copiado da execução de verdade.

## ➖ <Caso especial importante>
    Se houver uma regra que já confundiu alguém (ou que motivou um bug),
    ela merece seção própria. Explique a semântica, não só o comportamento.

## 📅 <Regra que sempre gera dúvida>
    Datas, fusos, arredondamento, ordem. Se você teve que explicar duas
    vezes para alguém, vira seção.

## 🛡️ A rede de segurança
    Tabela: situação → o que o sistema faz. Mostra maturidade melhor que
    qualquer badge. "O valor não é a velocidade, é o que ele se recusa a
    fazer no piloto automático."

## 🗂️ Arquitetura
    Tabela arquivo → papel. Depois, em prosa, as 2 ou 3 DECISÕES DE PROJETO
    não óbvias. Esta é a parte que faz o leitor pensar "quem escreveu isso
    sabia o que estava fazendo". Exemplos do tipo certo:
      - "preparar_boletos() é pura: sem input(), sem rede, sem disco — é o
         que permite conferir um mês inteiro sem tocar na API."
      - "Nada é enviado antes do [C]. Tudo acontece em memória até lá."

## 🔒 Privacidade e segurança
    O que o .gitignore exclui e por quê. Que não há segredo no código.
    Que os arquivos de exemplo são inventados. Que é tudo local.
    Fecha com o aviso de tratar credencial como credencial.

## 🧪 Testar sem efeito colateral
    Como percorrer o fluxo sem disparar nada. Como rodar os testes.

## 📌 Limites conhecidos
    Da API, do formato, do domínio. Lista curta e específica, com números.

## 📄 Licença
```

---

## Regras de escrita

**Explicar o porquê, não só o quê.** O diff mostra o quê.

> ruim: "O parser encontra o cabeçalho automaticamente."
> bom: "O parser acha o cabeçalho sozinho, porque a planilha é mantida por
> pessoas, não por um sistema."

**Exemplo real com saída real.** Rodar o programa e copiar a saída. Exemplo
inventado tem cheiro de inventado e o leitor sente.

**Tabela para referência, prosa para raciocínio.** Placeholders, validações,
arquivo→papel, limites: tabela. Decisão de projeto, motivação, contexto: prosa.

**Bloco de código sempre executável**, com a linguagem marcada para colorir.

**Hierarquia consistente.** Um `#`, `##` nas seções, `###` nas subseções, sem
pular nível — leitor de tela e indexação de busca dependem disso.

**Um emoji por título de seção**, no máximo. Ajuda a escanear a página. Se o
índice usa âncoras, lembrar que emoji entra na âncora gerada pelo GitHub.

**Idioma do projeto.** Código, domínio e usuário em português → README em
português. Não traduzir por achar que "open source tem que ser em inglês".

---

## Badges

No máximo 4, e só as que dizem algo verdadeiro:

- licença
- build/CI — **só se houver CI configurado de verdade**
- versão publicada (npm, PyPI)
- linguagem/versão mínima

Fileira de badge de vaidade (downloads de projeto sem downloads, "made with
love", contadores) é sinal de README preenchido sem cuidado.

---

## Anti-padrões

| Anti-padrão | Por que dói |
|---|---|
| Lista de features antes de mostrar funcionando | O leitor ainda não sabe o que é |
| "Contributing"/"Roadmap" genérico de template | Ninguém lê, e denuncia preenchimento automático |
| Screenshot de terminal como imagem | Não dá para copiar, quebra no tema escuro |
| Parágrafo de marketing no topo | Atrasa a resposta à pergunta 1 |
| Prometer o que o código não faz | Destrói a confiança na primeira tentativa |
| Instrução que não funciona copiada e colada | Erro mais caro do README inteiro |
| Dado real em exemplo | Vazamento, e a skill existe para evitar isso |

---

## Teste final

Depois de escrever, reler fingindo que nunca viu o projeto:

1. Em 30 segundos eu entendo o que isso é e para quem?
2. Em 5 minutos eu consigo ver funcionando?
3. Alguma seção responde pergunta que eu ainda não tinha?
   → está fora de ordem.
4. Algum comando falharia copiado e colado?
   → testar de verdade.
5. Tem algum dado real aqui?
   → voltar para a Fase 1.

---

## Fontes consultadas

- [How to Write a Great GitHub README (2026) — RepoClip](https://repoclip.io/blog/how-to-write-a-github-readme)
- [GitHub README Best Practices in 2026 — pushpen.dev](https://pushpen.dev/blog/github-readme-best-practices-2026)
- [GitHub README Template (2026): Best Practices + 12 Examples](https://gingiris.github.io/growth-tools/blog/2026/04/02/github-readme-template-guide/)
