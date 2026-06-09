# -*- coding: utf-8 -*-
"""assets.py — sprites do jogo.

Combina pixel-art Kenney (CC0, tiny-dungeon) para heróis e monstros comuns
com sprites pixel-art próprios (Lobo, Orc, Troll, Dragão, Esqueleto, Espírito)
desenhados em baixa resolução e escalados com nearest-neighbor, para que TUDO
compartilhe o mesmo estilo pixelado.
"""

import os
import pygame
from . import theme

TD = 16  # tamanho do tile no tiny-dungeon (packed, sem margem)

# Heróis (col, row) no tiny_dungeon.png (fallback se a arte dedicada faltar)
HEROI_TILE = {"Cavaleiro": (0, 8), "Mago": (0, 7), "Arqueiro": (4, 9)}

# Arte dedicada por classe (issue #1). Fallback: HEROI_TILE.
HEROI_ART = {"Cavaleiro": "cavaleiro.png", "Mago": "mago.png", "Arqueiro": "arqueira.png"}

# Monstros com bom equivalente Kenney
MONSTRO_TILE = {"Slime": (0, 9), "Goblin": (1, 9)}

# Altura de cada inimigo em pixels de tela (herdado do original)
SPRITE_ALTURA = {"Slime": 70, "Goblin": 110, "Lobo": 95, "Esqueleto": 130,
                 "Bruxa": 138, "Orc": 150, "Troll": 180, "Drag": 220}

# Ícones de item (col,row) no tiny_dungeon
ITEM_TILE = {
    "cura": (7, 9), "cura_g": (7, 9), "recurso": (8, 9), "antidoto": (6, 9),
    "captura": (5, 9), "arma": (7, 8), "armadura": (6, 8),
}


def altura_inimigo(nome):
    for chave, h in SPRITE_ALTURA.items():
        if chave in nome:
            return h
    return 110


# ---------------------------------------------------------------------------
#  Sprites pixel-art próprios (desenhados em surface pequena, depois escalados)
# ---------------------------------------------------------------------------
def _surf(w, h):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    return s


def _px(s, cor, x, y, w=1, h=1):
    pygame.draw.rect(s, cor, (x, y, w, h))


def _wolf():
    s = _surf(26, 18)
    corpo = (96, 99, 110); esc = (66, 68, 78); olho = (242, 193, 78)
    # corpo
    pygame.draw.ellipse(s, corpo, (4, 5, 16, 8))
    pygame.draw.ellipse(s, esc, (4, 5, 16, 8), 1)
    # cabeça
    pygame.draw.polygon(s, corpo, [(18, 6), (25, 4), (24, 12), (18, 12)])
    pygame.draw.polygon(s, esc, [(18, 6), (25, 4), (24, 12), (18, 12)], 1)
    # orelha
    pygame.draw.polygon(s, corpo, [(19, 6), (21, 1), (23, 6)])
    # focinho/dente
    _px(s, (235, 235, 240), 24, 9, 1, 2)
    _px(s, olho, 22, 7, 1, 1)
    # patas
    for px in (6, 10, 14, 17):
        _px(s, esc, px, 12, 2, 5)
    # cauda
    pygame.draw.polygon(s, corpo, [(4, 7), (0, 4), (4, 10)])
    return s


def _skeleton():
    s = _surf(16, 24)
    osso = (228, 228, 220); esc = (150, 150, 142); olho = (40, 40, 40)
    # crânio
    pygame.draw.ellipse(s, osso, (3, 1, 10, 9))
    _px(s, olho, 5, 4, 2, 2); _px(s, olho, 9, 4, 2, 2)
    _px(s, esc, 7, 7, 2, 2)
    # coluna/costelas
    _px(s, osso, 7, 10, 2, 9)
    for y in (11, 13, 15):
        _px(s, osso, 4, y, 8, 1)
    # braços
    _px(s, osso, 2, 11, 2, 6); _px(s, osso, 12, 11, 2, 6)
    # pernas
    _px(s, osso, 5, 19, 2, 5); _px(s, osso, 9, 19, 2, 5)
    return s


