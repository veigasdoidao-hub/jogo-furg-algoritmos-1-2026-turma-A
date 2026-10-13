# ============================================================
#  cena.py  —  a base das "telas" do jogo
# ============================================================
#  A Aroeira tem UMA Tela e só aceita UMA função de clique, UMA de
#  mouse, UMA de teclado e UMA de animação. Para ter menu, seletor,
#  editor e jogo no mesmo programa, cada um desses vira uma CENA, e o
#  Aplicativo repassa os eventos para a cena que estiver ativa.
#
#  Trocar de cena = remover tudo que a cena antiga colocou na tela e
#  deixar a nova colocar o que ela precisa.
# ============================================================
import os
import subprocess
import sys
import threading

import aroeira as ar


class Cena:
    """Base das cenas. Quem herdar sobrescreve só o que precisar."""

    def __init__(self, app):
        self.app = app
        self.tela = app.tela
        self.ativa = False          # o Aplicativo liga/desliga
        self.dialogo_aberto = False
        self._elementos = []

    # ---------------- ganchos (sobrescreva) ----------------
    def entrar(self):
        """Monta a cena: crie e adicione os elementos aqui."""

    def sair(self):
        """Desmonta a cena. O padrão já remove tudo que foi adicionado."""
        self.ativa = False
        self.limpar()

    def ao_clicar(self, ponto): pass
    def ao_mover_mouse(self, ponto): pass
    def ao_tecla(self, nome): pass
    def atualizar(self): pass

    # ---------------- elementos ----------------
    def adicionar(self, elemento):
        """Como tela.adicionar, mas a cena lembra o elemento para limpá-lo depois."""
        self.tela.adicionar(elemento)
        self._elementos.append(elemento)
        return elemento

    def remover(self, elemento):
        if elemento in self._elementos:
            self._elementos.remove(elemento)
            self.tela.remover(elemento)

    def limpar(self):
        for elemento in list(self._elementos):
            self.tela.remover(elemento)
        self._elementos.clear()

    # ---------------- diálogos ----------------
    def avisar(self, titulo, mensagem, depois=None):
        """Janelinha com um OK. `depois` (opcional) roda quando o OK é clicado."""
        self.dialogo_aberto = True

        def fechou():
            self.dialogo_aberto = False
            if depois:
                depois()

        self.tela.mostrar_dialogo(
            ar.CaixaDeDialogo(titulo, mensagem, ao_confirmar=fechou))

    def perguntar(self, titulo, mensagem, se_sim):
        """Janelinha Sim/Não. `se_sim` roda só se a resposta for Sim."""
        self.dialogo_aberto = True

        def resposta(sim):
            self.dialogo_aberto = False
            if sim:
                se_sim()

        self.tela.mostrar_dialogo(
            ar.CaixaDeDialogo(titulo, mensagem, modo="confirmacao",
                              ao_confirmar=resposta))


    def pedir_texto(self, titulo, mensagem, ao_receber, valor=""):
        """Janelinha com um campo de texto. `ao_receber(texto)` roda no OK."""
        self.dialogo_aberto = True

        def recebeu(texto):
            self.dialogo_aberto = False
            ao_receber(texto)

        self.tela.mostrar_dialogo(
            ar.CaixaDeDialogo(titulo, mensagem, modo="entrada",
                              ao_confirmar=recebeu, valor=valor))


def _matar_processo():
    """Último recurso: derruba o programa e o cliente gráfico dele (filho)."""
    if sys.platform == "win32":
        try:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(os.getpid())],
                           capture_output=True, creationflags=0x08000000)
        except Exception:
            pass
    os._exit(0)


class Aplicativo:
    """Guarda a Tela e a cena atual, e repassa os eventos para ela."""

    def __init__(self, tela, largura, altura):
        self.tela = tela
        self.largura = largura
        self.altura = altura
        self.cena = None
        # Preenchidos pelo menu.py (evita importações circulares):
        self.fabrica_menu = None
        self.fabrica_seletor = None
        self.forcar_saida = _matar_processo      # trocável em testes

    def ir_para(self, nova):
        antiga, self.cena = self.cena, None     # None: pausa os eventos na troca
        if antiga is not None:
            antiga.sair()
        nova.ativa = True
        nova.entrar()
        self.cena = nova

    def ir_menu(self):
        self.ir_para(self.fabrica_menu(self))

    def ir_seletor(self):
        self.ir_para(self.fabrica_seletor(self))

    def encerrar(self):
        """Fecha o jogo de verdade.

        tela.fechar() pede à janela que se destrua, mas em tela cheia esse
        pedido pode ficar sem resposta e a janela só congela. Por isso, se
        o programa ainda estiver vivo 0,8 s depois, ele é derrubado à força.
        Os dados (perfis, fases) já são gravados no instante em que mudam,
        então nada se perde.
        """
        try:
            self.tela.fechar()
        except Exception:
            pass
        espera = threading.Timer(0.8, self.forcar_saida)
        espera.daemon = True        # se o programa fechar sozinho antes, some junto
        espera.start()

    # Estas quatro são as funções que vão para a Aroeira (uma vez só).
    def despachar_clique(self, ponto):
        if self.cena:
            self.cena.ao_clicar(ponto)

    def despachar_mouse(self, ponto):
        if self.cena:
            self.cena.ao_mover_mouse(ponto)

    def despachar_tecla(self, nome):
        if self.cena:
            self.cena.ao_tecla(nome)

    def despachar_animacao(self):
        if self.cena:
            self.cena.atualizar()
