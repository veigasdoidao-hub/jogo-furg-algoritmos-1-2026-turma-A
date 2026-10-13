import math

import pyxel

import estilo
import fases
import perfis
from cena import Cena
from editor import Editor
from estilo import LARGURA
from mira_e_atira import Jogo

POR_PAGINA = 6


class Seletor(Cena):

    def entrar(self):
        estilo.preparar_texto_grande("Selecione a fase")
        self.x0 = 14
        self._pagina = 0
        self._itens = []
        self.perfil = perfis.atual()
        self._total = 1

        y_nav = 36 + POR_PAGINA * 14 + 6
        self.adicionar(estilo.botao(self.x0, y_nav, "Anterior", self._anterior, "neutro", 52))
        self.adicionar(estilo.botao(LARGURA - self.x0 - 52, y_nav, "Próxima", self._proxima,
                                    "neutro", 52))
        y_fim = y_nav + 22
        self.adicionar(estilo.botao(self.x0, y_fim, "Nova fase", self._nova, "sucesso", 70))
        self.adicionar(estilo.botao(LARGURA - self.x0 - 90, y_fim, "Voltar ao menu",
                                    self.app.ir_menu, "neutro", 90))
        self._y_nav = y_nav
        self._montar()

    def _montar(self):
        for item in self._itens:
            self.remover(item)
        self._itens = []

        self._lista = fases.listar()
        recordes = perfis.recordes(self.perfil) if self.perfil else {}
        self._total = max(1, math.ceil(len(self._lista) / POR_PAGINA))
        self._pagina = min(self._pagina, self._total - 1)

        if not self._lista:
            return

        inicio = self._pagina * POR_PAGINA
        x = self.x0
        for i, fase in enumerate(self._lista[inicio:inicio + POR_PAGINA]):
            y = 36 + i * 14
            rotulo = "%d. %s" % (inicio + i + 1, fase["nome"][:16])
            recorde = recordes.get(fase["arquivo"], 0)
            if recorde:
                rotulo += " (rec:%d)" % recorde
            self._item(estilo.botao(x, y, rotulo, lambda f=fase: self._jogar(f),
                                    "primario", 132))
            self._item(estilo.botao(x + 136, y, "Editar", lambda f=fase: self._editar(f),
                                    "alerta", 44))
            self._item(estilo.botao(x + 184, y, "Excluir", lambda f=fase: self._excluir(f),
                                    "perigo", 44))

    def _item(self, botao):
        self._itens.append(self.adicionar(botao))

    def _anterior(self):
        if self._pagina > 0:
            self._pagina -= 1
            self._montar()

    def _proxima(self):
        self._pagina += 1
        self._montar()

    def _jogar(self, fase):
        self.app.ir_para(Jogo(self.app, fase, voltar=self.app.ir_seletor))

    def _editar(self, fase):
        self.app.ir_para(Editor(self.app, fase))

    def _nova(self):
        self.app.ir_para(Editor(self.app))

    def _excluir(self, fase):
        def apagar():
            fases.excluir(fase["arquivo"])
            perfis.esquecer_fase(fase["arquivo"])
            if self.ativa:
                self._montar()

        self.perguntar("Excluir fase", 'Excluir "%s" para sempre?\n(Os recordes dela também somem.)'
                       % fase["nome"], apagar)

    def ao_tecla(self, nome):
        if nome == "Escape":
            self.app.ir_menu()

    def desenhar(self):
        pyxel.cls(estilo.PRETO)
        estilo.texto_grande(LARGURA // 2, 8, "Selecione a fase", estilo.BRANCO, 2)
        quem = ("Jogador: " + self.perfil) if self.perfil else "Sem perfil: recordes não serão salvos"
        estilo.escrever(self.x0, 24, quem, estilo.AZUL_CLARO)
        if not self._lista:
            estilo.escrever(self.x0, 40, "Nenhuma fase encontrada.", estilo.BRANCO)
            estilo.escrever(self.x0, 48, "Crie uma com 'Nova fase'!", estilo.BRANCO)
        estilo.centralizar(self._y_nav + 3, "%d / %d" % (self._pagina + 1, self._total),
                           estilo.BRANCO)
        self.desenhar_botoes()
