# ============================================================
#  menu.py  —  ponto de entrada do jogo:  python menu.py
# ============================================================
import os
import sys

import aroeira as ar
import configurações
import estilo
import fases
import perfis
from caminhos import pasta_dados
from cena import Aplicativo, Cena
from editor import Editor
from seletor import Seletor
from tela_perfis import TelaPerfis


class Menu(Cena):

    def entrar(self):
        a = self.app
        cx = a.largura / 2

        self.adicionar(ar.Retangulo(ar.Ponto(0, 0), a.largura, a.altura, cor="#0b132b"))
        self.adicionar(ar.Texto(ar.Ponto(cx - 175, a.altura / 2 - 260), "PEGKING", 72, "branco", True))

        jogador = perfis.atual()
        self.adicionar(ar.Texto(
            ar.Ponto(cx - 150, a.altura / 2 - 150),
            ("Jogador: " + jogador) if jogador else "Nenhum perfil criado ainda",
            20, "branco"))

        x = cx - estilo.L_MENU / 2
        y = a.altura / 2 - 80
        for i, (rotulo, acao, papel) in enumerate([
                ("Jogar", self._jogar, "primario"),
                ("Perfis", self._perfis, "neutro"),
                ("Editor de fases", self._editor, "alerta"),
                ("Sair", self._sair, "perigo")]):
            self.adicionar(estilo.botao(x, y + i * 70, rotulo, acao, papel, estilo.L_MENU))

    # ---------------- ações ----------------
    def _jogar(self):
        if perfis.atual() is None:
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
    """Executável sem console: sys.stderr é None e a Aroeira quebraria ao
    relatar um erro. Mandamos tudo para um arquivo de log ao lado do .exe."""
    if sys.stderr is None or sys.stdout is None:
        log = open(os.path.join(pasta_dados(), "pegking_erros.log"), "a", encoding="utf-8")
        if sys.stderr is None:
            sys.stderr = log
        if sys.stdout is None:
            sys.stdout = log


def principal():
    _garantir_saida_de_erros()
    tela_x, tela_y, *_ = configurações.config()
    tela = ar.Tela("Pegking", largura=tela_x, altura=tela_y, cor_fundo="#0b132b")
    app = Aplicativo(tela, tela_x, tela_y)
    app.fabrica_menu = Menu
    app.fabrica_seletor = Seletor

    fases.garantir_fases_padrao()
    app.ir_menu()

    # A Aroeira só aceita UMA função de cada tipo; o Aplicativo as repassa
    # para a cena que estiver ativa. Todas precisam ser registradas ANTES
    # do executar(), senão a Aroeira nem liga o evento correspondente.
    tela.ao_clicar(app.despachar_clique)
    tela.ao_mover_mouse(app.despachar_mouse)
    tela.ao_pressionar_tecla(app.despachar_tecla)
    tela.animar(app.despachar_animacao, fps=60)
    tela.executar(tela_cheia=True)


if __name__ == "__main__":
    principal()
