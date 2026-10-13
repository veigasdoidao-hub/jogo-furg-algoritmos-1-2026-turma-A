# ============================================================
#  mira_e_atira.py  —  a cena do jogo (mirar, atirar, pontuar)
# ============================================================
#  Fluxo de um tiro (self.estado):
#
#     "mirando"  -> o mouse gira a mira; o clique atira
#     "voando"   -> a bolinha cai, quica e acerta pegs
#     "limpando" -> a bolinha saiu: os pegs acertados somem, um a um
#     "fim"      -> a fase acabou (vitória ou derrota), diálogo na tela
#
#  Só depois de "limpando" terminar é que se pode atirar de novo.
#
#  A física usa o TEMPO REAL entre frames (dt), então o jogo tem a
#  mesma velocidade em qualquer computador, mesmo que o fps varie.
# ============================================================
import math
import time

import aroeira as ar
import estilo
import fases
import perfis
from cena import Cena
from fases import MARGEM, CAMPO_L, RAIO_PEG

# ---------------- Ajustes (mexa à vontade) ----------------
GRAVIDADE = 1000.0          # pixels/s²
VELOCIDADE_TIRO = 800.0     # pixels/s
VELOCIDADE_MAXIMA = 1800.0
REST_PEG = 0.80             # 1.0 = quica sem perder energia
REST_PAREDE = 0.90
RAIO_PROJETIL = 10
RAIO_CANHAO = 75
TAMANHO_MIRA = 105          # comprimento do "cano"
DIST_SAIDA = 85             # distância do centro do canhão onde a bolinha nasce
ANGULO_MIN = math.radians(10)    # a mira não aponta para cima
ANGULO_MAX = math.radians(170)
PASSO_MAXIMO = 8.0          # a bolinha nunca anda mais que isso por sub-passo
INTERVALO_LIMPEZA = 0.07    # segundos entre um peg sumindo e o próximo

# PONTUAÇÃO: cada peg acertado vale (valor base) × (nº do acerto no tiro).
# Ou seja, o 1º peg vale 1×, o 2º vale 2×, o 3º vale 3×... Quanto mais pegs
# o mesmo tiro acerta, mais cada um vale. Para pontuação simples
# (base × quantidade), troque "* self.n_acertos" por "* 1" em _registrar_acerto.
PONTOS_BASE = {"azul": 10, "laranja": 100}

COR_PEG = {"azul": "azul", "laranja": "laranja"}
COR_ACERTO = {"azul": "verde", "laranja": "amarelo"}    # cor "acesa"


def _agora():
    """Relógio do jogo (separado para poder ser trocado em testes)."""
    return time.perf_counter()


# ============================================================
#  Peg
# ============================================================
class Peg:
    """Uma bolinha-alvo. x e y são coordenadas de TELA (já com a margem)."""

    def __init__(self, x, y, tipo="azul"):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.acertado = False
        self.circulo = ar.Circulo(ar.Ponto(x, y), RAIO_PEG, COR_PEG[tipo])

    def definir_tipo(self, tipo):
        self.tipo = tipo
        self.circulo.cor = COR_PEG[tipo]

    def acender(self):
        self.acertado = True
        self.circulo.cor = COR_ACERTO[self.tipo]


