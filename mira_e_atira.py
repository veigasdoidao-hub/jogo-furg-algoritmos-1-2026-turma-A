import aroeira as ar
import math as mat
import random as rd

#tela
#(fazer resoluções selecionaveis no menu e linkar aqui)
tamanho_tela_x = 1400
tamanho_tela_y = 800
tela = ar.Tela("pegking", tamanho_tela_x, tamanho_tela_y, "cinza")

#tentativa do lançador
corpo = ar.Circulo(ar.Ponto(tamanho_tela_x // 2,0),75,"vermelho")
inicio_mira = ar.Ponto(tamanho_tela_x // 2,0)
fim_mira = ar.Ponto(tamanho_tela_x // 2,75)
mira = ar.Linha(inicio=inicio_mira, fim=fim_mira, cor="preto", espessura=4)

def clicou(ponto):
    global fim_mira
    fim_mira.x = ponto.x
    fim_mira.y = ponto.y
    vetor_mira = ar.Ponto(fim_mira.x - inicio_mira.x, fim_mira.y - inicio_mira.y)
    tamanho_vetor_mira = mat.sqrt(vetor_mira.x**2 + vetor_mira.y**2)
    vetor_mira_normalizado = ar.Ponto(vetor_mira.x / tamanho_vetor_mira, vetor_mira.y / tamanho_vetor_mira)
    fim_mira.x = inicio_mira.x + (vetor_mira_normalizado.x * 75)
    fim_mira.y = inicio_mira.y + (vetor_mira_normalizado.y * 75)
    mira.fim = fim_mira

#projetil
velocidade_projetil_x = 1
velocidade_projetil_y = 3
projeteis = []

def tiro(tiro):
    if tiro == ' ':
        projetil = ar.Circulo(ar.Ponto(fim_mira.x, fim_mira.y), 5, cor="preto")
        projeteis.append(projetil)
        tela.adicionar(projetil)

def atualizar():
    for projetil in projeteis:
        projetil.mover(dx=velocidade_projetil_x, dy=velocidade_projetil_y)
        if projetil.y > tamanho_tela_y or projetil.x > tamanho_tela_x:
            tela.remover(projetil)
            projeteis.remove(projetil)

#ordens
tela.ao_clicar(clicou)
tela.adicionar(corpo)
tela.adicionar(mira)
tela.ao_pressionar_tecla(tiro)
tela.animar(atualizar, fps=60)
tela.executar()