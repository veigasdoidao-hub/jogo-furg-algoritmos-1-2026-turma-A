# ============================================================
#  estilo.py  —  o visual padrão dos botões
# ============================================================
#  Todo botão do jogo nasce daqui, então todos têm a mesma cara.
#  Para mudar uma cor do jogo inteiro, mude aqui.
#
#  Papéis:  primario (ação principal)     sucesso (confirmar/criar)
#           perigo   (apagar/excluir)     neutro  (voltar/cancelar)
#           alerta   (reiniciar/editar)   destaque (testar)
# ============================================================
import aroeira as ar

PAPEIS = {
    "primario": "azul",
    "sucesso":  "verde",
    "perigo":   "vermelho",
    "neutro":   "cinza",
    "alerta":   "laranja",
    "destaque": "roxo",
}

L_MENU = 300      # botões do menu principal
L_PAINEL = 210    # botões dos painéis laterais (jogo e editor)
L_LINHA = 440     # botão grande de uma linha de lista
L_PEQUENO = 130   # botões de ação ao lado, nas listas
L_NAV = 160       # anterior / próxima


def botao(x, y, rotulo, acao, papel="primario", largura=L_PAINEL):
    return ar.Botao(ar.Ponto(x, y), rotulo, acao,
                    cor=PAPEIS[papel], cor_texto="branco", largura=largura)