# ============================================================
#  Jogo
# ============================================================
class Jogo(Cena):
    """
    fase       : dicionário de fases.py
    voltar     : função chamada para sair da fase (vai para o seletor/editor)
    modo_teste : True quando veio do editor (não oferece "próxima fase")
    """

    def __init__(self, app, fase, voltar, modo_teste=False):
        super().__init__(app)
        self.fase = fase
        self.voltar = voltar
        self.modo_teste = modo_teste

        # Recorde: só vale jogando uma fase salva, com um perfil escolhido
        # (testar no editor não conta).
        self.arquivo = fase.get("arquivo")
        self.perfil = None if modo_teste else perfis.atual()
        self.recorde = (perfis.recorde(self.perfil, self.arquivo)
                        if self.perfil and self.arquivo else 0)

        self.pegs = []
        self.acertos = []          # pegs acertados no tiro atual (somem no fim)
        self.estado = "mirando"
        self.pontos = 0
        self.bolas = fase["bolas"]
        self.n_acertos = 0         # acertos do tiro atual
        self.pontos_tiro = 0       # pontos do tiro atual
        self.angulo = math.pi / 2

        self.projetil = None
        self.px = self.py = self.vx = self.vy = 0.0
        self._ultimo = 0.0
        self._tempo_limpeza = 0.0
        self._tempo_voo = 0.0
        self._tempo_checagem = 0.0
        self._pos_checagem = (0.0, 0.0)

    # ---------------- montagem ----------------
    def entrar(self):
        L, A = self.app.largura, self.app.altura
        self.esq = MARGEM
        self.dir = MARGEM + CAMPO_L
        self.centro_x = (self.esq + self.dir) / 2

        # fundo, campo e painéis laterais
        self.adicionar(ar.Retangulo(ar.Ponto(0, 0), L, A, cor="#0b132b"))
        self.adicionar(ar.Retangulo(ar.Ponto(self.esq, 0), CAMPO_L, A, cor="#1c2541"))
        self.adicionar(ar.Retangulo(ar.Ponto(0, 0), self.esq, A, cor="cinza_claro"))
        self.adicionar(ar.Retangulo(ar.Ponto(self.dir, 0), L - self.dir, A, cor="cinza_claro"))
        for x in (self.esq, self.dir):
            self.adicionar(ar.Linha(ar.Ponto(x, 0), ar.Ponto(x, A), cor="cinza_claro", espessura=4))

        # canhão, pegs e mira (nesta ordem de desenho)
        self.adicionar(ar.Circulo(ar.Ponto(self.centro_x, 0), RAIO_CANHAO, "vermelho"))
        for d in self.fase["pegs"]:
            peg = Peg(MARGEM + d["x"], d["y"], d["tipo"])
            self.pegs.append(peg)
            self.adicionar(peg.circulo)
        self.mira = self.adicionar(ar.Linha(
            ar.Ponto(self.centro_x, 0), ar.Ponto(self.centro_x, TAMANHO_MIRA),
            cor="branco", espessura=6))

        # painel esquerdo
        self._texto(20, self.fase["nome"][:16], 22, True)
        quem = ("Jogador: " + self.perfil) if self.perfil else "Modo teste"
        self._texto(55, quem[:22], 16)
        self._t_pontos = self._texto(100, "", 22)
        self._t_recorde = self._texto(135, "", 18)
        self._t_bolas = self._texto(170, "", 22)
        self._t_laranjas = self._texto(205, "", 22)
        self._t_acertos = self._texto(270, "", 18)
        self._t_tiro = self._texto(300, "", 18)
        self.adicionar(estilo.botao(20, A - 130, "Reiniciar", self._reiniciar, "alerta"))
        self.adicionar(estilo.botao(20, A - 75, "Voltar", self.voltar, "neutro"))
        self._atualizar_textos()

        self._ultimo = _agora()

    def _texto(self, y, conteudo, tamanho, negrito=False):
        return self.adicionar(ar.Texto(ar.Ponto(20, y), conteudo, tamanho, "preto", negrito))

    def _definir(self, texto, valor):
        if texto.conteudo != valor:        # só redesenha se mudou
            texto.conteudo = valor

    def _laranjas_restantes(self):
        return sum(1 for p in self.pegs if p.tipo == "laranja")

    def _atualizar_textos(self):
        self._definir(self._t_pontos, "Pontos: %d" % self.pontos)
        self._definir(self._t_recorde,
                      "Recorde: %d" % self.recorde if self.perfil else "Sem recorde")
        self._definir(self._t_bolas, "Bolas: %d" % self.bolas)
        self._definir(self._t_laranjas, "Laranjas: %d" % self._laranjas_restantes())
        self._definir(self._t_acertos, "Acertos no tiro: %d" % self.n_acertos)
        self._definir(self._t_tiro, "Pontos no tiro: +%d" % self.pontos_tiro)

    def _reiniciar(self):
        self.app.ir_para(Jogo(self.app, self.fase, self.voltar, self.modo_teste))

    # ---------------- eventos ----------------
    def ao_mover_mouse(self, ponto):
        if self.estado == "mirando":
            self._apontar(ponto)

    def ao_clicar(self, ponto):
        if self.estado == "mirando":
            self._apontar(ponto)        # no celular não há "hover": mira onde tocou
            self._atirar()

    def ao_tecla(self, nome):
        if nome == "Escape" and self.estado != "fim":
            self.voltar()

    def _apontar(self, ponto):
        dx = ponto.x - self.centro_x
        dy = ponto.y
        if dx == 0 and dy == 0:
            return
        self.angulo = min(max(math.atan2(dy, dx), ANGULO_MIN), ANGULO_MAX)
        self.mira.fim = ar.Ponto(self.centro_x + math.cos(self.angulo) * TAMANHO_MIRA,
                                 math.sin(self.angulo) * TAMANHO_MIRA)

    # ---------------- o tiro ----------------
    def _atirar(self):
        if self.estado != "mirando" or self.bolas <= 0:
            return
        self.bolas -= 1
        self.n_acertos = 0
        self.pontos_tiro = 0
        self.acertos = []

        dx, dy = math.cos(self.angulo), math.sin(self.angulo)
        self.px = self.centro_x + dx * DIST_SAIDA
        self.py = dy * DIST_SAIDA
        self.vx = dx * VELOCIDADE_TIRO
        self.vy = dy * VELOCIDADE_TIRO
        self.projetil = self.adicionar(
            ar.Circulo(ar.Ponto(self.px, self.py), RAIO_PROJETIL, "branco"))

        self.estado = "voando"
        self._tempo_voo = 0.0
        self._tempo_checagem = 0.0
        self._pos_checagem = (self.px, self.py)
        self._ultimo = _agora()
        self._atualizar_textos()

    def atualizar(self):
        agora = _agora()
        dt = min(agora - self._ultimo, 0.05)     # limita saltos (janela travada etc.)
        self._ultimo = agora
        if self.estado == "voando":
            self._mover_projetil(max(dt, 0.0))
        elif self.estado == "limpando":
            self._limpar_acertos(max(dt, 0.0))

    def _mover_projetil(self, dt):
        r = RAIO_PROJETIL
        x_min, x_max = self.esq + r, self.dir - r
        x, y, vx, vy = self.px, self.py, self.vx, self.vy

        # Sub-passos: a bolinha nunca anda mais que PASSO_MAXIMO de uma vez,
        # senão, rápida, ela atravessaria um peg sem encostar.
        passos = max(1, math.ceil(math.hypot(vx, vy) * dt / PASSO_MAXIMO))
        h = dt / passos
        minimo = RAIO_PEG + r

        for _ in range(passos):
            vy += GRAVIDADE * h
            x += vx * h
            y += vy * h

            # paredes e teto
            if x < x_min:
                x = x_min
                if vx < 0:
                    vx = -vx * REST_PAREDE
            elif x > x_max:
                x = x_max
                if vx > 0:
                    vx = -vx * REST_PAREDE
            if y < r:
                y = r
                if vy < 0:
                    vy = -vy * REST_PAREDE

            # pegs: empurra a bolinha para fora e reflete a velocidade
            for peg in self.pegs:
                dx, dy = x - peg.x, y - peg.y
                d2 = dx * dx + dy * dy
                if d2 >= minimo * minimo:
                    continue
                d = math.sqrt(d2)
                if d > 1e-9:
                    nx, ny = dx / d, dy / d
                else:
                    nx, ny = 0.0, -1.0
                x = peg.x + nx * minimo
                y = peg.y + ny * minimo
                vn = vx * nx + vy * ny          # velocidade na direção da batida
                if vn < 0:                      # só reflete se estiver "entrando"
                    k = (1 + REST_PEG) * vn
                    vx -= k * nx
                    vy -= k * ny
                self._registrar_acerto(peg)

        v = math.hypot(vx, vy)
        if v > VELOCIDADE_MAXIMA:
            vx, vy = vx * VELOCIDADE_MAXIMA / v, vy * VELOCIDADE_MAXIMA / v

        self.px, self.py, self.vx, self.vy = x, y, vx, vy
        self.projetil.centro = ar.Ponto(x, y)

        # saiu por baixo?
        if y - r > self.app.altura:
            self._fim_do_voo()
            return

        # bolinha emperrada (equilibrada num peg, por exemplo): encerra o tiro
        self._tempo_voo += dt
        self._tempo_checagem += dt
        if self._tempo_checagem >= 1.5:
            moveu = math.hypot(x - self._pos_checagem[0], y - self._pos_checagem[1])
            self._pos_checagem = (x, y)
            self._tempo_checagem = 0.0
            if moveu < 15:
                self._fim_do_voo()
                return
        if self._tempo_voo > 40:
            self._fim_do_voo()

    def _registrar_acerto(self, peg):
        if peg.acertado:                # peg já aceso neste tiro não pontua de novo
            return
        peg.acender()
        self.acertos.append(peg)
        self.n_acertos += 1
        ganho = PONTOS_BASE[peg.tipo] * self.n_acertos
        self.pontos_tiro += ganho
        self.pontos += ganho
        self._atualizar_textos()

    # ---------------- depois do tiro ----------------
    def _fim_do_voo(self):
        self.remover(self.projetil)
        self.projetil = None
        self.estado = "limpando"
        self._tempo_limpeza = INTERVALO_LIMPEZA      # o 1º peg some já no próximo frame
        if not self.acertos:
            self._concluir_tiro()

    def _limpar_acertos(self, dt):
        self._tempo_limpeza += dt
        if self._tempo_limpeza < INTERVALO_LIMPEZA:
            return
        self._tempo_limpeza = 0.0
        peg = self.acertos.pop(0)
        self.pegs.remove(peg)
        self.remover(peg.circulo)
        if not self.acertos:
            self._concluir_tiro()

    def _concluir_tiro(self):
        self.estado = "mirando"
        self._atualizar_textos()
        if self._laranjas_restantes() == 0:
            self._vitoria()
        elif self.bolas == 0:
            self._derrota()

    # ---------------- fim da fase ----------------
    def _registrar_recorde(self):
        """Guarda os pontos se forem o melhor deste perfil nesta fase.
        Devolve o texto da linha de recorde para o diálogo final."""
        if not (self.perfil and self.arquivo):
            return ""
        novo = perfis.registrar(self.perfil, self.arquivo, self.pontos)
        self.recorde = perfis.recorde(self.perfil, self.arquivo)
        self._atualizar_textos()
        return "\nNovo recorde!" if novo else "\nRecorde: %d" % self.recorde

    def _vitoria(self):
        self.estado = "fim"
        resumo = "Pontos: %d" % self.pontos + self._registrar_recorde()
        proxima = None if self.modo_teste else fases.proxima(self.fase.get("arquivo"))

        if proxima:
            def resposta(sim):
                if sim:
                    self.app.ir_para(Jogo(self.app, proxima, self.voltar))
                else:
                    self.voltar()
            caixa = ar.CaixaDeDialogo("Fase concluída!", resumo + "\n\nJogar a próxima fase?",
                                      modo="confirmacao", ao_confirmar=resposta)
        else:
            if not self.modo_teste:
                resumo += "\n\nVocê completou todas as fases!"
            caixa = ar.CaixaDeDialogo("Fase concluída!", resumo, ao_confirmar=self.voltar)
        self.tela.mostrar_dialogo(caixa)

    def _derrota(self):
        self.estado = "fim"
        recorde = self._registrar_recorde()

        def resposta(sim):
            if sim:
                self._reiniciar()
            else:
                self.voltar()

        self.tela.mostrar_dialogo(ar.CaixaDeDialogo(
            "Acabaram as bolas",
            "Pontos: %d%s\n\nTentar de novo?" % (self.pontos, recorde),
            modo="confirmacao", ao_confirmar=resposta))
