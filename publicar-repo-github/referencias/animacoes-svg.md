# Animações SVG para o README

Referência da Fase 4 da skill `publicar-repo-github`. Modelo real:
[`gabrieldevcode/lab-gestore`](https://github.com/gabrieldevcode/lab-gestore),
pasta `docs/animacoes/` (banner, divisor, fluxo-kanban, nota-obrigatoria,
caminhao, contadores, confete, api-terminal).

Princípio: **a animação conta o que o projeto faz.** Se trocar o nome do projeto
e ela continuar servindo, é genérica demais — refazer.

---

## O que o GitHub aceita

SVG vai num `<img>`. Nesse modo:

| Funciona | Não funciona |
|---|---|
| CSS `@keyframes`, `animation`, `transform`, `opacity` | `<script>` / JavaScript |
| `<animate>` / `<animateTransform>` (SMIL) | `<foreignObject>` |
| Gradientes, `clipPath`, `stroke-dasharray` | Fonte web externa, `@import` |
| Fontes do sistema (`Segoe UI`, `system-ui`...) | Imagem/URL externa |
| `@media (prefers-reduced-motion)` | Interação (hover, clique) |

Use **CSS puro**. Sempre termine o `<style>` com:

```css
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
```

Para animação de entrada (`opacity:0` → `1`), o estado reduzido tem que deixar o
elemento **visível**: `@media (prefers-reduced-motion:reduce){.etapa{opacity:1}}`
antes da regra `*`.

## Regras de projeto

1. **Paleta do projeto.** Ler as cores do CSS/tailwind/logo na Fase 0. Duas cores
   (principal + destaque) e neutros. Sem identidade visual: azul `#2563EB` +
   verde `#22C55E` sobre `#FFFFFF`→`#F1F5F9`.
2. **Mecanismo central animado.** Perguntar: "o que passa por onde?" Nota por camadas,
   pedido numa esteira, requisição num servidor, dado por um pipeline, sensor
   pulsando, caminhão numa estrada.
3. **Leve e simples.** ≤ 12 KB, 900 px de largura, `viewBox` sempre. Loop lento
   (3–9 s) ou entrada única em sequência (delays de 0,4 s).
4. **Dados fictícios**, como no resto do README.
5. **Acessível.** `role="img"` e `aria-label` descritivo; divisor decorativo
   pode usar `aria-label="Divisor"`.
6. **Nunca texto sobre IA** no SVG.

## Conjunto mínimo

| Arquivo | Altura | Conteúdo |
|---|---|---|
| `banner.svg` | 260 | Nome, frase, traço que se desenha, etapas do fluxo entrando uma a uma |
| `divisor.svg` | 12 | Linha com brilho deslizando |
| `fluxo-<tema>.svg` | 200–300 | O fluxo real, um objeto percorrendo as etapas |
| 1–3 de tema | variável | A regra única do projeto (barreira, contador, terminal, estrada...) |

## Como embutir

```html
<div align="center">

<img src="docs/animacoes/banner.svg" alt="Nome — frase curta" width="100%">

</div>

...texto...

<p align="center"><img src="docs/animacoes/divisor.svg" alt="" width="100%"></p>

<p align="center"><img src="docs/animacoes/fluxo-tema.svg" alt="Descrição do fluxo" width="100%"></p>
```

Caminho **relativo** (`docs/animacoes/...`): funciona no GitHub, em forks e no
clone. Não usar `raw.githubusercontent.com`.

---

## Receitas

Troque as cores (`#2A2158` principal, `#A3CE3C` destaque) pelas do projeto.

### Divisor com brilho

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="12" viewBox="0 0 900 12" role="img" aria-label="Divisor">
<style>
.brilho{animation:brilho 3.2s ease-in-out infinite}
@keyframes brilho{0%{transform:translateX(-220px)}100%{transform:translateX(900px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>
<defs>
<linearGradient id="luz" x1="0" x2="1"><stop offset="0" stop-color="#2A2158" stop-opacity="0"/><stop offset=".5" stop-color="#2A2158"/><stop offset="1" stop-color="#2A2158" stop-opacity="0"/></linearGradient>
<clipPath id="linha"><rect x="0" y="4" width="900" height="4" rx="2"/></clipPath>
</defs>
<rect x="0" y="4" width="900" height="4" rx="2" fill="#A3CE3C" fill-opacity=".45"/>
<g clip-path="url(#linha)"><rect class="brilho" x="0" y="4" width="220" height="4" fill="url(#luz)"/></g>
</svg>
```

### Banner: título, traço que se desenha, etapas em sequência

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="260" viewBox="0 0 900 260" role="img" aria-label="NOME — frase do projeto">
<style>
.titulo{font:800 56px 'Segoe UI',Inter,system-ui,sans-serif;fill:#2A2158;letter-spacing:3px}
.sub{font:400 19px 'Segoe UI',Inter,system-ui,sans-serif;fill:#6B6880}
.pill{font:600 14px 'Segoe UI',Inter,system-ui,sans-serif;fill:#1C1A2E}
.traco{stroke-dasharray:300;stroke-dashoffset:300;animation:desenha 1.4s .2s ease-out forwards}
@keyframes desenha{to{stroke-dashoffset:0}}
.etapa{opacity:0;animation:aparece .5s ease-out forwards}
.e1{animation-delay:.7s}.e2{animation-delay:1.1s}.e3{animation-delay:1.5s}
@keyframes aparece{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@media (prefers-reduced-motion:reduce){.traco{stroke-dashoffset:0}.etapa{opacity:1}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>
<defs>
<linearGradient id="fundo" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#EEEDF4"/></linearGradient>
<clipPath id="moldura"><rect width="900" height="260" rx="18"/></clipPath>
</defs>
<g clip-path="url(#moldura)">
<rect width="900" height="260" fill="url(#fundo)"/>
<text class="titulo" x="450" y="92" text-anchor="middle">NOME</text>
<path class="traco" d="M300 112 H600" stroke="#A3CE3C" stroke-width="4" stroke-linecap="round"/>
<text class="sub" x="450" y="148" text-anchor="middle">Frase do projeto em uma linha</text>
<g class="etapa e1"><rect x="230" y="172" width="120" height="32" rx="16" fill="#FFF" stroke="#E6E4EE"/><text class="pill" x="290" y="193" text-anchor="middle">Etapa 1</text></g>
<g class="etapa e2"><rect x="390" y="172" width="120" height="32" rx="16" fill="#FFF" stroke="#E6E4EE"/><text class="pill" x="450" y="193" text-anchor="middle">Etapa 2</text></g>
<g class="etapa e3"><rect x="550" y="172" width="120" height="32" rx="16" fill="#FFF" stroke="#E6E4EE"/><text class="pill" x="610" y="193" text-anchor="middle">Etapa 3</text></g>
</g>
</svg>
```

### Fluxo: um objeto percorre as etapas

Estações fixas + um ponto que viaja em loop. O mesmo padrão serve para pedido,
requisição, arquivo, mensagem — trocar o rótulo e o formato do objeto.

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="160" viewBox="0 0 900 160" role="img" aria-label="Um item passa por A, B e C">
<style>
.est{font:600 14px 'Segoe UI',Inter,system-ui,sans-serif;fill:#1C1A2E}
.item{animation:viaja 6s ease-in-out infinite}
@keyframes viaja{0%{transform:translateX(0)}40%{transform:translateX(300px)}55%{transform:translateX(300px)}95%{transform:translateX(600px)}100%{transform:translateX(600px)}}
.pulso{transform-box:fill-box;transform-origin:center;animation:pulsa 2s ease-in-out infinite}
@keyframes pulsa{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>
<path d="M150 80 H750" stroke="#E6E4EE" stroke-width="4" stroke-linecap="round"/>
<g><circle cx="150" cy="80" r="26" fill="#FFF" stroke="#2A2158" stroke-width="2"/><text class="est" x="150" y="130" text-anchor="middle">A</text></g>
<g><circle cx="450" cy="80" r="26" fill="#FFF" stroke="#2A2158" stroke-width="2"/><text class="est" x="450" y="130" text-anchor="middle">B</text></g>
<g><circle cx="750" cy="80" r="26" fill="#FFF" stroke="#2A2158" stroke-width="2"/><text class="est" x="750" y="130" text-anchor="middle">C</text></g>
<g class="item"><circle class="pulso" cx="150" cy="80" r="11" fill="#A3CE3C"/></g>
</svg>
```

### Outras ideias que combinam com o projeto

| Projeto é... | Animação | Técnica |
|---|---|---|
| Fila / mensageria | Mensagens entrando e saindo da fila | `translateX` com delays escalonados |
| API / backend | Terminal digitando uma requisição e a resposta | `clip-path`/largura animada em `<text>`, cursor piscando |
| Dashboard / métricas | Contadores que sobem e barras que crescem | `transform:scaleY` com `transform-origin` embaixo |
| Barreira / validação | Item barrado por um portão e outro que passa | dois objetos, um para em `x` fixo |
| Logística / entrega | Caminhão numa estrada tracejada | `stroke-dasharray` rolando + corpo balançando |
| IoT / sensor | Ondas se expandindo do sensor | `scale` + `opacity` em círculos concêntricos |
| Pipeline de dados | Pontos fluindo por etapas com cores diferentes | `animateMotion` ou `translateX` encadeado |
| Celebração (fim do fluxo) | Confete/estrelas ao concluir | retângulos pequenos com `translateY` + `rotate` |

## Validar

```bash
python ~/.claude/skills/publicar-repo-github/referencias/validar_svg.py docs/animacoes
```

Falha se o SVG tem XML inválido, `<script>`, recurso externo, falta de `viewBox`
ou `aria-label`, não respeita `prefers-reduced-motion`, passa de 12 KB ou
menciona IA. Para **ver** a animação antes de publicar, abra o arquivo no
navegador (`start docs/animacoes/banner.svg`).

## Erros comuns

| Erro | Efeito | Correção |
|---|---|---|
| Fonte do Google via `@import` | Cai na fonte padrão | Pilha de sistema |
| `transform-origin` sem `transform-box:fill-box` | Gira em torno do canto da tela | Adicionar `transform-box:fill-box;transform-origin:center` |
| Entrada com `opacity:0` sem regra reduced-motion | Fica invisível para quem desliga animação | `opacity:1` no `@media` |
| Largura fixa sem `viewBox` | Estoura no celular | `viewBox` + `width="100%"` no `<img>` |
| Animação que não representa o projeto | Enfeite genérico | Voltar à Fase 0: qual é o mecanismo central? |
