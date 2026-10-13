import unicodedata
from functools import lru_cache

import pyxel

LARGURA = 256
ALTURA = 192

(PRETO, AZUL_ESCURO, ROXO, VERDE_AZULADO, MARROM, AZUL, AZUL_CLARO, BRANCO,
 VERMELHO, LARANJA, AMARELO, VERDE, AZUL_MEDIO, CINZA, ROSA, PELE) = range(16)

PAPEIS = {
    "primario": (AZUL, BRANCO),
    "sucesso":  (VERDE_AZULADO, BRANCO),
    "perigo":   (VERMELHO, BRANCO),
    "neutro":   (CINZA, PRETO),
    "alerta":   (LARANJA, PRETO),
    "destaque": (ROXO, BRANCO),
}

ALTURA_BOTAO = 11


@lru_cache(maxsize=512)
def _limpar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")


def limpar(texto):
    return _limpar(str(texto))


def largura_texto(texto):
    return 4 * len(limpar(texto))


def escrever(x, y, texto, cor=BRANCO):
    pyxel.text(int(x), int(y), limpar(texto), cor)


def centralizar(y, texto, cor=BRANCO, cx=LARGURA / 2):
    escrever(cx - largura_texto(texto) / 2, y, texto, cor)


def negrito(x, y, texto, cor=BRANCO, sombra=PRETO):
    escrever(x + 1, y + 1, texto, sombra)
    escrever(x, y, texto, cor)
    escrever(x + 1, y, texto, cor)


_mapas = {}


def preparar_texto_grande(texto):
    texto = limpar(texto)
    if texto in _mapas:
        return
    larg = 4 * len(texto)
    pyxel.rect(0, 0, larg, 6, PRETO)
    pyxel.text(0, 0, texto, BRANCO)
    corridas = []
    for j in range(6):
        i = 0
        while i < larg:
            if pyxel.pget(i, j) == BRANCO:
                inicio = i
                while i < larg and pyxel.pget(i, j) == BRANCO:
                    i += 1
                corridas.append((inicio, j, i - inicio))
            else:
                i += 1
    _mapas[texto] = corridas
    pyxel.rect(0, 0, larg, 6, PRETO)


def texto_grande(cx, y, texto, cor=BRANCO, k=2, sombra=PRETO):
    texto = limpar(texto)
    if texto not in _mapas:
        preparar_texto_grande(texto)
    x0 = int(cx - 4 * len(texto) * k / 2)
    corridas = _mapas[texto]
    for i, j, n in corridas:
        pyxel.rect(x0 + i * k + 1, y + j * k + 1, n * k, k, sombra)
    for i, j, n in corridas:
        pyxel.rect(x0 + i * k, y + j * k, n * k, k, cor)


def digitado():
    texto = getattr(pyxel, "input_text", None)
    if texto is not None:
        return "".join(c for c in limpar(texto) if 32 <= ord(c) < 127)
    saida = ""
    maiuscula = pyxel.btn(pyxel.KEY_SHIFT)
    for c in "abcdefghijklmnopqrstuvwxyz":
        if pyxel.btnp(getattr(pyxel, "KEY_" + c.upper())):
            saida += c.upper() if maiuscula else c
    for d in "0123456789":
        if pyxel.btnp(getattr(pyxel, "KEY_" + d)):
            saida += d
    if pyxel.btnp(pyxel.KEY_SPACE):
        saida += " "
    return saida


def apagou():
    return pyxel.btnp(pyxel.KEY_BACKSPACE, 15, 3)


class Botao:
    def __init__(self, x, y, rotulo, acao, papel="primario",
                 largura=56, altura=ALTURA_BOTAO):
        self.x, self.y = x, y
        self.rotulo = rotulo
        self.acao = acao
        self.papel = papel
        self.largura, self.altura = largura, altura
        self.ativo = True
        self.visivel = True

    def contem(self, px, py):
        return (self.x <= px < self.x + self.largura
                and self.y <= py < self.y + self.altura)

    def desenhar(self, hover=True):
        if not self.visivel:
            return
        fundo, texto = PAPEIS[self.papel]
        sobre = hover and self.ativo and self.contem(pyxel.mouse_x, pyxel.mouse_y)
        if not self.ativo:
            fundo, texto = AZUL_ESCURO, CINZA
        pyxel.rect(self.x, self.y, self.largura, self.altura, fundo)
        pyxel.rectb(self.x, self.y, self.largura, self.altura,
                    BRANCO if sobre else PRETO)
        rotulo = limpar(self.rotulo)[:(self.largura - 4) // 4]
        tx = self.x + (self.largura - 4 * len(rotulo)) // 2
        ty = self.y + (self.altura - 5) // 2
        pyxel.text(tx, ty, rotulo, texto)


def botao(x, y, rotulo, acao, papel="primario", largura=56, altura=ALTURA_BOTAO):
    return Botao(x, y, rotulo, acao, papel, largura, altura)


class Vista:
    def __init__(self, ox, oy, escala):
        self.ox, self.oy, self.escala = ox, oy, escala

    def sx(self, x):
        return int(round(self.ox + x * self.escala))

    def sy(self, y):
        return int(round(self.oy + y * self.escala))

    def r(self, raio):
        return max(1, int(round(raio * self.escala)))

    def mundo(self, sx, sy):
        return (sx - self.ox) / self.escala, (sy - self.oy) / self.escala
