import math
import time

import pyxel

import estilo
import fases
import perfis
from cena import Cena, Dialogo
from estilo import LARGURA, ALTURA, Vista
from fases import CAMPO_L, CAMPO_A, RAIO_PEG

GRAVIDADE = 1000.0
VELOCIDADE_TIRO = 800.0
VELOCIDADE_MAXIMA = 1800.0
REST_PEG = 0.80
REST_PAREDE = 0.90
RAIO_PROJETIL = 10
RAIO_CANHAO = 75
TAMANHO_MIRA = 105
DIST_SAIDA = 85
ANGULO_MIN = math.radians(10)
ANGULO_MAX = math.radians(170)
PASSO_MAXIMO = 8.0
INTERVALO_LIMPEZA = 0.07

PONTOS_BASE = {"azul": 10, "laranja": 100}

COR_PEG = {"azul": (estilo.AZUL_MEDIO, estilo.AZUL),
           "laranja": (estilo.LARANJA, estilo.MARROM)}
COR_ACERTO = {"azul": (estilo.VERDE, estilo.VERDE_AZULADO),
              "laranja": (estilo.AMARELO, estilo.LARANJA)}

VISTA = Vista(0, 0, LARGURA / CAMPO_L)


def _agora():
    return time.perf_counter()


class Peg:

    def __init__(self, x, y, tipo="azul"):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.acertado = False

    def definir_tipo(self, tipo):
        self.tipo = tipo

    def acender(self):
        self.acertado = True

    def desenhar(self, vista):
        cores = COR_ACERTO if self.acertado else COR_PEG
        fundo, contorno = cores[self.tipo]
        x, y, r = vista.sx(self.x), vista.sy(self.y), vista.r(RAIO_PEG)
        pyxel.circ(x, y, r, fundo)
        if r >= 3:
            pyxel.circb(x, y, r, contorno)


