import os
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
os.chdir(AQUI)


def rodar(comando):
    print("\n> " + " ".join(comando))
    subprocess.check_call(comando)


rodar([sys.executable, "-m", "pip", "install", "--upgrade", "pyxel", "pyinstaller"])

rodar([sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole", "--noconfirm",
       "--name", "Pegking", "--collect-all", "pyxel", "menu.py"])

dist = os.path.join(AQUI, "dist")
if os.path.isdir("niveis"):
    shutil.copytree("niveis", os.path.join(dist, "niveis"), dirs_exist_ok=True)

print("\nPronto! Seu jogo está em: " + dist)
