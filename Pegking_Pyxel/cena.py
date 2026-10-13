import textwrap

import pyxel

import estilo
from estilo import ALTURA, LARGURA, ALTURA_BOTAO


def _quebrar(mensagem, largura):
    saida = []
    for linha in str(mensagem).split("\n"):
        saida.extend(textwrap.wrap(linha, largura) or [""])
    return saida


class Dialogo:

    LARGURA = 208

    def __init__(self, titulo="", mensagem="", modo="mensagem",
                 ao_confirmar=None, valor="", maximo=40):
        if modo not in ("mensagem", "confirmacao", "entrada"):
            raise ValueError("modo inválido: %r" % (modo,))
        self.titulo, self.modo = titulo, modo
        self.ao_confirmar = ao_confirmar
        self.valor, self.maximo = str(valor), maximo
        self.app = None

        self.linhas = _quebrar(mensagem, (self.LARGURA - 16) // 4)
        h = 8 + 12 + len(self.linhas) * 7 + 6
        if modo == "entrada":
            h += 16
        h += ALTURA_BOTAO + 8
        self.altura = h
        self.x = (LARGURA - self.LARGURA) // 2
        self.y = (ALTURA - h) // 2

        yb = self.y + h - 8 - ALTURA_BOTAO
        cx = self.x + self.LARGURA // 2
        if modo == "confirmacao":
            self.botoes = [
                estilo.botao(cx - 44, yb, "Sim", lambda: self._responder(True), "sucesso", 40),
                estilo.botao(cx + 4, yb, "Não", lambda: self._responder(False), "perigo", 40)]
        else:
            self.botoes = [estilo.botao(cx - 20, yb, "OK", lambda: self._responder(None),
                                        "primario", 40)]

    def _responder(self, valor):
        self.app.dialogo = None
        if not self.ao_confirmar:
            return
        if self.modo == "entrada":
            self.ao_confirmar(self.valor)
        elif self.modo == "confirmacao":
            self.ao_confirmar(valor)
        else:
            self.ao_confirmar()

    def _cancelar(self):
        self.app.dialogo = None

    def atualizar(self, mx, my, clique):
        if self.modo == "entrada":
            self.valor = (self.valor + estilo.digitado())[:self.maximo]
            if estilo.apagou():
                self.valor = self.valor[:-1]
            if pyxel.btnp(pyxel.KEY_RETURN):
                return self._responder(None)
            if pyxel.btnp(pyxel.KEY_ESCAPE):
                return self._cancelar()
        elif self.modo == "mensagem":
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_ESCAPE):
                return self._responder(None)
        elif pyxel.btnp(pyxel.KEY_ESCAPE):
            return self._responder(False)

        if clique:
            for b in self.botoes:
                if b.contem(mx, my):
                    b.acao()
                    return

    def desenhar(self):
        pyxel.dither(0.5)
        pyxel.rect(0, 0, LARGURA, ALTURA, estilo.PRETO)
        pyxel.dither(1.0)
        pyxel.rect(self.x, self.y, self.LARGURA, self.altura, estilo.AZUL_ESCURO)
        pyxel.rectb(self.x, self.y, self.LARGURA, self.altura, estilo.CINZA)
        estilo.negrito(self.x + 8, self.y + 8, self.titulo)
        y = self.y + 8 + 12
        for linha in self.linhas:
            estilo.escrever(self.x + 8, y, linha, estilo.AZUL_CLARO)
            y += 7
        if self.modo == "entrada":
            y += 4
            larg = self.LARGURA - 16
            pyxel.rect(self.x + 8, y, larg, 12, estilo.PRETO)
            pyxel.rectb(self.x + 8, y, larg, 12, estilo.AZUL)
            visivel = estilo.limpar(self.valor)[-((larg - 8) // 4 - 1):]
            cursor = "_" if (pyxel.frame_count // 15) % 2 == 0 else " "
            estilo.escrever(self.x + 12, y + 3, visivel + cursor, estilo.BRANCO)
        for b in self.botoes:
            b.desenhar()


class Cena:

    def __init__(self, app):
        self.app = app
        self.ativa = False
        self.botoes = []

    @property
    def dialogo_aberto(self):
        return self.app.dialogo is not None

    def entrar(self):
        pass

    def sair(self):
        self.ativa = False
        self.botoes.clear()

    def ao_mover_mouse(self, x, y): pass
    def ao_tecla(self, nome): pass
    def atualizar(self): pass

    def ao_clicar(self, x, y):
        for b in reversed(list(self.botoes)):
            if b.visivel and b.ativo and b.contem(x, y):
                b.acao()
                return True
        return False

    def desenhar(self):
        pyxel.cls(estilo.PRETO)
        self.desenhar_botoes()

    def adicionar(self, botao):
        self.botoes.append(botao)
        return botao

    def remover(self, botao):
        if botao in self.botoes:
            self.botoes.remove(botao)

    def desenhar_botoes(self):
        hover = not self.dialogo_aberto
        for b in self.botoes:
            b.desenhar(hover)

    def avisar(self, titulo, mensagem, depois=None):
        self.app.mostrar_dialogo(Dialogo(titulo, mensagem, "mensagem", depois))

    def perguntar(self, titulo, mensagem, se_sim):
        def resposta(sim):
            if sim:
                se_sim()
        self.app.mostrar_dialogo(Dialogo(titulo, mensagem, "confirmacao", resposta))

    def pedir_texto(self, titulo, mensagem, ao_receber, valor="", maximo=40):
        self.app.mostrar_dialogo(Dialogo(titulo, mensagem, "entrada", ao_receber,
                                         valor, maximo))


class Aplicativo:

    def __init__(self):
        self.largura = LARGURA
        self.altura = ALTURA
        self.cena = None
        self.dialogo = None
        self.fabrica_menu = None
        self.fabrica_seletor = None

    def ir_para(self, nova):
        antiga, self.cena = self.cena, None
        self.dialogo = None
        if antiga is not None:
            antiga.sair()
        nova.ativa = True
        nova.entrar()
        self.cena = nova

    def ir_menu(self):
        self.ir_para(self.fabrica_menu(self))

    def ir_seletor(self):
        self.ir_para(self.fabrica_seletor(self))

    def mostrar_dialogo(self, dialogo):
        dialogo.app = self
        self.dialogo = dialogo

    def encerrar(self):
        pyxel.quit()

    def atualizar(self):
        cena = self.cena
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        clique = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)

        if self.dialogo is not None:
            self.dialogo.atualizar(mx, my, clique)
            if cena is not None and self.cena is cena:
                cena.atualizar()
            return
        if cena is None:
            return

        cena.ao_mover_mouse(mx, my)
        if clique:
            cena.ao_clicar(mx, my)
        if self.cena is not cena:
            return
        if self.dialogo is None and pyxel.btnp(pyxel.KEY_ESCAPE):
            cena.ao_tecla("Escape")
            if self.cena is not cena:
                return
        cena.atualizar()

    def desenhar(self):
        if self.cena is not None:
            self.cena.desenhar()
        if self.dialogo is not None:
            self.dialogo.desenhar()