class Jogo(Cena):

    def __init__(self, app, fase, voltar, modo_teste=False):
        super().__init__(app)
        self.fase = fase
        self.voltar = voltar
        self.modo_teste = modo_teste

        self.arquivo = fase.get("arquivo")
        self.perfil = None if modo_teste else perfis.atual()
        self.recorde = (perfis.recorde(self.perfil, self.arquivo)
                        if self.perfil and self.arquivo else 0)

        self.pegs = []
        self.acertos = []
        self.estado = "mirando"
        self.pontos = 0
        self.bolas = fase["bolas"]
        self.n_acertos = 0
        self.pontos_tiro = 0
        self.angulo = math.pi / 2

        self.projetil = False
        self.px = self.py = self.vx = self.vy = 0.0
        self._ultimo = 0.0
        self._tempo_limpeza = 0.0
        self._tempo_voo = 0.0
        self._tempo_checagem = 0.0
        self._pos_checagem = (0.0, 0.0)

        self.laranjas = 0
        self.esq = 0
        self.dir = CAMPO_L
        self.centro_x = CAMPO_L / 2

    def entrar(self):
        for d in self.fase["pegs"]:
            self.pegs.append(Peg(d["x"], d["y"], d["tipo"]))
        self.laranjas = sum(1 for p in self.pegs if p.tipo == "laranja")
        self.adicionar(estilo.botao(2, ALTURA - 13, "Reiniciar", self._reiniciar, "alerta", 44))
        self.adicionar(estilo.botao(49, ALTURA - 13, "Voltar", self.voltar, "neutro", 34))
        self._ultimo = _agora()

    def _laranjas_restantes(self):
        return self.laranjas

    def _reiniciar(self):
        self.app.ir_para(Jogo(self.app, self.fase, self.voltar, self.modo_teste))

    def ao_mover_mouse(self, x, y):
        if self.estado == "mirando" and not self.dialogo_aberto:
            self._apontar(*VISTA.mundo(x, y))

    def ao_clicar(self, x, y):
        if super().ao_clicar(x, y):
            return True
        if self.estado == "mirando":
            self._apontar(*VISTA.mundo(x, y))
            self._atirar()
        return False

    def ao_tecla(self, nome):
        if nome == "Escape" and self.estado != "fim":
            self.voltar()

    def _apontar(self, wx, wy):
        dx = wx - self.centro_x
        dy = wy
        if dx == 0 and dy == 0:
            return
        self.angulo = min(max(math.atan2(dy, dx), ANGULO_MIN), ANGULO_MAX)

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
        self.projetil = True

        self.estado = "voando"
        self._tempo_voo = 0.0
        self._tempo_checagem = 0.0
        self._pos_checagem = (self.px, self.py)
        self._ultimo = _agora()

    def atualizar(self):
        agora = _agora()
        dt = min(agora - self._ultimo, 0.05)
        self._ultimo = agora
        if self.estado == "voando":
            self._mover_projetil(max(dt, 0.0))
        elif self.estado == "limpando":
            self._limpar_acertos(max(dt, 0.0))

        if (not self.dialogo_aberto and self.estado != "fim"
                and pyxel.btnp(pyxel.KEY_R)):
            self._reiniciar()

    def _mover_projetil(self, dt):
        r = RAIO_PROJETIL
        x_min, x_max = self.esq + r, self.dir - r
        x, y, vx, vy = self.px, self.py, self.vx, self.vy

        passos = max(1, math.ceil(math.hypot(vx, vy) * dt / PASSO_MAXIMO))
        h = dt / passos
        minimo = RAIO_PEG + r
        minimo2 = minimo * minimo
        pegs = self.pegs

        for _ in range(passos):
            vy += GRAVIDADE * h
            x += vx * h
            y += vy * h

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

            for peg in pegs:
                dx = x - peg.x
                if dx >= minimo or dx <= -minimo:
                    continue
                dy = y - peg.y
                if dy >= minimo or dy <= -minimo:
                    continue
                d2 = dx * dx + dy * dy
                if d2 >= minimo2:
                    continue
                d = math.sqrt(d2)
                if d > 1e-9:
                    nx, ny = dx / d, dy / d
                else:
                    nx, ny = 0.0, -1.0
                x = peg.x + nx * minimo
                y = peg.y + ny * minimo
                vn = vx * nx + vy * ny
                if vn < 0:
                    k = (1 + REST_PEG) * vn
                    vx -= k * nx
                    vy -= k * ny
                self._registrar_acerto(peg)

        v = math.hypot(vx, vy)
        if v > VELOCIDADE_MAXIMA:
            vx, vy = vx * VELOCIDADE_MAXIMA / v, vy * VELOCIDADE_MAXIMA / v

        self.px, self.py, self.vx, self.vy = x, y, vx, vy

        if y - r > CAMPO_A:
            self._fim_do_voo()
            return

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
        if peg.acertado:
            return
        peg.acender()
        self.acertos.append(peg)
        self.n_acertos += 1
        ganho = PONTOS_BASE[peg.tipo] * self.n_acertos
        self.pontos_tiro += ganho
        self.pontos += ganho

    def _fim_do_voo(self):
        self.projetil = False
        self.estado = "limpando"
        self._tempo_limpeza = INTERVALO_LIMPEZA
        if not self.acertos:
            self._concluir_tiro()

    def _limpar_acertos(self, dt):
        self._tempo_limpeza += dt
        if self._tempo_limpeza < INTERVALO_LIMPEZA:
            return
        self._tempo_limpeza = 0.0
        peg = self.acertos.pop(0)
        self.pegs.remove(peg)
        if peg.tipo == "laranja":
            self.laranjas -= 1
        if not self.acertos:
            self._concluir_tiro()

    def _concluir_tiro(self):
        self.estado = "mirando"
        if self._laranjas_restantes() == 0:
            self._vitoria()
        elif self.bolas == 0:
            self._derrota()

    def _registrar_recorde(self):
        if not (self.perfil and self.arquivo):
            return ""
        novo = perfis.registrar(self.perfil, self.arquivo, self.pontos)
        self.recorde = perfis.recorde(self.perfil, self.arquivo)
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
            caixa = Dialogo("Fase concluída!", resumo + "\n\nJogar a próxima fase?",
                            "confirmacao", resposta)
        else:
            if not self.modo_teste:
                resumo += "\n\nVocê completou todas as fases!"
            caixa = Dialogo("Fase concluída!", resumo, "mensagem", self.voltar)
        self.app.mostrar_dialogo(caixa)

    def _derrota(self):
        self.estado = "fim"
        recorde = self._registrar_recorde()

        def resposta(sim):
            if sim:
                self._reiniciar()
            else:
                self.voltar()

        self.app.mostrar_dialogo(Dialogo(
            "Acabaram as bolas",
            "Pontos: %d%s\n\nTentar de novo?" % (self.pontos, recorde),
            "confirmacao", resposta))

    def desenhar(self):
        v = VISTA
        pyxel.cls(estilo.PRETO)
        pyxel.rectb(0, 0, LARGURA, ALTURA, estilo.AZUL)

        cx = v.sx(self.centro_x)
        pyxel.circ(cx, v.sy(0), v.r(RAIO_CANHAO), estilo.VERMELHO)
        for peg in self.pegs:
            peg.desenhar(v)

        ex = v.sx(self.centro_x + math.cos(self.angulo) * TAMANHO_MIRA)
        ey = v.sy(math.sin(self.angulo) * TAMANHO_MIRA)
        pyxel.line(cx, 0, ex, ey, estilo.BRANCO)
        pyxel.line(cx + 1, 0, ex + 1, ey, estilo.BRANCO)

        if self.projetil:
            pyxel.circ(v.sx(self.px), v.sy(self.py), max(2, v.r(RAIO_PROJETIL)), estilo.BRANCO)

        quem = self.perfil if self.perfil else "Modo teste"
        estilo.escrever(3, 2, "%s - %s" % (self.fase["nome"][:14], quem[:10]), estilo.BRANCO)
        rec = ("Rec:%d" % self.recorde) if self.perfil else "Sem recorde"
        estilo.escrever(3, 9, "Pontos:%d  %s" % (self.pontos, rec), estilo.AMARELO)
        estilo.escrever(3, 16, "Bolas:%d  Laranjas:%d" % (self.bolas, self._laranjas_restantes()),
                        estilo.AZUL_CLARO)
        for i, texto in enumerate(("Acertos:%d" % self.n_acertos,
                                   "Tiro:+%d" % self.pontos_tiro)):
            estilo.escrever(LARGURA - 3 - estilo.largura_texto(texto), 2 + i * 7,
                            texto, estilo.CINZA)
        estilo.escrever(LARGURA - 3 - estilo.largura_texto("R reinicia  Esc volta"),
                        ALTURA - 8, "R reinicia  Esc volta", estilo.CINZA)

        self.desenhar_botoes()
