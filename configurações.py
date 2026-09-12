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
    return botao1,botao2,botao3