import math

import pyxel

import estilo
import fases
from cena import Cena
from estilo import ALTURA, LARGURA, Vista
from fases import CAMPO_L, CAMPO_A, RAIO_PEG, Y_MIN_PEG, BOLAS_PADRAO, BOLAS_MAX
from mira_e_atira import Jogo, Peg, RAIO_CANHAO

NOMES = {"azul": "peg azul", "laranja": "peg laranja", "apagar": "apagar"}
COR_CURSOR = {"azul": estilo.AZUL_MEDIO, "laranja": estilo.LARANJA, "apagar": estilo.VERMELHO}

PAINEL = 64
CAMPO_PX = LARGURA - PAINEL
VISTA = Vista(PAINEL, 0, CAMPO_PX / CAMPO_L)
CAMPO_ALT_PX = VISTA.sy(CAMPO_A)


class Editor(Cena):

    def __init__(self, app, fase=None, sujo=False):
        super().__init__(app)
        if fase is None:
            fase = {"nome": "Nova fase", "bolas": BOLAS_PADRAO, "ordem": 1000,
                    "arquivo": None, "pegs": []}
        self.fase = fase
        self.arquivo = fase.get("arquivo")
        self.ordem = fase.get("ordem", 1000)
        self.bolas = fase["bolas"]
        self.nome = fase["nome"]
        self.ferramenta = "azul"
        self.pegs = []
        self._sujo = sujo
        self.cursor = None

    def entrar(self):
        for d in self.fase["pegs"]:
            self.pegs.append(Peg(d["x"], d["y"], d["tipo"]))

        b = self._botao
        b(4, 14, "Peg azul", lambda: self._escolher("azul"), "primario")
        b(4, 27, "Peg laranja", lambda: self._escolher("laranja"), "alerta")
        b(4, 40, "Apagar", lambda: self._escolher("apagar"), "perigo")
        b(4, 53, "Limpar tudo", self._limpar_tudo, "neutro")
        b(4, ALTURA - 41, "Testar", self._testar, "destaque")
        b(4, ALTURA - 28, "Salvar", self._salvar, "sucesso")
        b(4, ALTURA - 15, "Voltar", self._voltar, "neutro")

        self._b_nome = b(PAINEL + 30, CAMPO_ALT_PX + 4, self.nome, self._pedir_nome,
                         "neutro", CAMPO_PX - 34)
        b(PAINEL + 66, CAMPO_ALT_PX + 19, "-", lambda: self._mudar_bolas(-1), "neutro", 14)
        b(PAINEL + 84, CAMPO_ALT_PX + 19, "+", lambda: self._mudar_bolas(+1), "neutro", 14)
        self._atualizar_nome()

    def _botao(self, x, y, rotulo, acao, papel, largura=56):
        return self.adicionar(estilo.botao(x, y, rotulo, acao, papel, largura))

    def _escolher(self, ferramenta):
        self.ferramenta = ferramenta

    def _mudar_bolas(self, delta):
        novo = max(1, min(BOLAS_MAX, self.bolas + delta))
        if novo != self.bolas:
            self.bolas = novo
            self._sujo = True

    def _pedir_nome(self):
        def recebeu(texto):
            texto = texto.strip()
            if texto and texto != self.nome:
                self.nome = texto[:40]
                self._sujo = True
                self._atualizar_nome()
        self.pedir_texto("Nome da fase", "Digite o nome da fase:", recebeu,
                         valor=self.nome, maximo=40)

    def _atualizar_nome(self):
        self._b_nome.rotulo = self.nome

    def _limpar_tudo(self):
        if not self.pegs:
            return

        def apagar():
            self.pegs.clear()
            self._sujo = True

        self.perguntar("Limpar tudo", "Remover todos os pegs da fase?", apagar)

    def _no_campo(self, p):
        return 0 <= p[0] <= CAMPO_L and 0 <= p[1] <= CAMPO_A

    def _ajustar(self, p):
        x = min(max(p[0], RAIO_PEG), CAMPO_L - RAIO_PEG)
        y = min(max(p[1], Y_MIN_PEG), CAMPO_A - RAIO_PEG)
        return x, y

    def _peg_em(self, p):
        for peg in reversed(self.pegs):
            if math.hypot(p[0] - peg.x, p[1] - peg.y) <= RAIO_PEG + 8:
                return peg
        return None

    def _cabe(self, x, y):
        return all(math.hypot(x - p.x, y - p.y) >= 2 * RAIO_PEG - 1 for p in self.pegs)

    def ao_mover_mouse(self, sx, sy):
        p = VISTA.mundo(sx, sy)
        if not self.dialogo_aberto and self._no_campo(p) and sy < CAMPO_ALT_PX:
            self.cursor = self._ajustar(p)
        else:
            self.cursor = None

    def ao_clicar(self, sx, sy):
        if super().ao_clicar(sx, sy):
            return True
        p = VISTA.mundo(sx, sy)
        if not self._no_campo(p) or sx < PAINEL or sy >= CAMPO_ALT_PX:
            return False
        peg = self._peg_em(p)

        if self.ferramenta == "apagar":
            if peg:
                self.pegs.remove(peg)
                self._sujo = True
        elif peg:
            if peg.tipo != self.ferramenta:
                peg.definir_tipo(self.ferramenta)
                self._sujo = True
        else:
            x, y = self._ajustar(p)
            if self._cabe(x, y):
                self.pegs.append(Peg(x, y, self.ferramenta))
                self._sujo = True
        return False

    def ao_tecla(self, nome):
        if nome == "Escape":
            self._voltar()

    def _montar_fase(self):
        nome = self.nome.strip() or "Fase sem nome"
        return {
            "nome": nome[:40],
            "bolas": self.bolas,
            "ordem": self.ordem,
            "arquivo": self.arquivo,
            "pegs": [{"x": int(round(p.x)), "y": int(round(p.y)), "tipo": p.tipo}
                     for p in self.pegs],
        }

    def _salvar(self):
        fase = self._montar_fase()
        erro = fases.validar(fase)
        if erro:
            self.avisar("Não dá para salvar", erro)
            return

        arquivo = fases.nome_para_arquivo(fase["nome"])
        fase["ordem"] = self.ordem if arquivo == self.arquivo else 1000

        if arquivo != self.arquivo and fases.existe(arquivo):
            self.perguntar("Já existe",
                           'Já existe uma fase chamada "%s".\nSubstituir?' % fase["nome"],
                           lambda: self._gravar(fase, arquivo))
        else:
            self._gravar(fase, arquivo)

    def _gravar(self, fase, arquivo):
        fases.salvar(fase, arquivo)
        self.arquivo = arquivo
        self.ordem = fase["ordem"]
        self._sujo = False
        self.avisar("Fase salva", 'A fase "%s" foi salva.' % fase["nome"])

    def _testar(self):
        fase = self._montar_fase()
        erro = fases.validar(fase)
        if erro:
            self.avisar("Não dá para testar", erro)
            return
        sujo = self._sujo
        app = self.app
        app.ir_para(Jogo(app, fase,
                         voltar=lambda: app.ir_para(Editor(app, fase, sujo)),
                         modo_teste=True))

    def _voltar(self):
        if self._sujo:
            self.perguntar("Sair do editor",
                           "Há alterações não salvas.\nSair mesmo assim?",
                           self.app.ir_seletor)
        else:
            self.app.ir_seletor()

    def desenhar(self):
        v = VISTA
        pyxel.cls(estilo.PRETO)

        pyxel.rectb(PAINEL, 0, CAMPO_PX, CAMPO_ALT_PX, estilo.AZUL)
        y_lim = v.sy(Y_MIN_PEG - RAIO_PEG)
        pyxel.line(PAINEL + 1, y_lim, LARGURA - 2, y_lim, estilo.AZUL_ESCURO)
        pyxel.circ(v.sx(CAMPO_L / 2), v.sy(0), v.r(RAIO_CANHAO), estilo.VERMELHO)
        for peg in self.pegs:
            peg.desenhar(v)

        if self.cursor is not None:
            x, y = self.cursor
            pyxel.circb(v.sx(x), v.sy(y), v.r(RAIO_PEG), COR_CURSOR[self.ferramenta])

        pyxel.rect(0, 0, PAINEL, ALTURA, estilo.AZUL_ESCURO)
        pyxel.line(PAINEL - 1, 0, PAINEL - 1, ALTURA, estilo.AZUL)
        estilo.negrito(4, 4, "EDITOR", estilo.BRANCO)
        dicas = ("Clique no campo", "p/ por pegs.", "Clique num peg", "de outra cor",
                 "troca a cor.", "Use Testar", "antes de salvar.", "Esc volta.")
        for i, linha in enumerate(dicas):
            estilo.escrever(4, 70 + i * 7, linha, estilo.CINZA)

        yb = CAMPO_ALT_PX
        pyxel.rect(PAINEL, yb + 1, CAMPO_PX, ALTURA - yb, estilo.AZUL_ESCURO)
        estilo.escrever(PAINEL + 4, yb + 7, "Nome:", estilo.BRANCO)
        estilo.escrever(PAINEL + 4, yb + 22, "Bolas: %d" % self.bolas, estilo.BRANCO)
        laranjas = sum(1 for p in self.pegs if p.tipo == "laranja")
        estilo.escrever(PAINEL + 4, yb + 36,
                        "Pegs:%d  Laranjas:%d  Ferr:%s" % (len(self.pegs), laranjas,
                                                         NOMES[self.ferramenta]),
                        estilo.AZUL_CLARO)
        self.desenhar_botoes()
