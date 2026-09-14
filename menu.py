import aroeira
import configurações
import mira_e_atira
tela_x, tela_y,botao_largura,botao_altura,escala = configurações.config()
botao_largura = botao_largura/escala
botao_altura = botao_altura/escala
botao_jogar, botao_sair, botao_perfil, quadros_botao_jogar, quadros_botao_sair, quadros_botao_perfil = configurações.paths()
sobre_botao_jogar = False
sobre_botao_sair = False
sobre_botao_perfil = False
quadro_atual_jogar = 0
quadro_atual_sair = 0
quadro_atual_perfil = 0
contagem_quadro_jogar = 0
contagem_quadro_sair = 0
contagem_quadro_perfil = 0
intervalo_troca_quadro = 2  
tela = aroeira.Tela("PEEGLE", altura=tela_y, largura=tela_x)
#FUNÇÃO QUE DETECTA A HITBOX DO BOTÃO
def opcao_hitbox(ponto, botao):
    return (botao.origem.x <= ponto.x <= botao.origem.x + botao.largura and botao.origem.y <= ponto.y <= botao.origem.y + botao.altura)
def clicar(ponto):
    
    if opcao_hitbox(ponto, placeholder_botão):
        tela.remover(bota1)
        tela.remover(bota2)
        tela.remover(bota3)
        tela.remover(placeholder_background)
        tela.ao_clicar(None)
        mira_e_atira.Jogo.jogar(tela)
    elif  opcao_hitbox(ponto, placeholder_botão2):
        quit()
    elif opcao_hitbox(ponto,placeholder_botão3):
        quit()

def selecionar(ponto):
    global sobre_botao_jogar, quadro_atual_jogar, contagem_quadro_jogar
    global sobre_botao_sair, quadro_atual_sair, contagem_quadro_sair
    global sobre_botao_perfil, quadro_atual_perfil, contagem_quadro_perfil

    
    sobre_botao_jogar = opcao_hitbox(ponto, placeholder_botão)
    if not sobre_botao_jogar and quadro_atual_jogar != 0:
        quadro_atual_jogar = 0
        contagem_quadro_jogar = 0
        bota1.caminho = botao_jogar


    sobre_botao_sair = opcao_hitbox(ponto, placeholder_botão2)
    if not sobre_botao_sair and quadro_atual_sair != 0:
        quadro_atual_sair = 0
        contagem_quadro_sair = 0
        bota2.caminho = botao_sair


    sobre_botao_perfil = opcao_hitbox(ponto, placeholder_botão3)
    if not sobre_botao_perfil and quadro_atual_perfil != 0:
        quadro_atual_perfil = 0
        contagem_quadro_perfil = 0
        bota3.caminho = botao_perfil


def animar():
    global quadro_atual_jogar, contagem_quadro_jogar
    global quadro_atual_sair, contagem_quadro_sair
    global quadro_atual_perfil, contagem_quadro_perfil

  
    if sobre_botao_jogar and quadro_atual_jogar < len(quadros_botao_jogar) - 1:
        contagem_quadro_jogar += 1
        if contagem_quadro_jogar >= intervalo_troca_quadro:
            contagem_quadro_jogar = 0
            quadro_atual_jogar += 1
            bota1.caminho = quadros_botao_jogar[quadro_atual_jogar]

   
    if sobre_botao_sair and quadro_atual_sair < len(quadros_botao_sair) - 1:
        contagem_quadro_sair += 1
        if contagem_quadro_sair >= intervalo_troca_quadro:
            contagem_quadro_sair = 0
            quadro_atual_sair += 1
            bota2.caminho = quadros_botao_sair[quadro_atual_sair]

   
    if sobre_botao_perfil and quadro_atual_perfil < len(quadros_botao_perfil) - 1:
        contagem_quadro_perfil += 1
        if contagem_quadro_perfil >= intervalo_troca_quadro:
            contagem_quadro_perfil = 0
            quadro_atual_perfil += 1
            bota3.caminho = quadros_botao_perfil[quadro_atual_perfil]
def pre_carregar_imagens():
    todos_os_caminhos = (quadros_botao_jogar + quadros_botao_sair + quadros_botao_perfil)
    for caminho in todos_os_caminhos:
        escondida = aroeira.Imagem(aroeira.Ponto(-10000, 0), caminho)
        escondida.visivel = True
        tela.adicionar(escondida)


bota1 = aroeira.Imagem(caminho=botao_jogar,origem=(aroeira.Ponto(((tela_x/2)-(botao_altura)),tela_y/2)), altura= botao_altura, largura= botao_largura,)
bota2 = aroeira.Imagem(caminho=botao_sair,origem=(aroeira.Ponto(((tela_x/2)-(botao_altura)),(tela_y/2+botao_altura))), altura= botao_altura, largura= botao_largura,)
bota3 = aroeira.Imagem(caminho=botao_perfil,origem=(aroeira.Ponto(((tela_x/2)-(botao_altura)),((tela_y/2+botao_altura*2)))), altura= botao_altura, largura= botao_largura,)
placeholder_botão = aroeira.Retangulo(origem=(aroeira.Ponto(((tela_x/2)-(botao_altura)),tela_y/2)),altura=botao_altura,largura=botao_largura, cor="azul")
placeholder_botão2 = aroeira.Retangulo(origem=(aroeira.Ponto(((tela_x/2)-(botao_altura)),(tela_y/2+botao_altura))),altura=botao_altura,largura=botao_largura, cor="azul")
placeholder_botão3 = aroeira.Retangulo(origem=(aroeira.Ponto(((tela_x/2)-(botao_altura)),((tela_y/2+botao_altura*2)))),altura=botao_altura,largura=botao_largura, cor="azul")
placeholder_background = aroeira.Retangulo(origem=(aroeira.Ponto(00,00)),largura=tela_x,altura=tela_y)

pre_carregar_imagens()
tela.adicionar(placeholder_background)
tela.adicionar(bota1)
tela.adicionar(bota2)
tela.adicionar(bota3)


tela.ao_clicar(clicar)
tela.ao_mover_mouse(selecionar)
tela.animar(animar, fps=60)
tela.executar(tela_cheia=True)
