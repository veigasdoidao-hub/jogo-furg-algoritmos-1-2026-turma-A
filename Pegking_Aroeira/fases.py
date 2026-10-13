# ============================================================
#  fases.py  —  ler, gravar e listar as fases (níveis)
# ============================================================
#  Cada fase é um arquivo .json dentro da pasta "niveis/":
#
#      {"nome": "Grade", "bolas": 10, "ordem": 1,
#       "pegs": [{"x": 300, "y": 400, "tipo": "azul"}, ...]}
#
#  As coordenadas são relativas ao CAMPO (a área entre as paredes),
#  não à tela. Assim a fase não depende de onde o campo fica.
#  Este arquivo não usa nada gráfico: é só dado.
# ============================================================
import json
import math
import os
import re
import unicodedata

import configurações
from caminhos import pasta_dados

PASTA = os.path.join(pasta_dados(), "niveis")

_tela_x, _tela_y, *_ = configurações.config()

MARGEM = 250                    # largura dos painéis laterais
CAMPO_L = _tela_x - 2 * MARGEM  # largura do campo de jogo
CAMPO_A = _tela_y               # altura do campo de jogo
RAIO_PEG = 30
Y_MIN_PEG = 140                 # nenhum peg acima disto (o canhão fica ali)
BOLAS_PADRAO = 10
BOLAS_MAX = 30


# ------------------------------------------------------------
#  Nomes de arquivo
# ------------------------------------------------------------
def nome_para_arquivo(nome):
    """'Minha Fase Épica!' -> 'minha_fase_epica.json'"""
    texto = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_")
    return (texto or "fase") + ".json"


def _caminho(arquivo):
    return os.path.join(PASTA, arquivo)


def existe(arquivo):
    return os.path.isfile(_caminho(arquivo))


# ------------------------------------------------------------
#  Ler
# ------------------------------------------------------------
def _normalizar(dados, arquivo):
    """Aceita um arquivo meio torto e devolve sempre um dicionário válido."""
    if not isinstance(dados, dict):
        raise ValueError("arquivo de fase inválido")

    pegs = []
    for p in dados.get("pegs", []):
        try:
            x = float(p["x"])
            y = float(p["y"])
        except (KeyError, TypeError, ValueError):
            continue
        tipo = "laranja" if p.get("tipo") == "laranja" else "azul"
        pegs.append({"x": x, "y": y, "tipo": tipo})

    try:
        bolas = int(dados.get("bolas", BOLAS_PADRAO))
    except (TypeError, ValueError):
        bolas = BOLAS_PADRAO
    try:
        ordem = int(dados.get("ordem", 1000))
    except (TypeError, ValueError):
        ordem = 1000

    return {
        "arquivo": arquivo,
        "nome": str(dados.get("nome") or os.path.splitext(arquivo)[0]),
        "bolas": max(1, min(BOLAS_MAX, bolas)),
        "ordem": ordem,
        "pegs": pegs,
    }


def carregar(arquivo):
    with open(_caminho(arquivo), "r", encoding="utf-8") as f:
        return _normalizar(json.load(f), arquivo)


def listar():
    """Todas as fases, na ordem em que aparecem no seletor."""
    if not os.path.isdir(PASTA):
        return []
    resultado = []
    for arquivo in os.listdir(PASTA):
        if not arquivo.endswith(".json"):
            continue
        try:
            resultado.append(carregar(arquivo))
        except (OSError, ValueError):
            continue          # arquivo quebrado não derruba o jogo
    resultado.sort(key=lambda f: (f["ordem"], f["arquivo"]))
    return resultado


def proxima(arquivo):
    """A fase que vem depois de `arquivo` (ou None se for a última)."""
    todas = listar()
    for i, fase in enumerate(todas):
        if fase["arquivo"] == arquivo:
            return todas[i + 1] if i + 1 < len(todas) else None
    return None


# ------------------------------------------------------------
#  Gravar
# ------------------------------------------------------------
def validar(fase):
    """Devolve um texto explicando o problema, ou None se a fase está ok."""
    if not any(p["tipo"] == "laranja" for p in fase["pegs"]):
        return "A fase precisa de pelo menos um peg laranja: é ele o objetivo do jogo."
    return None


def salvar(fase, arquivo=None):
    arquivo = arquivo or nome_para_arquivo(fase["nome"])
    os.makedirs(PASTA, exist_ok=True)
    dados = {
        "nome": fase["nome"],
        "bolas": int(fase["bolas"]),
        "ordem": int(fase.get("ordem", 1000)),
        "pegs": [{"x": int(round(p["x"])), "y": int(round(p["y"])), "tipo": p["tipo"]}
                 for p in fase["pegs"]],
    }
    with open(_caminho(arquivo), "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)
    return arquivo


def excluir(arquivo):
    try:
        os.remove(_caminho(arquivo))
    except FileNotFoundError:
        pass


# ------------------------------------------------------------
#  Fases prontas (criadas na primeira execução)
# ------------------------------------------------------------
def _peg(x, y, laranja=False):
    return {"x": int(round(x)), "y": int(round(y)),
            "tipo": "laranja" if laranja else "azul"}


def _grade():
    cx, pegs = CAMPO_L / 2, []
    for linha in range(6):
        colunas = 11 if linha % 2 == 0 else 10
        for col in range(colunas):
            x = cx + (col - (colunas - 1) / 2) * 120
            pegs.append(_peg(x, 300 + linha * 110, (linha + col) % 5 == 0))
    return pegs


def _circulos():
    cx, cy, pegs = CAMPO_L / 2, 580, []
    for i in range(16):
        a = 2 * math.pi * i / 16
        pegs.append(_peg(cx + 330 * math.cos(a), cy + 330 * math.sin(a), i % 4 == 0))
    for i in range(8):
        a = 2 * math.pi * i / 8
        pegs.append(_peg(cx + 180 * math.cos(a), cy + 180 * math.sin(a), i % 2 == 0))
    pegs.append(_peg(cx, cy, True))
    return pegs


def _ondas():
    cx, pegs = CAMPO_L / 2, []
    for linha in range(3):
        for k in range(12):
            x = cx + (k - 5.5) * 108
            y = 320 + linha * 240 + 70 * math.sin(k * 0.8 + linha)
            pegs.append(_peg(x, y, (k + 2 * linha) % 4 == 0))
    return pegs


def _piramide():
    cx, pegs = CAMPO_L / 2, []
    for i in range(9):
        for j in range(i + 1):
            x = cx + (j - i / 2) * 110
            pegs.append(_peg(x, 250 + i * 80, i >= 3 and (j == 0 or j == i)))
    return pegs


def _fases_padrao():
    return [
        {"nome": "Grade",     "bolas": 10, "ordem": 1, "pegs": _grade()},
        {"nome": "Círculos",  "bolas": 10, "ordem": 2, "pegs": _circulos()},
        {"nome": "Ondas",     "bolas": 10, "ordem": 3, "pegs": _ondas()},
        {"nome": "Pirâmide",  "bolas": 10, "ordem": 4, "pegs": _piramide()},
    ]


def garantir_fases_padrao():
    """Se a pasta niveis/ não tem nenhuma fase, cria as fases prontas."""
    os.makedirs(PASTA, exist_ok=True)
    if any(a.endswith(".json") for a in os.listdir(PASTA)):
        return
    for fase in _fases_padrao():
        salvar(fase)
