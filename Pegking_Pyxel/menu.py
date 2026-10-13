import os
import sys
import traceback

import pyxel

import estilo
import fases
import perfis
from caminhos import pasta_dados
from cena import Aplicativo, Cena
from editor import Editor
from estilo import LARGURA, ALTURA
from seletor import Seletor
from tela_perfis import TelaPerfis


FUNDO = [(col * 22 + (11 if linha % 2 else 0), 12 + linha * 34)
         for linha in range(6) for col in range(13)]


class Menu(Cena):

    def entrar(self):
        self.jogador = perfis.atual()
        estilo.preparar_texto_grande("PEGKING")
        cx = LARGURA // 2
        x = cx - 40
        y = 84
        for i, (rotulo, acao, papel) in enumerate([
                ("Jogar", self._jogar, "primario"),
                ("Perfis", self._perfis, "neutro"),
                ("Editor de fases", self._editor, "alerta"),
                ("Sair", self._sair, "perigo")]):
            self.adicionar(estilo.botao(x, y + i * 22, rotulo, acao, papel, 80, 16))

    def desenhar(self):
        pyxel.cls(estilo.PRETO)
        for x, y in FUNDO:
            pyxel.circ(x, y, 5, estilo.AZUL_ESCURO)
        estilo.texto_grande(LARGURA // 2, 24, "PEGKING", estilo.AZUL_MEDIO, 4)

        estilo.centralizar(64, ("Jogador: " + self.jogador) if self.jogador else "Nenhum perfil criado ainda",
                           estilo.BRANCO)
        estilo.centralizar(ALTURA - 8, "Alt+Enter: tela cheia", estilo.CINZA)
        self.desenhar_botoes()

    def _jogar(self):
        if self.jogador is None:
            self.avisar("Perfil", "Crie um perfil para jogar: é nele que seus recordes ficam salvos.",
                        depois=self._perfis)
        else:
            self.app.ir_seletor()

    def _perfis(self):
        self.app.ir_para(TelaPerfis(self.app))

    def _editor(self):
        self.app.ir_para(Editor(self.app))

    def _sair(self):
        self.app.encerrar()


def _garantir_saida_de_erros():
    if sys.stderr is None or sys.stdout is None:
        log = open(os.path.join(pasta_dados(), "pegking_erros.log"), "a", encoding="utf-8")
        if sys.stderr is None:
            sys.stderr = log
        if sys.stdout is None:
            sys.stdout = log


def principal():
    _garantir_saida_de_erros()
    pyxel.init(LARGURA, ALTURA, title="Pegking", fps=60, quit_key=pyxel.KEY_NONE)
    pyxel.mouse(True)
    if hasattr(pyxel, "fullscreen"):
        pyxel.fullscreen(True)

    app = Aplicativo()
    app.fabrica_menu = Menu
    app.fabrica_seletor = Seletor

    fases.garantir_fases_padrao()
    app.ir_menu()
    try:
        pyxel.run(app.atualizar, app.desenhar)
    except Exception:
        traceback.print_exc()
        raise


if __name__ == "__main__":
    principal()
