# ============================================================
#  configurações.py  —  lê o tela.txt
# ============================================================
#  O tela.txt que estiver ao lado do programa (ou do .exe) tem
#  prioridade. Assim dá para mudar a resolução sem refazer o executável.
#  Os botões agora são todos da Aroeira (ver estilo.py): a antiga
#  função paths(), que apontava para graficos/, não existe mais.
# ============================================================
import os

from caminhos import pasta_dados

_PADRAO = {"tela_x": 1920, "tela_y": 1080, "escala": 10,
           "botaoaltura": 1500, "botaolargura": 3000}


def _achar_tela_txt():
    ao_lado = os.path.join(pasta_dados(), "tela.txt")
    if os.path.isfile(ao_lado):
        return ao_lado
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "tela.txt")


def config():
    """Devolve (tela_x, tela_y, botaolargura, botaoaltura, escala)."""
    configuracoes = dict(_PADRAO)
    try:
        with open(_achar_tela_txt(), "r") as arquivo:
            for linha in arquivo:
                if "=" not in linha:
                    continue                      # ignora linhas em branco
                chave, valor = linha.strip().split("=")
                configuracoes[chave.strip()] = int(valor.strip())
    except OSError:
        pass                                      # sem tela.txt: usa o padrão
    return (configuracoes["tela_x"], configuracoes["tela_y"],
            configuracoes["botaolargura"], configuracoes["botaoaltura"],
            configuracoes["escala"])
