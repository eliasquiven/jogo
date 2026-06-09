# -*- coding: utf-8 -*-
"""theme.py — paleta, fontes e helpers visuais de Crônicas de Pedravale (Pygame)."""

import os
import pygame

# ---- Paleta (tema medieval escuro, herdada do original) ----
FUNDO       = (28, 26, 23)
PAINEL      = (42, 38, 34)
PAINEL_ESC  = (13, 11, 9)
TEXTO       = (232, 220, 192)
BOTAO       = (74, 63, 47)
BOTAO_HOVER = (107, 90, 64)
BORDA       = (122, 92, 52)
OURO        = (217, 164, 65)

# Cores por "tag" de mensagem (igual ao original)
COR_TAG = {
    "narrativa": (232, 220, 192), "titulo": (217, 164, 65), "dano": (224, 106, 91),
    "cura": (127, 201, 127), "crit": (242, 193, 78), "sistema": (154, 160, 166),
    "heroi": (111, 177, 224), "vilao": (176, 127, 208),
}

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


def cor_por_fracao(frac):
    """Verde > amarelo > vermelho conforme a fração cai (RGB)."""
    if frac > 0.6:
        return (127, 201, 127)
    if frac > 0.3:
        return (242, 193, 78)
    return (224, 106, 91)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_cor(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (int(lerp(c1[0], c2[0], t)), int(lerp(c1[1], c2[1], t)), int(lerp(c1[2], c2[2], t)))


def ease_out(t):
    """Easing suave (desacelera no fim)."""
    return 1 - (1 - t) * (1 - t)


_FONT_CACHE = {}


def fonte(tam, bold=False):
    """Fonte do sistema (DejaVu/segoe), cacheada."""
    key = (tam, bold)
    f = _FONT_CACHE.get(key)
    if f is None:
        # SysFont com fallback automático multiplataforma.
        f = pygame.font.SysFont("dejavusans,segoeui,arial,freesans", tam, bold=bold)
        _FONT_CACHE[key] = f
    return f


def gradiente_vertical(surf, rect, cor_topo, cor_base, passos=64):
    """Preenche `rect` com um gradiente vertical suave."""
    x, y, w, h = rect
    passos = max(2, min(passos, h))
    for i in range(passos):
        t = i / (passos - 1)
        cor = lerp_cor(cor_topo, cor_base, t)
        y0 = y + int(h * i / passos)
        y1 = y + int(h * (i + 1) / passos)
        pygame.draw.rect(surf, cor, (x, y0, w, y1 - y0 + 1))
