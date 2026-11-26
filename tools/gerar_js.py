"""Converte dados/semob_linhas_organizado.json em dados-semob.js (o arquivo que a página carrega).
Uso, a partir da raiz do projeto:  python3 tools/gerar_js.py
"""
import json, pathlib

raiz = pathlib.Path(__file__).resolve().parent.parent
dados = json.loads((raiz / "dados" / "semob_linhas_organizado.json").read_text(encoding="utf-8"))
(raiz / "dados-semob.js").write_text(
    "window.SEMOB_DATA = " + json.dumps(dados, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
print("dados-semob.js gerado com", len(dados["linhas"]), "linhas")
