# ============================================================
#  editor.py  —  editor de fases
# ============================================================
#  Ferramentas (painel esquerdo):
#     Peg azul / Peg laranja : clique no campo para colocar
#                              (clicar num peg de outra cor troca a cor)
#     Apagar                 : clique num peg para removê-lo
#  O nome da fase é digitado no painel direito.
#  "Testar" joga a fase sem salvar; "Salvar" grava em niveis/<nome>.json.
# ============================================================
import math

import aroeira as ar
import estilo
import fases
from cena import Cena
from fases import MARGEM, CAMPO_L, RAIO_PEG, Y_MIN_PEG, BOLAS_PADRAO, BOLAS_MAX
from mira_e_atira import Jogo, Peg, RAIO_CANHAO

NOMES = {"azul": "peg azul", "laranja": "peg laranja", "apagar": "apagar"}
COR_CURSOR = {"azul": "azul", "laranja": "laranja", "apagar": "vermelho"}


class Editor(Cena):
    """fase = dicionário de fases.py para editar, ou None para uma fase nova."""

    def __init__(self, app, fase=None, sujo=False):
        super().__init__(app)
        if fase is None:
            fase = {"nome": "Nova fase", "bolas": BOLAS_PADRAO, "ordem": 1000,
                    "arquivo": None, "pegs": []}
        self.fase = fase
        self.arquivo = fase.get("arquivo")     # arquivo onde "Salvar" grava
        self.ordem = fase.get("ordem", 1000)
        self.bolas = fase["bolas"]
        self.ferramenta = "azul"
        self.pegs = []
        self._sujo = sujo                      # há alterações não salvas?

    # ---------------- montagem ----------------
    def entrar(self):
        L, A = self.app.largura, self.app.altura
        esq, dire = MARGEM, MARGEM + CAMPO_L
        cx = (esq + dire) / 2

        self.adicionar(ar.Retangulo(ar.Ponto(0, 0), L, A, cor="#0b132b"))
        self.adicionar(ar.Retangulo(ar.Ponto(esq, 0), CAMPO_L, A, cor="#1c2541"))
        self.adicionar(ar.Retangulo(ar.Ponto(0, 0), esq, A, cor="cinza_claro"))
        self.adicionar(ar.Retangulo(ar.Ponto(dire, 0), L - dire, A, cor="cinza_claro"))
        for x in (esq, dire):
            self.adicionar(ar.Linha(ar.Ponto(x, 0), ar.Ponto(x, A), cor="cinza_claro", espessura=4))
        # limite de cima: acima desta linha não cabem pegs (o canhão fica ali)
        y_lim = Y_MIN_PEG - RAIO_PEG
        self.adicionar(ar.Linha(ar.Ponto(esq, y_lim), ar.Ponto(dire, y_lim),
                                cor="#5c6b8a", espessura=2))
        self.adicionar(ar.Circulo(ar.Ponto(cx, 0), RAIO_CANHAO, "vermelho"))

        for d in self.fase["pegs"]:
            self._novo_peg(MARGEM + d["x"], d["y"], d["tipo"])

        # "fantasma": mostra onde o peg vai ficar
        self.cursor = self.adicionar(ar.Circulo(
            ar.Ponto(-200, -200), RAIO_PEG, cor="transparente",
            borda=COR_CURSOR[self.ferramenta], espessura_borda=2))
        self.cursor.visivel = False

        # painel esquerdo
        self.adicionar(ar.Texto(ar.Ponto(20, 15), "EDITOR DE FASES", 20, "preto", True))
        self._botao(20, 60, "Peg azul", lambda: self._escolher("azul"), "primario")
        self._botao(20, 110, "Peg laranja", lambda: self._escolher("laranja"), "alerta")
        self._botao(20, 160, "Apagar", lambda: self._escolher("apagar"), "perigo")
        self._t_ferramenta = self._texto(20, 215, "", 16)
        self._t_bolas = self._texto(20, 270, "", 20)
        self._botao(20, 305, "-", lambda: self._mudar_bolas(-1), "neutro", 100)
        self._botao(130, 305, "+", lambda: self._mudar_bolas(+1), "neutro", 100)
        self._t_pegs = self._texto(20, 370, "", 16)
        self._t_laranjas = self._texto(20, 395, "", 16)
        self._botao(20, 450, "Limpar tudo", self._limpar_tudo, "neutro")
        self._botao(20, A - 195, "Testar", self._testar, "destaque")
        self._botao(20, A - 140, "Salvar", self._salvar, "sucesso")
        self._botao(20, A - 85, "Voltar", self._voltar, "neutro")

        # painel direito
        self.campo_nome = self.adicionar(ar.Campo(
            ar.Ponto(dire + 15, 60), rotulo="Nome da fase", dica="Ex.: Chuva de pegs",
            largura=220))
        self.campo_nome.valor = self.fase["nome"]
        self.adicionar(ar.Texto(
            ar.Ponto(dire + 15, 150),
            "Dicas:\n- Clique no campo\n  para colocar pegs\n- Clique num peg de\n  outra cor para trocar\n"
            "- Use 'Testar' antes\n  de salvar\n- Esc volta",
            14, "preto"))

        self._escolher(self.ferramenta)
        self._atualizar_contagem()

    def _botao(self, x, y, rotulo, acao, papel, largura=estilo.L_PAINEL):
        return self.adicionar(estilo.botao(x, y, rotulo, acao, papel, largura))

    def _texto(self, x, y, conteudo, tamanho):
        return self.adicionar(ar.Texto(ar.Ponto(x, y), conteudo, tamanho, "preto"))

    def _novo_peg(self, x, y, tipo):
        peg = Peg(x, y, tipo)
        self.pegs.append(peg)
        self.adicionar(peg.circulo)
        return peg

    # ---------------- painel ----------------
    def _escolher(self, ferramenta):
        self.ferramenta = ferramenta
        self._t_ferramenta.conteudo = "Ferramenta: " + NOMES[ferramenta]
        self.cursor.borda = COR_CURSOR[ferramenta]

    def _mudar_bolas(self, delta):
        novo = max(1, min(BOLAS_MAX, self.bolas + delta))
        if novo != self.bolas:
            self.bolas = novo
            self._sujo = True
            self._atualizar_contagem()

    def _atualizar_contagem(self):
        laranjas = sum(1 for p in self.pegs if p.tipo == "laranja")
        self._t_bolas.conteudo = "Bolas: %d" % self.bolas
        self._t_pegs.conteudo = "Pegs: %d" % len(self.pegs)
        self._t_laranjas.conteudo = "Laranjas: %d" % laranjas

    def _limpar_tudo(self):
        if not self.pegs:
            return

        def apagar():
            for peg in list(self.pegs):
                self.remover(peg.circulo)
            self.pegs.clear()
            self._sujo = True
            self._atualizar_contagem()

        self.perguntar("Limpar tudo", "Remover todos os pegs da fase?", apagar)

    # ---------------- o campo ----------------
    def _no_campo(self, p):
        return MARGEM <= p.x <= MARGEM + CAMPO_L and 0 <= p.y <= self.app.altura

    def _ajustar(self, p):
        """Mantém o peg inteiro dentro do campo e abaixo do canhão."""
        x = min(max(p.x, MARGEM + RAIO_PEG), MARGEM + CAMPO_L - RAIO_PEG)
        y = min(max(p.y, Y_MIN_PEG), self.app.altura - RAIO_PEG)
        return x, y

    def _peg_em(self, p):
        for peg in reversed(self.pegs):
            if math.hypot(p.x - peg.x, p.y - peg.y) <= RAIO_PEG:
                return peg
        return None

    def _cabe(self, x, y):
        return all(math.hypot(x - p.x, y - p.y) >= 2 * RAIO_PEG - 1 for p in self.pegs)

    def ao_mover_mouse(self, ponto):
        dentro = self._no_campo(ponto)
        if dentro:
            x, y = self._ajustar(ponto)
            self.cursor.centro = ar.Ponto(x, y)
        if self.cursor.visivel != dentro:
            self.cursor.visivel = dentro

    def ao_clicar(self, ponto):
        if self.dialogo_aberto or not self._no_campo(ponto):
            return
        peg = self._peg_em(ponto)

        if self.ferramenta == "apagar":
            if peg:
                self.pegs.remove(peg)
                self.remover(peg.circulo)
                self._alterou()
        elif peg:
            if peg.tipo != self.ferramenta:       # clicar noutra cor troca a cor
                peg.definir_tipo(self.ferramenta)
                self._alterou()
        else:
            x, y = self._ajustar(ponto)
            if self._cabe(x, y):
                self._novo_peg(x, y, self.ferramenta)
                self._alterou()

    def _alterou(self):
        self._sujo = True
        self._atualizar_contagem()

    def ao_tecla(self, nome):
        if nome == "Escape" and not self.dialogo_aberto:
            self._voltar()

    # ---------------- salvar / testar / sair ----------------
    def _montar_fase(self):
        nome = self.campo_nome.valor.strip() or "Fase sem nome"
        return {
            "nome": nome[:40],
            "bolas": self.bolas,
            "ordem": self.ordem,
            "arquivo": self.arquivo,
            "pegs": [{"x": int(round(p.x - MARGEM)), "y": int(round(p.y)), "tipo": p.tipo}
                     for p in self.pegs],
        }

    def _salvar(self):
        fase = self._montar_fase()
        erro = fases.validar(fase)
        if erro:
            self.avisar("Não dá para salvar", erro)
            return

        arquivo = fases.nome_para_arquivo(fase["nome"])
        # uma fase nova (outro arquivo) vai para o fim da lista do seletor
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