def _orc():
    s = _surf(20, 26)
    pele = (96, 150, 70); esc = (60, 100, 44); pano = (90, 60, 40)
    olho = (224, 80, 60); tusk = (235, 235, 220)
    # pernas
    _px(s, esc, 5, 20, 4, 6); _px(s, esc, 11, 20, 4, 6)
    # tronco
    pygame.draw.rect(s, pele, (4, 10, 12, 11))
    pygame.draw.rect(s, esc, (4, 10, 12, 11), 1)
    _px(s, pano, 5, 17, 10, 3)  # tanga
    # braços
    _px(s, pele, 1, 11, 3, 8); _px(s, pele, 16, 11, 3, 8)
    # cabeça
    pygame.draw.rect(s, pele, (5, 2, 10, 9))
    pygame.draw.rect(s, esc, (5, 2, 10, 9), 1)
    _px(s, olho, 7, 5, 2, 1); _px(s, olho, 11, 5, 2, 1)
    _px(s, tusk, 7, 9, 1, 2); _px(s, tusk, 12, 9, 1, 2)
    # clava
    _px(s, (120, 84, 50), 18, 6, 2, 10)
    pygame.draw.circle(s, (120, 84, 50), (19, 6), 3)
    return s


def _troll():
    s = _surf(26, 30)
    pele = (120, 138, 96); esc = (78, 96, 60); olho = (242, 193, 78)
    # pernas grossas
    _px(s, esc, 6, 23, 6, 7); _px(s, esc, 14, 23, 6, 7)
    # corpo curvado
    pygame.draw.ellipse(s, pele, (3, 9, 20, 16))
    pygame.draw.ellipse(s, esc, (3, 9, 20, 16), 1)
    # braços longos
    pygame.draw.rect(s, pele, (0, 11, 4, 13))
    pygame.draw.rect(s, pele, (22, 11, 4, 13))
    _px(s, esc, 0, 22, 4, 3); _px(s, esc, 22, 22, 4, 3)
    # cabeça pequena
    pygame.draw.ellipse(s, pele, (9, 2, 9, 9))
    _px(s, olho, 11, 5, 2, 1); _px(s, olho, 14, 5, 2, 1)
    _px(s, (235, 235, 220), 11, 8, 1, 2)  # presa
    return s


def _spirit():
    s = _surf(18, 22)
    base = (140, 230, 180, 200); glow = (110, 200, 150, 110); olho = (240, 255, 245)
    pygame.draw.circle(s, glow, (9, 9), 9)
    pygame.draw.ellipse(s, base, (4, 2, 10, 12))
    # cauda fantasmagórica
    pygame.draw.polygon(s, base, [(4, 12), (6, 20), (9, 14), (12, 20), (14, 12)])
    _px(s, olho, 6, 6, 2, 2); _px(s, olho, 10, 6, 2, 2)
    return s


def _dragon():
    """Vorthak — chefe. Pixel-art encorpado e ameaçador."""
    s = _surf(40, 32)
    corpo = (120, 40, 48); esc = (78, 24, 30); asa = (90, 34, 60)
    asa_esc = (60, 22, 40); olho = (255, 210, 70); chifre = (230, 220, 200)
    fogo = (255, 140, 50)
    # cauda
    pygame.draw.polygon(s, corpo, [(2, 22), (10, 18), (10, 24)])
    # asa traseira
    pygame.draw.polygon(s, asa_esc, [(12, 12), (2, 2), (8, 14), (4, 16), (14, 18)])
    # corpo
    pygame.draw.ellipse(s, corpo, (8, 12, 20, 14))
    pygame.draw.ellipse(s, esc, (8, 12, 20, 14), 1)
    # asa dianteira (membrana)
    pygame.draw.polygon(s, asa, [(16, 12), (10, 0), (22, 6), (28, 2), (26, 16)])
    pygame.draw.polygon(s, asa_esc, [(16, 12), (10, 0), (22, 6), (28, 2), (26, 16)], 1)
    # pescoço + cabeça
    pygame.draw.polygon(s, corpo, [(24, 14), (32, 6), (39, 8), (38, 14), (28, 18)])
    pygame.draw.polygon(s, esc, [(24, 14), (32, 6), (39, 8), (38, 14), (28, 18)], 1)
    # chifres
    pygame.draw.polygon(s, chifre, [(33, 6), (34, 1), (36, 6)])
    pygame.draw.polygon(s, chifre, [(36, 6), (38, 2), (39, 7)])
    # olho
    _px(s, olho, 35, 9, 2, 2)
    # narina/fogo
    _px(s, fogo, 39, 11, 1, 1)
    # patas
    _px(s, esc, 12, 25, 3, 5); _px(s, esc, 20, 25, 3, 5)
    # espinhos dorsais
    for hx in (12, 16, 20):
        pygame.draw.polygon(s, esc, [(hx, 13), (hx + 2, 9), (hx + 4, 13)])
    return s


_PROC = {
    "wolf": _wolf, "skeleton": _skeleton, "orc": _orc, "troll": _troll,
    "spirit": _spirit, "dragon": _dragon,
}

