# -*- coding: utf-8 -*-
"""backgrounds.py — desenho dos 14 cenários (Pygame).

Céu em gradiente + silhuetas em camadas. Fundos suaves combinam bem com
sprites pixelados (padrão comum em jogos indie). As partículas (particles.py)
somam a atmosfera por cima.
"""

import math
import os
import pygame
from . import theme
from .theme import gradiente_vertical

_img_cache = {}


def _imagem(nome):
    """Carrega (uma vez) uma imagem de assets/. Retorna None se faltar."""
    if nome not in _img_cache:
        try:
            _img_cache[nome] = pygame.image.load(os.path.join(theme.ASSETS_DIR, nome)).convert_alpha()
        except Exception:
            _img_cache[nome] = None
    return _img_cache[nome]


def _cobrir(surf, img, w, h, offset_y=0):
    """Desenha `img` preenchendo (w,h) preservando proporção (cover, centralizado)."""
    iw, ih = img.get_size()
    escala = max(w / iw, h / ih)
    sw, sh = max(1, int(iw * escala)), max(1, int(ih * escala))
    chave = ("scaled", id(img), w, h)
    scaled = _img_cache.get(chave)
    if scaled is None:
        scaled = pygame.transform.scale(img, (sw, sh))
        _img_cache[chave] = scaled
    y = (h - sh) // 2 + offset_y
    if sh > h:
        y = max(h - sh, min(0, y))
    surf.blit(scaled, ((w - sw) // 2, y))


def _poly(surf, cor, pts):
    pygame.draw.polygon(surf, cor, pts)


def _ceu(surf, w, h, topo, base, noturno=False):
    gradiente_vertical(surf, (0, 0, w, h), topo, base)


def _sol(surf, x, y, r, cor):
    glow = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    for i in range(r * 2, 0, -2):
        a = int(70 * (1 - i / (r * 2)))
        pygame.draw.circle(glow, (*cor, a), (r * 2, r * 2), i)
    surf.blit(glow, (x - r * 2, y - r * 2))
    pygame.draw.circle(surf, cor, (x, y), r)


def vila(surf, w, h):
    # Pedravale: usa a arte dedicada (assets/vila.png) se houver — cenário-base da história.
    img = _imagem("vila.png")
    if img:
        _cobrir(surf, img, w, h)
        return
    _ceu(surf, w, h, (58, 52, 78), (150, 96, 78))
    _sol(surf, int(w * 0.8), int(h * 0.22), 26, (240, 180, 120))
    chao = int(h * 0.7)
    pygame.draw.rect(surf, (70, 84, 56), (0, chao, w, h - chao))
    # casas de pedra
    for fx in (0.1, 0.32, 0.55, 0.78):
        bx = int(w * fx); bw = int(w * 0.14); bh = int(h * 0.26)
        by = chao - bh
        pygame.draw.rect(surf, (108, 96, 84), (bx, by, bw, bh))
        pygame.draw.rect(surf, (60, 52, 46), (bx, by, bw, bh), 2)
        _poly(surf, (120, 70, 54), [(bx - 6, by), (bx + bw + 6, by), (bx + bw // 2, by - 24)])
        # janelas acesas
        pygame.draw.rect(surf, (245, 205, 120), (bx + bw // 4, by + bh // 3, 10, 12))
        pygame.draw.rect(surf, (245, 205, 120), (bx + bw - bw // 4 - 10, by + bh // 3, 10, 12))


def campo(surf, w, h):
    _ceu(surf, w, h, (120, 170, 220), (200, 220, 210))
    _sol(surf, int(w * 0.18), int(h * 0.2), 24, (255, 240, 180))
    chao = int(h * 0.62)
    for fy, cor in ((0.62, (96, 140, 70)), (0.74, (80, 124, 58)), (0.86, (66, 108, 48))):
        pygame.draw.ellipse(surf, cor, (-w * 0.2, int(h * fy), w * 1.4, h))
    # trilha
    _poly(surf, (150, 130, 92), [(w * 0.42, h), (w * 0.58, h), (w * 0.53, chao), (w * 0.49, chao)])


def floresta(surf, w, h):
    # usa a arte dedicada (assets/floresta.png) se houver — encontros de combate da floresta.
    img = _imagem("floresta.png")
    if img:
        _cobrir(surf, img, w, h)
        return
    _ceu(surf, w, h, (32, 54, 48), (54, 74, 56))
    chao = int(h * 0.78)
    pygame.draw.rect(surf, (38, 52, 36), (0, chao, w, h - chao))
    # árvores em camadas
    for camada, (cor, esc, n) in enumerate((((40, 64, 50), 0.55, 6), ((52, 80, 58), 0.7, 7))):
        for i in range(n):
            tx = int(w * (i + 0.5) / n + (camada * 30))
            ty = int(h * esc)
            tw = int(w * 0.09)
            _poly(surf, cor, [(tx - tw, ty), (tx + tw, ty), (tx, ty - h * 0.42)])
            pygame.draw.rect(surf, (60, 44, 30), (tx - 4, ty, 8, chao - ty))


def reino(surf, w, h):
    _ceu(surf, w, h, (70, 90, 140), (170, 150, 130))
    chao = int(h * 0.72)
    pygame.draw.rect(surf, (96, 90, 82), (0, chao, w, h - chao))
    # muralha + portão
    pygame.draw.rect(surf, (150, 140, 120), (int(w * 0.2), int(h * 0.3), int(w * 0.6), chao - int(h * 0.3)))
    # torres
    for fx in (0.18, 0.78):
        tx = int(w * fx)
        pygame.draw.rect(surf, (170, 158, 134), (tx - 22, int(h * 0.22), 44, chao - int(h * 0.22)))
        _poly(surf, (180, 70, 60), [(tx - 26, int(h * 0.22)), (tx + 26, int(h * 0.22)), (tx, int(h * 0.12))])
    # portão arco
    gx, gy, gw, gh = int(w * 0.42), int(h * 0.44), int(w * 0.16), chao - int(h * 0.44)
    pygame.draw.rect(surf, (60, 46, 34), (gx, gy, gw, gh))
    pygame.draw.arc(surf, (217, 164, 65), (gx, gy - gw // 2, gw, gw), 0, math.pi, 4)


def caverna(surf, w, h):
    # Cavernas de Veludo: usa a arte pixel-art (assets/caverna_veludo.png) se houver.
    img = _imagem("caverna_veludo.png")
    if img:
        _cobrir(surf, img, w, h, offset_y=-12)
        return
    _ceu(surf, w, h, (20, 22, 30), (28, 26, 34))
    # rochas
    _poly(surf, (40, 38, 50), [(0, 0), (w, 0), (w, h * 0.2), (w * 0.7, h * 0.32),
                               (w * 0.4, h * 0.18), (0, h * 0.3)])
    _poly(surf, (34, 32, 44), [(0, h), (w, h), (w, h * 0.78), (w * 0.6, h * 0.68),
                               (w * 0.3, h * 0.82), (0, h * 0.72)])
    # cristais brilhantes
    for fx, fy, cor in ((0.2, 0.55, (120, 200, 255)), (0.7, 0.4, (160, 130, 240)),
                        (0.85, 0.7, (120, 200, 255))):
        cx, cy = int(w * fx), int(h * fy)
        glow = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*cor, 60), (20, 20), 20)
        surf.blit(glow, (cx - 20, cy - 20))
        _poly(surf, cor, [(cx, cy - 14), (cx + 5, cy), (cx, cy + 14), (cx - 5, cy)])


def covil(surf, w, h):
    # Covil do dragão: usa a arte dedicada (assets/covil.png) se houver — combate com o dragão.
    img = _imagem("covil.png")
    if img:
        _cobrir(surf, img, w, h)
        return
    _ceu(surf, w, h, (40, 18, 20), (70, 24, 22))
    _poly(surf, (28, 14, 16), [(0, 0), (w, 0), (w, h * 0.25), (w * 0.5, h * 0.36), (0, h * 0.28)])
    chao = int(h * 0.78)
    pygame.draw.rect(surf, (44, 22, 22), (0, chao, w, h - chao))
    # poça de lava
    pygame.draw.ellipse(surf, (220, 90, 40), (int(w * 0.2), chao - 10, int(w * 0.6), 40))
    pygame.draw.ellipse(surf, (255, 170, 70), (int(w * 0.3), chao - 4, int(w * 0.4), 24))
    # montes de ouro
    for fx in (0.15, 0.82):
        pygame.draw.ellipse(surf, (200, 160, 60), (int(w * fx) - 30, chao - 18, 60, 24))


def taverna(surf, w, h):
    surf.fill((58, 42, 30))
    # parede de madeira
    for i in range(0, w, 28):
        pygame.draw.line(surf, (48, 34, 24), (i, 0), (i, int(h * 0.8)), 2)
    chao = int(h * 0.8)
    pygame.draw.rect(surf, (74, 52, 34), (0, chao, w, h - chao))
    # viga
    pygame.draw.rect(surf, (40, 28, 20), (0, int(h * 0.12), w, 14))
    # lareira
    fx = int(w * 0.78)
    pygame.draw.rect(surf, (50, 40, 36), (fx, int(h * 0.4), int(w * 0.16), chao - int(h * 0.4)))
    glow = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 150, 60, 90), (60, 60), 50)
    surf.blit(glow, (fx + int(w * 0.08) - 60, int(h * 0.6) - 60))
    pygame.draw.ellipse(surf, (240, 140, 50), (fx + 10, int(h * 0.62), int(w * 0.1), 24))
    # balcão
    pygame.draw.rect(surf, (60, 42, 28), (int(w * 0.08), int(h * 0.62), int(w * 0.34), 18))


def forja(surf, w, h):
    surf.fill((40, 34, 32))
    chao = int(h * 0.78)
    pygame.draw.rect(surf, (54, 46, 42), (0, chao, w, h - chao))
    # fornalha
    fx, fy = int(w * 0.6), int(h * 0.3)
    pygame.draw.rect(surf, (60, 52, 48), (fx, fy, int(w * 0.3), chao - fy))
    glow = pygame.Surface((160, 160), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 130, 40, 120), (80, 80), 70)
    surf.blit(glow, (fx + int(w * 0.15) - 80, fy + 60 - 80))
    pygame.draw.arc(surf, (255, 170, 60), (fx + 20, fy + 30, int(w * 0.2), int(w * 0.2)), math.pi, math.tau, 6)
    # bigorna
    ax = int(w * 0.25)
    pygame.draw.rect(surf, (50, 50, 58), (ax, chao - 30, 50, 16))
    pygame.draw.rect(surf, (40, 40, 48), (ax + 16, chao - 14, 18, 14))


def trono(surf, w, h):
    _ceu(surf, w, h, (40, 36, 56), (60, 50, 64))
    chao = int(h * 0.74)
    pygame.draw.rect(surf, (70, 62, 60), (0, chao, w, h - chao))
    # colunas
    for fx in (0.12, 0.32, 0.68, 0.88):
        cx = int(w * fx)
        pygame.draw.rect(surf, (150, 140, 130), (cx - 12, int(h * 0.18), 24, chao - int(h * 0.18)))
    # degraus + tapete
    for i in range(3):
        pygame.draw.rect(surf, (90, 50, 50), (int(w * 0.4) - i * 14, chao - 10 - i * 10, int(w * 0.2) + i * 28, 10))
    _poly(surf, (160, 40, 50), [(w * 0.46, chao), (w * 0.54, chao), (w * 0.58, h), (w * 0.42, h)])
    # trono
    tx = int(w * 0.5)
    pygame.draw.rect(surf, (180, 150, 70), (tx - 26, int(h * 0.34), 52, int(h * 0.3)))
    _poly(surf, (200, 170, 80), [(tx - 26, int(h * 0.34)), (tx + 26, int(h * 0.34)), (tx, int(h * 0.24))])


def pantano(surf, w, h):
    _ceu(surf, w, h, (44, 54, 44), (60, 68, 52))
    agua = int(h * 0.6)
    pygame.draw.rect(surf, (46, 58, 44), (0, agua, w, h - agua))
    pygame.draw.ellipse(surf, (54, 66, 50), (int(w * 0.1), agua + 20, int(w * 0.5), 40))
    # árvores mortas
    for fx in (0.2, 0.45, 0.72, 0.9):
        tx = int(w * fx)
        pygame.draw.line(surf, (40, 36, 30), (tx, agua), (tx, int(h * 0.25)), 5)
        pygame.draw.line(surf, (40, 36, 30), (tx, int(h * 0.4)), (tx + 18, int(h * 0.3)), 3)
        pygame.draw.line(surf, (40, 36, 30), (tx, int(h * 0.5)), (tx - 16, int(h * 0.42)), 3)
    # altar submerso
    pygame.draw.rect(surf, (90, 96, 88), (int(w * 0.42), agua - 6, int(w * 0.16), 22))


def montanha(surf, w, h):
    _ceu(surf, w, h, (110, 130, 165), (200, 210, 220))
    # picos
    _poly(surf, (120, 130, 150), [(0, h * 0.7), (w * 0.3, h * 0.2), (w * 0.55, h * 0.6), (w * 0.8, h * 0.25), (w, h * 0.6), (w, h), (0, h)])
    _poly(surf, (235, 240, 248), [(w * 0.3, h * 0.2), (w * 0.36, h * 0.34), (w * 0.24, h * 0.34)])
    _poly(surf, (235, 240, 248), [(w * 0.8, h * 0.25), (w * 0.86, h * 0.38), (w * 0.74, h * 0.38)])
    # abismo + ponte
    pygame.draw.rect(surf, (40, 46, 60), (0, int(h * 0.78), w, h))
    pygame.draw.rect(surf, (90, 80, 64), (0, int(h * 0.78), w, 10))


def lago(surf, w, h):
    _ceu(surf, w, h, (18, 24, 34), (24, 32, 44))
    agua = int(h * 0.55)
    gradiente_vertical(surf, (0, agua, w, h - agua), (30, 50, 70), (16, 26, 40))
    # cristal central
    cx, cy = int(w * 0.5), int(agua - 6)
    glow = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.circle(glow, (120, 210, 255, 70), (60, 60), 55)
    surf.blit(glow, (cx - 60, cy - 60))
    _poly(surf, (150, 220, 255), [(cx, cy - 26), (cx + 9, cy), (cx, cy + 26), (cx - 9, cy)])
    # reflexo
    for i in range(6):
        yy = agua + 12 + i * 10
        pygame.draw.line(surf, (120, 200, 240, 60), (cx - 18, yy), (cx + 18, yy), 1)


def ruinas(surf, w, h):
    _ceu(surf, w, h, (60, 60, 80), (120, 110, 110))
    chao = int(h * 0.74)
    pygame.draw.rect(surf, (80, 76, 70), (0, chao, w, h - chao))
    for fx in (0.15, 0.4, 0.66, 0.88):
        cx = int(w * fx); ch = int(h * (0.3 + 0.12 * (fx * 3 % 1)))
        pygame.draw.rect(surf, (140, 132, 120), (cx - 12, chao - ch, 24, ch))
        pygame.draw.rect(surf, (110, 102, 92), (cx - 16, chao - ch, 32, 10))


def amanhecer(surf, w, h):
    gradiente_vertical(surf, (0, 0, w, h), (250, 180, 110), (255, 230, 180))
    _sol(surf, int(w * 0.5), int(h * 0.55), 50, (255, 240, 190))
    # colinas distantes
    for fy, cor in ((0.7, (210, 150, 110)), (0.82, (180, 120, 96))):
        pygame.draw.ellipse(surf, cor, (-w * 0.2, int(h * fy), w * 1.4, h))


_CENAS = {
    "vila": vila, "campo": campo, "floresta": floresta, "reino": reino,
    "caverna": caverna, "covil": covil, "taverna": taverna, "forja": forja,
    "trono": trono, "pantano": pantano, "montanha": montanha, "lago": lago,
    "ruinas": ruinas, "amanhecer": amanhecer,
}


def desenhar_fundo(surf, w, h, cenario):
    _CENAS.get(cenario, campo)(surf, w, h)


def desenhar_titulo(surf, w, h):
    """Desenha o fundo da tela de título. Retorna True se usou a arte dedicada
    (assets/titulo.jpg) — que já traz título e dragão embutidos, dispensando o
    overlay procedural; False se caiu no fundo procedural."""
    img = _imagem("titulo.jpg")
    if img:
        _cobrir(surf, img, w, h)
        return True
    _ceu(surf, w, h, (16, 14, 26), (40, 24, 36), noturno=True)
    chao = int(h * 0.62)
    _poly(surf, (20, 16, 28), [(0, chao), (w * 0.2, chao - 70), (w * 0.32, chao - 35),
                               (w * 0.5, chao - 95), (w * 0.66, chao - 45), (w * 0.82, chao - 85),
                               (w, chao - 20), (w, h), (0, h)])
    return False


def desenhar_mapa(surf, w, h):
    """Desenha o mapa a partir da arte dedicada (assets/mapa.jpg), que já traz
    as regiões e o título. Retorna True se usou a imagem; False caso contrário
    (cabe ao chamador desenhar o mapa procedural)."""
    img = _imagem("mapa.jpg")
    if img:
        _cobrir(surf, img, w, h)
        return True
    return False
