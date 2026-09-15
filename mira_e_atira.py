import aroeira as ar
import math as mat
import configurações 

def colidiu(projetil, alvo):
    distancia_x = projetil.x - alvo.x
    distancia_y = projetil.y - alvo.y
    distancia = mat.sqrt(distancia_x ** 2 + distancia_y ** 2)
    return distancia <= projetil.raio + alvo.raio

class Jogo:
    def __init__(self):
        deus="morto"
    def jogar(tela):  
        global fim_mira, angulo,mira,inicio_mira,corpo,velocidade_x,velocidade_y
        tela_x,tela_y,a,b,c= configurações.config()
        corpo = ar.Circulo(ar.Ponto(tela_x // 2,0),75,"vermelho")
        alvo = ar.Circulo(ar.Ponto(tela_x * 3 // 4, tela_y // 2),30,"azul")
        inicio_mira = ar.Ponto(tela_x // 2,0)
        fim_mira = ar.Ponto(tela_x // 2,75)
        mira = ar.Linha(inicio=inicio_mira, fim=fim_mira, cor="preto", espessura=4)
        angulo = mat.atan2(fim_mira.y - inicio_mira.y,fim_mira.x - inicio_mira.x)
        gravidade = 0.2
        
        def mouse_track(posição):
            global fim_mira, angulo
            fim_mira.x = posição.x
            fim_mira.y = posição.y
            vetor_x = fim_mira.x - inicio_mira.x
            vetor_y = fim_mira.y - inicio_mira.y
            tamanho_vetor = mat.sqrt(vetor_x**2 + vetor_y**2)
            fim_mira.x = inicio_mira.x + (vetor_x / tamanho_vetor) * 75
            fim_mira.y = inicio_mira.y + (vetor_y / tamanho_vetor) * 75
            mira.fim = fim_mira
            if tamanho_vetor == 0:
                return
            if len(projeteis) == 0:
                atualizar_angulo()
        velocidade_projetil = 8
        gravidade = 0.1
        velocidade_x = 0
        velocidade_y = 0
        projeteis = []
    
        def atualizar_angulo():
            global angulo
            angulo = mat.atan2(fim_mira.y - inicio_mira.y,fim_mira.x - inicio_mira.x)       
    
        def atualizar():
            global velocidade_y
            for projetil in projeteis:
                velocidade_y += gravidade
                projetil.mover(velocidade_x, velocidade_y)
                if colidiu(projetil, alvo):
                    alvo.cor = "verde"
                    tela.remover(projetil)
                    projeteis.remove(projetil)
                    atualizar_angulo()
                    continue
                saiu_da_tela = (projetil.y > tela_y or projetil.y < 0 or projetil.x > tela_x or projetil.x < 0)
                if saiu_da_tela:
                    tela.remover(projetil)
                    projeteis.remove(projetil)
                    atualizar_angulo()

        class bala:
                def atirar(tiro):
                    global angulo,fim_mira,velocidade_x,velocidade_y
                    if len(projeteis) == 0:
                        projetil = ar.Circulo(ar.Ponto(fim_mira.x, fim_mira.y), 10, cor="preto")
                        velocidade_x = velocidade_projetil * mat.cos(angulo)
                        velocidade_y = velocidade_projetil * mat.sin(angulo)
                        projeteis.append(projetil)
                        tela.adicionar(projetil)
                        return True       
 
        tela.ao_mover_mouse(mouse_track)
        tela.adicionar(corpo)
        tela.adicionar(alvo)
        tela.adicionar(mira)
        tela.ao_clicar(bala.atirar)
        tela.animar(atualizar, fps=100)