# Inimigo (por substring no nome) -> ('tile',(c,r)), ('proc', chave) ou
# ('img', arquivo[, chave_proc_fallback]). Arte dedicada da issue #1.
MONSTRO_ART = {
    "Slime": ("tile", (0, 9)), "Goblin": ("tile", (1, 9)),
    "Lobo": ("img", "lobo.png", "wolf"),
    "Esqueleto": ("img", "esqueleto.png", "skeleton"),
    "Bruxa": ("img", "bruxa.png", "spirit"),
    "Orc": ("img", "orc.png", "orc"),
    "Troll": ("img", "troll.png", "troll"),
    "Drag": ("img", "dragao_vorthak.png", "dragon"),   # arte dedicada (issue #7)
}


class Assets:
    def __init__(self):
        self.tiny = pygame.image.load(os.path.join(theme.ASSETS_DIR, "tiny_dungeon.png")).convert_alpha()
        self.env = pygame.image.load(os.path.join(theme.ASSETS_DIR, "rogue_env.png")).convert_alpha()
        self._cache = {}       # (kind, height) -> Surface escalada
        self._proc_cache = {}  # chave -> surface base
        self._imgs = {}        # nome de arquivo -> Surface (ou None se faltar)

    # --- recortes ---
    def tile(self, c, r):
        return self.tiny.subsurface((c * TD, r * TD, TD, TD))

    def env_tile(self, c, r):
        return self.env.subsurface((c * 17, r * 17, 16, 16))

    def _proc_base(self, chave):
        s = self._proc_cache.get(chave)
        if s is None:
            s = _PROC[chave]()
            self._proc_cache[chave] = s
        return s

    def _imagem(self, nome):
        """Carrega (uma vez) uma imagem de assets/. None se faltar."""
        if nome not in self._imgs:
            try:
                self._imgs[nome] = pygame.image.load(os.path.join(theme.ASSETS_DIR, nome)).convert_alpha()
            except Exception:
                self._imgs[nome] = None
        return self._imgs[nome]

    def _arte(self, kind, val, fallback="dragon"):
        """Resolve (kind, val) para uma surface base: tile Kenney, pixel-art
        procedural ou imagem dedicada (com fallback procedural)."""
        if kind == "tile":
            return self.tile(*val)
        if kind == "img":
            img = self._imagem(val)
            return img if img is not None else self._proc_base(fallback)
        return self._proc_base(val)

    def _escalar_altura(self, base, altura):
        w, h = base.get_size()
        nova_w = max(1, int(w * altura / h))
        # smoothscale para artes ilustradas (grandes); nearest para pixel-art.
        escalar = pygame.transform.smoothscale if h > 64 else pygame.transform.scale
        return escalar(base, (nova_w, altura))

    # --- API pública ---
    def heroi(self, classe, altura, face=1):
        return self._sprite(("heroi", classe, altura, face),
                            self._base_heroi(classe), altura, face)

    def inimigo(self, nome, altura, face=-1):
        return self._sprite(("ini", nome, altura, face),
                            self._base_inimigo(nome), altura, face)

    def aliado(self, nome, altura, face=1):
        return self._sprite(("ali", nome, altura, face),
                            self._base_aliado(nome), altura, face)

    def _sprite(self, key, base, altura, face):
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        surf = self._escalar_altura(base, altura)
        if face < 0:
            surf = pygame.transform.flip(surf, True, False)
        self._cache[key] = surf
        return surf

    def _base_heroi(self, classe):
        nome = HEROI_ART.get(classe)
        if nome:
            img = self._imagem(nome)
            if img is not None:
                return img
        c, r = HEROI_TILE.get(classe, (0, 8))
        return self.tile(c, r)

    def _base_inimigo(self, nome):
        for chave, art in MONSTRO_ART.items():
            if chave in nome:
                return self._arte(*art)
        return self.tile(1, 9)  # default goblin

    def _base_aliado(self, nome):
        n = nome.lower()
        if "lobo" in n:
            img = self._imagem("lobo.png")
            return img if img is not None else self._proc_base("wolf")
        if "espírito" in n or "espirito" in n:
            return self._proc_base("spirit")
        for chave, art in MONSTRO_ART.items():
            if chave.lower() in n:
                return self._arte(*art)
        if "selene" in n:
            return self.tile(4, 9)   # ranger
        return self.tile(2, 7)       # aldeão genérico

    def item_icon(self, nome_efeito_ou_tipo, size=32):
        key = ("item", nome_efeito_ou_tipo, size)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        cr = ITEM_TILE.get(nome_efeito_ou_tipo)
        if not cr:
            return None
        surf = pygame.transform.scale(self.tile(*cr), (size, size))
        self._cache[key] = surf
        return surf
