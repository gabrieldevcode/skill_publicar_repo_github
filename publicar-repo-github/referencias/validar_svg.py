#!/usr/bin/env python3
"""Valida os SVGs animados de um README antes de commitar.

Uso: python validar_svg.py docs/animacoes [--max-kb=12]

Confere o que o GitHub aceita: XML válido, sem script, sem recurso externo,
com aria-label, com prefers-reduced-motion e com peso razoável.
Somente leitura. Sai com código 1 se algum SVG falhar.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

MAX_KB = 12
for a in sys.argv[1:]:
    if a.startswith("--max-kb="):
        MAX_KB = int(a.split("=", 1)[1])

alvo = next((a for a in sys.argv[1:] if not a.startswith("--")), ".")
arquivos = [alvo] if alvo.endswith(".svg") else [
    os.path.join(d, f) for d, _, fs in os.walk(alvo) for f in fs if f.endswith(".svg")
]
if not arquivos:
    print("nenhum .svg encontrado em", alvo)
    sys.exit(1)

PROIBIDO = [
    (r"<script", "contém <script> (GitHub remove e pode descartar o SVG)"),
    (r"<foreignObject", "contém <foreignObject> (não renderiza no GitHub)"),
    (r"\bon[a-z]+\s*=", "contém handler de evento (onclick...)"),
    (r"(?:href|src)\s*=\s*[\"']https?://", "referencia recurso externo"),
    (r"url\(\s*[\"']?https?://", "referencia recurso externo via url()"),
    (r"@import", "usa @import (fonte/CSS externo)"),
    (r"(?i)claude|anthropic|gerado por ia|generated with", "menção a IA (Regra 2)"),
]

falhas = 0
for caminho in sorted(arquivos):
    erros = []
    bruto = open(caminho, encoding="utf-8").read()
    kb = len(bruto.encode("utf-8")) / 1024
    try:
        raiz = ET.fromstring(bruto)
    except ET.ParseError as e:
        erros.append(f"XML inválido: {e}")
        raiz = None
    if raiz is not None:
        if not raiz.tag.endswith("svg"):
            erros.append("raiz não é <svg>")
        if "viewBox" not in raiz.attrib:
            erros.append("falta viewBox (não escala no README)")
        if not raiz.attrib.get("aria-label") and "aria-hidden" not in raiz.attrib:
            erros.append("falta aria-label (ou aria-hidden para decorativo)")
        if "xmlns" not in bruto:
            erros.append("falta xmlns")
    if kb > MAX_KB:
        erros.append(f"{kb:.1f} KB > {MAX_KB} KB")
    if "@keyframes" in bruto and "prefers-reduced-motion" not in bruto:
        erros.append("anima mas não respeita prefers-reduced-motion")
    if "@keyframes" not in bruto and "<animate" not in bruto:
        erros.append("não tem nenhuma animação")
    for padrao, msg in PROIBIDO:
        if re.search(padrao, bruto):
            erros.append(msg)
    print(("FALHA " if erros else "ok    ") + f"{caminho} ({kb:.1f} KB)")
    for e in erros:
        print("   -", e)
    falhas += bool(erros)

sys.exit(1 if falhas else 0)
