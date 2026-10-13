# ============================================================
#  tela_perfis.py  —  criar, escolher e excluir perfis
# ============================================================
import math

import aroeira as ar
import estilo
import perfis
from cena import Cena

POR_PAGINA = 6


class TelaPerfis(Cena):

    def entrar(self):
        L, A = self.app.largura, self.app.altura
        self.x0 = L / 2 - 300
        self._pagina = 0
        self._itens = []

        self.adicionar(ar.Retangulo(ar.Ponto(0, 0), L, A, cor="#0b132b"))
        self.adicionar(ar.Texto(ar.Ponto(L / 2 - 80, 40), "Perfis", 44, "branco", True))
        self.adicionar(ar.Texto(ar.Ponto(self.x0, 105),
                                "Clique num perfil para jogar com ele.", 18, "branco"))

        y_nav = 140 + POR_PAGINA * 70 + 20
        self.adicionar(estilo.botao(self.x0, y_nav, "Anterior", self._anterior,
                                    "neutro", estilo.L_NAV))
        self._t_pagina = self.adicionar(ar.Texto(ar.Ponto(L / 2 - 30, y_nav + 8), "", 20, "branco"))
        self.adicionar(estilo.botao(self.x0 + 440, y_nav, "Próxima", self._proxima,
                                    "neutro", estilo.L_NAV))

        y_fim = y_nav + 80
        self.adicionar(estilo.botao(self.x0, y_fim, "Novo perfil", self._novo, "sucesso", 220))
        self.adicionar(estilo.botao(self.x0 + 380, y_fim, "Voltar ao menu",
                                    self.app.ir_menu, "neutro", 220))
        self._montar()

    def _montar(self):
        for item in self._itens:
            self.remover(item)
        self._itens = []

        nomes = perfis.listar()
        ativo = perfis.atual()
        total = max(1, math.ceil(len(nomes) / POR_PAGINA))
        self._pagina = min(self._pagina, total - 1)
        self._t_pagina.conteudo = "%d / %d" % (self._pagina + 1, total)

        if not nomes:
            self._item(ar.Texto(ar.Ponto(self.x0, 150),
                                "Nenhum perfil ainda. Crie o seu em 'Novo perfil'!",
                                22, "branco"))
            return

        inicio = self._pagina * POR_PAGINA
        for i, nome in enumerate(nomes[inicio:inicio + POR_PAGINA]):
            y = 140 + i * 70
            n = perfis.quantos_recordes(nome)
            rotulo = ("> " if nome == ativo else "   ") + nome + "   (%d recorde%s)" % (
                n, "" if n == 1 else "s")
            self._item(estilo.botao(self.x0, y, rotulo, lambda p=nome: self._escolher(p),
                                    "primario" if nome == ativo else "neutro", 440))
            self._item(estilo.botao(self.x0 + 460, y, "Excluir", lambda p=nome: self._excluir(p),
                                    "perigo", estilo.L_PEQUENO))

    def _item(self, elemento):
        self._itens.append(self.adicionar(elemento))

    def _anterior(self):
        if self._pagina > 0:
            self._pagina -= 1
            self._montar()

    def _proxima(self):
        self._pagina += 1
        self._montar()

    # ---------------- ações ----------------
    def _escolher(self, nome):
        perfis.definir_atual(nome)
        self._montar()

    def _novo(self):
        self.pedir_texto("Novo perfil",
                         "Nome do jogador (até %d letras).\nDeixe em branco e clique OK para cancelar."
                         % perfis.TAMANHO_MAX_NOME,
                         self._criar)

    def _criar(self, texto):
        if not texto.strip():
            return                                  # em branco = cancelar
        try:
            perfis.criar(texto)
        except ValueError as erro:
            self.avisar("Perfil", str(erro))
            return
        if self.ativa:
            self._montar()

    def _excluir(self, nome):
        def apagar():
            perfis.excluir(nome)
            if self.ativa:
                self._montar()

        self.perguntar("Excluir perfil",
                       'Excluir o perfil "%s" e todos os recordes dele?' % nome, apagar)

    def ao_tecla(self, nome):
        if nome == "Escape" and not self.dialogo_aberto:
            self.app.ir_menu()
