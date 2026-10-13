import math

import pyxel

import estilo
import perfis
from cena import Cena
from estilo import LARGURA

POR_PAGINA = 6


class TelaPerfis(Cena):

    def entrar(self):
        estilo.preparar_texto_grande("Perfis")
        self.x0 = 24
        self._pagina = 0
        self._itens = []
        self._total = 1

        y_nav = 36 + POR_PAGINA * 14 + 6
        self.adicionar(estilo.botao(self.x0, y_nav, "Anterior", self._anterior, "neutro", 52))
        self.adicionar(estilo.botao(LARGURA - self.x0 - 52, y_nav, "Próxima", self._proxima,
                                    "neutro", 52))
        y_fim = y_nav + 22
        self.adicionar(estilo.botao(self.x0, y_fim, "Novo perfil", self._novo, "sucesso", 70))
        self.adicionar(estilo.botao(LARGURA - self.x0 - 90, y_fim, "Voltar ao menu",
                                    self.app.ir_menu, "neutro", 90))
        self._y_nav = y_nav
        self._montar()

    def _montar(self):
        for item in self._itens:
            self.remover(item)
        self._itens = []

        ativo, itens = perfis.resumo()
        self._nomes = [nome for nome, _ in itens]
        contagem = dict(itens)
        self._total = max(1, math.ceil(len(self._nomes) / POR_PAGINA))
        self._pagina = min(self._pagina, self._total - 1)

        if not self._nomes:
            return

        inicio = self._pagina * POR_PAGINA
        for i, nome in enumerate(self._nomes[inicio:inicio + POR_PAGINA]):
            y = 36 + i * 14
            n = contagem[nome]
            rotulo = ("> " if nome == ativo else "  ") + nome + " (%d recorde%s)" % (
                n, "" if n == 1 else "s")
            self._item(estilo.botao(self.x0, y, rotulo, lambda p=nome: self._escolher(p),
                                    "primario" if nome == ativo else "neutro", 150))
            self._item(estilo.botao(self.x0 + 156, y, "Excluir", lambda p=nome: self._excluir(p),
                                    "perigo", 52))

    def _item(self, botao):
        self._itens.append(self.adicionar(botao))

    def _anterior(self):
        if self._pagina > 0:
            self._pagina -= 1
            self._montar()

    def _proxima(self):
        self._pagina += 1
        self._montar()

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
            return
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
        if nome == "Escape":
            self.app.ir_menu()

    def desenhar(self):
        pyxel.cls(estilo.PRETO)
        estilo.texto_grande(LARGURA // 2, 8, "Perfis", estilo.BRANCO, 2)
        estilo.escrever(self.x0, 24, "Clique num perfil para jogar com ele.", estilo.AZUL_CLARO)
        if not self._nomes:
            estilo.escrever(self.x0, 40, "Nenhum perfil ainda.", estilo.BRANCO)
            estilo.escrever(self.x0, 48, "Crie o seu em 'Novo perfil'!", estilo.BRANCO)
        estilo.centralizar(self._y_nav + 3, "%d / %d" % (self._pagina + 1, self._total),
                           estilo.BRANCO)
        self.desenhar_botoes()
