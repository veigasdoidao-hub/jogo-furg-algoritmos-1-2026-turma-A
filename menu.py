import aroeira
import configurações
import mira_e_atira
tela_x, tela_y,botao_largura,botao_altura,escala = configurações.config()
botao_largura = botao_largura/escala
botao_altura = botao_altura/escala
botao_path,botao_path2,botao_path3 = configurações.paths()

tela = aroeira.Tela("PEEGLE", altura=tela_y, largura=tela_x)

def opcao_hitbox(ponto, botao):
    return (botao.origem.x <= ponto.x <= botao.origem.x + botao.largura and botao.origem.y <= ponto.y <= botao.origem.y + botao.altura)


def clicar(ponto):
    
    if opcao_hitbox(ponto, placeholder_botão):
        tela.remover(bota1)
        tela.remover(bota2)
        tela.remover(bota3)
        tela.remover(placeholder_background)
        tela.ao_clicar(None)
        mira_e_atira.jogar(tela)
    elif  opcao_hitbox(ponto, placeholder_botão2):
        quit()
    elif opcao_hitbox(ponto,placeholder_botão3):
        quit()
 
def placeholder_(ponto):
    pass
def placeholder_a():
    pass    

bota1 = aroeira.Imagem(caminho=botao_path,origem=(aroeira.Ponto(((tela_x/2)-(botao_altura)),tela_y/2)), altura= botao_altura, largura= botao_largura,)
bota2 = aroeira.Imagem(caminho=botao_path2,origem=(aroeira.Ponto(((tela_x/2)-(botao_altura)),(tela_y/2+botao_altura))), altura= botao_altura, largura= botao_largura,)
bota3 = aroeira.Imagem(caminho=botao_path3,origem=(aroeira.Ponto(((tela_x/2)-(botao_altura)),((tela_y/2+botao_altura*2)))), altura= botao_altura, largura= botao_largura,)
placeholder_botão = aroeira.Retangulo(origem=(aroeira.Ponto(((tela_x/2)-(botao_altura)),tela_y/2)),altura=botao_altura,largura=botao_largura, cor="azul")
placeholder_botão2 = aroeira.Retangulo(origem=(aroeira.Ponto(((tela_x/2)-(botao_altura)),(tela_y/2+botao_altura))),altura=botao_altura,largura=botao_largura, cor="azul")
placeholder_botão3 = aroeira.Retangulo(origem=(aroeira.Ponto(((tela_x/2)-(botao_altura)),((tela_y/2+botao_altura*2)))),altura=botao_altura,largura=botao_largura, cor="azul")
placeholder_background = aroeira.Retangulo(origem=(aroeira.Ponto(00,00)),largura=tela_x,altura=tela_y)

tela.adicionar(placeholder_background)
tela.adicionar(bota1)
tela.adicionar(bota2)
tela.adicionar(bota3)

tela.ao_clicar(clicar)
tela.ao_mover_mouse(placeholder_)
tela.animar(placeholder_a, fps=60)

tela.executar(tela_cheia=True)
