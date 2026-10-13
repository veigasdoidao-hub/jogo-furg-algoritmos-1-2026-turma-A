# ============================================================
#  instalador.py  —  gera o Pegking.exe
#
#      python instalador.py          (ou dê dois cliques no .bat)
#
#  Resultado: pasta  dist/  com
#      Pegking.exe     o jogo
#      tela.txt        resolução (pode editar sem refazer o .exe)
#      niveis/         suas fases (se existirem aqui)
#  Para entregar o jogo, copie essa pasta inteira. Perfis e fases novas
#  são gravados ao lado do .exe.
#
#  O PyInstaller não cruza plataformas: rode no Windows para gerar .exe.
# ============================================================
import os
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
os.chdir(AQUI)


def rodar(comando):
    print("\n> " + " ".join(comando))
    subprocess.check_call(comando)


rodar([sys.executable, "-m", "pip", "install", "--upgrade", "flet", "pyinstaller"])

flet = shutil.which("flet")
if flet is None:
    rodar([sys.executable, "-m", "pip", "install", "--upgrade", "flet-cli"])
    flet = shutil.which("flet")
if flet is None:
    sys.exit("Não achei o comando 'flet'. Feche e abra o terminal e tente de novo.")

# tela.txt também vai DENTRO do exe (reserva); o de fora, se existir, tem prioridade.
rodar([flet, "pack", "menu.py", "--name", "Pegking",
       "--add-data", "tela.txt" + os.pathsep + ".", "--yes"])

dist = os.path.join(AQUI, "dist")
shutil.copy("tela.txt", dist)
if os.path.isdir("niveis"):
    shutil.copytree("niveis", os.path.join(dist, "niveis"), dirs_exist_ok=True)

print("\nPronto! Seu jogo está em: " + dist)
