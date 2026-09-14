import os

def config():
    diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho_tela = os.path.join(diretorio, "tela.txt")
    with open(caminho_tela, "r") as arquivo:
        configuracoes = {}

        for linha in arquivo:
            chave, valor = linha.strip().split("=")
            configuracoes[chave.strip()] = int(valor.strip())

    tela_x = configuracoes["tela_x"]
    tela_y = configuracoes["tela_y"]
    botaolargura = configuracoes["botaolargura"]
    botaoaltura = configuracoes["botaoaltura"]
    escala = configuracoes["escala"]

    return tela_x,tela_y,botaolargura,botaoaltura,escala
def paths():
    diretorio = os.path.dirname(os.path.abspath(__file__))
    botao1 = os.path.join(diretorio, r"graficos\botaojogar.jpg")
    botao2 = os.path.join(diretorio, r"graficos\botaosair.jpg")
    botao3 = os.path.join(diretorio, r"graficos\botaoperfil.jpg")

    botaoANI1 = os.path.join(diretorio, r"graficos\botaojogar.jpg")
    botaoANI2 = os.path.join(diretorio, r"graficos\botaojogar2.jpg")
    botaoANI3 = os.path.join(diretorio, r"graficos\botaojogar3.jpg")
    botaoANI4 = os.path.join(diretorio, r"graficos\botaojogar4.jpg")
    quadros_jogar = [botaoANI1, botaoANI2, botaoANI3, botaoANI4]

    botaoSairANI1 = os.path.join(diretorio, r"graficos\botaosair.jpg")
    botaoSairANI2 = os.path.join(diretorio, r"graficos\botaosair2.jpg")
    botaoSairANI3 = os.path.join(diretorio, r"graficos\botaosair3.jpg")
    botaoSairANI4 = os.path.join(diretorio, r"graficos\botaosair4.jpg")
    quadros_sair = [botaoSairANI1, botaoSairANI2, botaoSairANI3, botaoSairANI4]

    botaoPerfilANI1 = os.path.join(diretorio, r"graficos\botaoperfil.jpg")
    botaoPerfilANI2 = os.path.join(diretorio, r"graficos\botaoperfil2.jpg")
    botaoPerfilANI3 = os.path.join(diretorio, r"graficos\botaoperfil3.jpg")
    botaoPerfilANI4 = os.path.join(diretorio, r"graficos\botaoperfil4.jpg")
    quadros_perfil = [botaoPerfilANI1, botaoPerfilANI2, botaoPerfilANI3, botaoPerfilANI4]

    return botao1, botao2, botao3, quadros_jogar, quadros_sair, quadros_perfil
