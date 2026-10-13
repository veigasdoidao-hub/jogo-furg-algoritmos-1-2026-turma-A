# ============================================================
#  caminhos.py  —  onde ficam os dados do jogo (fases, perfis, tela.txt)
# ============================================================
#  Rodando com "python menu.py": a pasta do próprio projeto.
#  Rodando como executável (.exe): a pasta onde o .exe está. Os dados
#  NÃO podem ficar dentro do .exe, porque lá dentro nada é gravável.
# ============================================================
import os
import sys


def pasta_dados():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))
