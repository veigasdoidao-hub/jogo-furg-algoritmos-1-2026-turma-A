import json
import os
import sys

from caminhos import pasta_dados

ARQUIVO = os.path.join(pasta_dados(), "perfis.json")
TAMANHO_MAX_NOME = 16


def _ler():
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except (OSError, ValueError):
        dados = {}
    if not isinstance(dados, dict):
        dados = {}
    bruto = dados.get("perfis")
    if not isinstance(bruto, dict):
        bruto = {}

    perfis = {}
    for nome, d in bruto.items():
        rec = d.get("recordes") if isinstance(d, dict) else None
        if not isinstance(rec, dict):
            rec = {}
        perfis[str(nome)] = {"recordes": {str(k): int(v) for k, v in rec.items()
                                          if isinstance(v, (int, float))}}
    atual = dados.get("atual")
    if atual not in perfis:
        atual = next(iter(perfis), None)
    return {"atual": atual, "perfis": perfis}


def _gravar(dados):
    try:
        temporario = ARQUIVO + ".tmp"
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=1)
        os.replace(temporario, ARQUIVO)
    except OSError as erro:
        if sys.stderr:
            sys.stderr.write("[perfis] não consegui gravar %s: %s\n" % (ARQUIVO, erro))


def listar():
    return list(_ler()["perfis"])


def atual():
    return _ler()["atual"]


def recorde(nome, arquivo):
    perfil = _ler()["perfis"].get(nome)
    return perfil["recordes"].get(arquivo, 0) if perfil else 0


def recordes(nome):
    perfil = _ler()["perfis"].get(nome)
    return dict(perfil["recordes"]) if perfil else {}


def resumo():
    dados = _ler()
    return dados["atual"], [(n, len(p["recordes"])) for n, p in dados["perfis"].items()]


def quantos_recordes(nome):
    perfil = _ler()["perfis"].get(nome)
    return len(perfil["recordes"]) if perfil else 0


def criar(nome):
    nome = (nome or "").strip()
    if not nome:
        raise ValueError("O nome não pode ficar vazio.")
    if len(nome) > TAMANHO_MAX_NOME:
        raise ValueError("O nome pode ter no máximo %d letras." % TAMANHO_MAX_NOME)
    dados = _ler()
    if any(nome.casefold() == existente.casefold() for existente in dados["perfis"]):
        raise ValueError('Já existe um perfil chamado "%s".' % nome)
    dados["perfis"][nome] = {"recordes": {}}
    dados["atual"] = nome
    _gravar(dados)
    return nome


def definir_atual(nome):
    dados = _ler()
    if nome in dados["perfis"]:
        dados["atual"] = nome
        _gravar(dados)


def excluir(nome):
    dados = _ler()
    if nome in dados["perfis"]:
        del dados["perfis"][nome]
        if dados["atual"] == nome:
            dados["atual"] = next(iter(dados["perfis"]), None)
        _gravar(dados)


def registrar(nome, arquivo, pontos):
    dados = _ler()
    perfil = dados["perfis"].get(nome)
    if perfil is None or pontos <= 0:
        return False
    if pontos > perfil["recordes"].get(arquivo, 0):
        perfil["recordes"][arquivo] = int(pontos)
        _gravar(dados)
        return True
    return False


def esquecer_fase(arquivo):
    dados = _ler()
    mudou = False
    for perfil in dados["perfis"].values():
        if arquivo in perfil["recordes"]:
            del perfil["recordes"][arquivo]
            mudou = True
    if mudou:
        _gravar(dados)
