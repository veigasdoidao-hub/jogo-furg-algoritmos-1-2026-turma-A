# ============================================================
#  seletor.py  —  escolher a fase (jogar, editar ou excluir)
# ============================================================
import math

import aroeira as ar
import estilo
import fases
import perfis
from cena import Cena
from editor import Editor
from mira_e_atira import Jogo

POR_PAGINA = 6


class Seletor(Cena):

    def entrar(self):
        L, A = self.app.largura, self.app.altura
        self.x0 = L / 2 - 360
        self._pagina = 0
        self._itens = []        # botões da página atual (refeitos a cada troca)
        self.perfil = perfis.atual()

        self.adicionar(ar.Retangulo(ar.Ponto(0, 0), L, A, cor="#0b132b"))
        self.adicionar(ar.Texto(ar.Ponto(L / 2 - 175, 40), "Selecione a fase", 44, "branco", True))
        quem = ("Jogador: " + self.perfil) if self.perfil else "Sem perfil: recordes não serão salvos"
        self.adicionar(ar.Texto(ar.Ponto(self.x0, 105), quem, 18, "branco"))

        y_nav = 140 + POR_PAGINA * 70 + 20
        self.adicionar(estilo.botao(self.x0, y_nav, "Anterior", self._anterior,
                                    "neutro", estilo.L_NAV))
        self._t_pagina = self.adicionar(ar.Texto(ar.Ponto(L / 2 - 30, y_nav + 8), "", 20, "branco"))
        self.adicionar(estilo.botao(self.x0 + 560, y_nav, "Próxima", self._proxima,
                                    "neutro", estilo.L_NAV))

        y_fim = y_nav + 80
        self.adicionar(estilo.botao(self.x0, y_fim, "Nova fase", self._nova, "sucesso", 220))
        self.adicionar(estilo.botao(self.x0 + 500, y_fim, "Voltar ao menu",
                                    self.app.ir_menu, "neutro", 220))
        self._montar()

    # ---------------- lista ----------------
    def _montar(self):
        for item in self._itens:
            self.remover(item)
        self._itens = []

        lista = fases.listar()
        total = max(1, math.ceil(len(lista) / POR_PAGINA))
        self._pagina = min(self._pagina, total - 1)
        self._t_pagina.conteudo = "%d / %d" % (self._pagina + 1, total)

        if not lista:
            self._item(ar.Texto(ar.Ponto(self.x0, 150),
                                "Nenhuma fase encontrada. Crie uma com 'Nova fase'!",
                                22, "branco"))
            return

        inicio = self._pagina * POR_PAGINA
        for i, fase in enumerate(lista[inicio:inicio + POR_PAGINA]):
            y = 140 + i * 70
            rotulo = "%d. %s" % (inicio + i + 1, fase["nome"][:20])
            recorde = perfis.recorde(self.perfil, fase["arquivo"]) if self.perfil else 0
            if recorde:
                rotulo += "   (recorde: %d)" % recorde
            self._item(estilo.botao(self.x0, y, rotulo, lambda f=fase: self._jogar(f),
                                    "primario", estilo.L_LINHA))
            self._item(estilo.botao(self.x0 + 460, y, "Editar", lambda f=fase: self._editar(f),
                                    "alerta", estilo.L_PEQUENO))
            self._item(estilo.botao(self.x0 + 600, y, "Excluir", lambda f=fase: self._excluir(f),
                                    "perigo", 120))

    def _item(self, elemento):
        self._itens.append(self.adicionar(elemento))

    def _anterior(self):
        if self._pagina > 0:
            self._pagina -= 1
            self._montar()

    def _proxima(self):
        self._pagina += 1          # _montar corrige se passou da última
        self._montar()

    # ---------------- ações ----------------
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
        if nome == "Escape" and not self.dialogo_aberto:
            self.app.ir_menu()
