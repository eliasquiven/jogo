# -*- coding: utf-8 -*-
"""particles.py — motor de partículas de ambiente.

Muito além do original em Tkinter: usa alpha real, halos de brilho (blend
aditivo), oscilação suave e reciclagem de partículas. Cada cenário ativa um
conjunto de efeitos.
"""

import math
import random
import pygame

# Efeitos por cenário (nome -> tupla de efeitos)
EFEITOS = {
    "covil":     ("brasas", "lava"),
    "forja":     ("brasas",),
    "caverna":   ("gotas", "vagalumes_frios"),
    "lago":      ("vagalumes_frios", "bolhas"),
    "floresta":  ("vagalumes", "poeira"),
    "pantano":   ("nevoa", "bolhas"),
    "montanha":  ("neve",),
    "taverna":   ("brasas",),
    "trono":     ("poeira",),
    "reino":     ("poeira",),
    "amanhecer": ("poeira", "brasas_suave"),
    "vila":      ("poeira_leve",),
    "campo":     ("poeira_leve",),
    "ruinas":    ("poeira_leve",),
}

_glow_cache = {}


def _glow(raio, cor):
    key = (raio, cor)
    s = _glow_cache.get(key)
    if s is None:
        s = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        for r in range(raio, 0, -1):
            a = int(120 * (r / raio) ** 2)
            pygame.draw.circle(s, (cor[0], cor[1], cor[2], 120 - a), (raio, raio), r)
        _glow_cache[key] = s
    return s


class _P:
    __slots__ = ("x", "y", "vx", "vy", "life", "maxlife", "size", "seed", "kind")

    def __init__(self, x, y, vx, vy, life, size, kind, seed=0.0):
        self.x = x; self.y = y; self.vx = vx; self.vy = vy
        self.life = life; self.maxlife = life; self.size = size
        self.kind = kind; self.seed = seed


class ParticleSystem:
    def __init__(self):
        self.efeitos = ()
        self.particulas = []
        self.t = 0.0
        self.w = 800
        self.h = 400
        self.estrelas = []
        self._acc = {}

    def configurar(self, cenario, modo, w, h):
        self.w, self.h = w, h
        if modo == "titulo":
            self.efeitos = ("estrelas", "dragao_titulo")
        elif modo == "combate":
            self.efeitos = EFEITOS.get(cenario, ("poeira_leve",)) + ("combate_poeira",)
        else:
            self.efeitos = EFEITOS.get(cenario, ("poeira_leve",))
        self.particulas = []
        self._acc = dict.fromkeys(self.efeitos, 0.0)
        # estrelas estáticas com fase de cintilação
        self.estrelas = [(random.uniform(0, w), random.uniform(0, h * 0.5),
                          random.uniform(0, math.tau), random.uniform(1, 2))
                         for _ in range(70)]

    # ---- emissão ----
    def _emitir(self, dt):
        taxas = {
            "brasas": 22, "brasas_suave": 8, "lava": 0, "gotas": 16,
            "vagalumes": 0, "vagalumes_frios": 0, "neve": 30, "nevoa": 0,
            "bolhas": 6, "poeira": 10, "poeira_leve": 4, "estrelas": 0,
            "dragao_titulo": 0, "combate_poeira": 3,
        }
        # mantém populações fixas para flutuantes (vagalumes/névoa)
        alvos = {"vagalumes": 14, "vagalumes_frios": 12, "nevoa": 4}
        for e in self.efeitos:
            alvo = alvos.get(e)
            if alvo is not None:
                atuais = sum(1 for p in self.particulas if p.kind == e)
                for _ in range(alvo - atuais):
                    self._spawn(e)
                continue
            taxa = taxas.get(e, 0)
            if taxa <= 0:
                continue
            self._acc[e] = self._acc.get(e, 0.0) + taxa * dt
            while self._acc[e] >= 1:
                self._acc[e] -= 1
                self._spawn(e)

    def _spawn(self, e):
        w, h = self.w, self.h
        if e in ("brasas", "brasas_suave"):
            self.particulas.append(_P(random.uniform(0, w), h + 4,
                random.uniform(-6, 6), random.uniform(-34, -18),
                random.uniform(1.4, 2.8), random.uniform(2, 4), e, random.uniform(0, 6)))
        elif e == "gotas":
            self.particulas.append(_P(random.uniform(0, w), -4,
                0, random.uniform(160, 240), random.uniform(1.0, 1.8),
                random.uniform(2, 3), e))
        elif e == "neve":
            self.particulas.append(_P(random.uniform(0, w), -4,
                random.uniform(-6, 6), random.uniform(20, 45),
                random.uniform(4, 8), random.uniform(2, 4), e, random.uniform(0, 6)))
        elif e in ("vagalumes", "vagalumes_frios"):
            self.particulas.append(_P(random.uniform(0, w), random.uniform(h * 0.2, h * 0.9),
                0, 0, random.uniform(3, 6), random.uniform(2, 3), e, random.uniform(0, 6)))
        elif e == "nevoa":
            self.particulas.append(_P(random.uniform(-100, w), random.uniform(h * 0.55, h * 0.95),
                random.uniform(8, 20), 0, 999, random.uniform(60, 120), e, random.uniform(0, 6)))
        elif e == "bolhas":
            self.particulas.append(_P(random.uniform(0, w), h + 4,
                random.uniform(-4, 4), random.uniform(-30, -16),
                random.uniform(1.5, 3), random.uniform(2, 5), e, random.uniform(0, 6)))
        elif e in ("poeira", "poeira_leve", "combate_poeira"):
            self.particulas.append(_P(random.uniform(0, w), random.uniform(0, h),
                random.uniform(-8, 8), random.uniform(-10, -2),
                random.uniform(3, 6), random.uniform(1, 3), e, random.uniform(0, 6)))

    # ---- atualização ----
    def update(self, dt):
        self.t += dt
        self._emitir(dt)
        vivos = []
        for p in self.particulas:
            p.life -= dt
            if p.life <= 0:
                continue
            if p.kind in ("vagalumes", "vagalumes_frios"):
                # vagueio suave
                p.x += math.sin(self.t * 1.1 + p.seed) * 14 * dt
                p.y += math.cos(self.t * 0.9 + p.seed * 2) * 12 * dt
                if p.life < 0.4:
                    p.life = random.uniform(3, 6)  # recicla brilho
            elif p.kind == "nevoa":
                p.x += p.vx * dt
                if p.x - p.size > self.w:
                    p.x = -p.size * 2
            else:
                p.x += p.vx * dt
                p.y += p.vy * dt
                if p.kind in ("brasas", "brasas_suave"):
                    p.x += math.sin(self.t * 2 + p.seed) * 10 * dt
                if p.kind == "neve":
                    p.x += math.sin(self.t * 1.3 + p.seed) * 16 * dt
            vivos.append(p)
        self.particulas = vivos

    # ---- desenho ----
    def draw(self, surf):
        w, h = self.w, self.h
        if "estrelas" in self.efeitos:
            for (x, y, fase, sz) in self.estrelas:
                b = 0.5 + 0.5 * math.sin(self.t * 2 + fase)
                a = int(120 + 135 * b)
                c = (255, 255, 235, a)
                pygame.draw.circle(surf, c, (int(x), int(y)), int(sz))
        if "lava" in self.efeitos:
            pulso = 0.5 + 0.5 * math.sin(self.t * 1.5)
            raio = int(min(w, h) * 0.5 + pulso * 30)
            g = _glow(raio, (230, 90, 40))
            surf.blit(g, (w // 2 - raio, h - raio // 2), special_flags=pygame.BLEND_RGBA_ADD)

        for p in self.particulas:
            t01 = p.life / p.maxlife if p.maxlife else 1
            if p.kind in ("brasas", "brasas_suave"):
                fade = min(1.0, t01 * 1.6)
                cor = (245, 197, 66) if p.seed % 3 < 1 else ((224, 119, 42) if p.seed % 3 < 2 else (224, 80, 48))
                g = _glow(int(p.size * 3), cor)
                surf.blit(g, (int(p.x - p.size * 3), int(p.y - p.size * 3)),
                          special_flags=pygame.BLEND_RGBA_ADD)
                pygame.draw.circle(surf, (*cor, int(220 * fade)), (int(p.x), int(p.y)), int(p.size))
            elif p.kind == "gotas":
                pygame.draw.line(surf, (150, 190, 220, 200), (p.x, p.y), (p.x, p.y + 6), 1)
            elif p.kind == "neve":
                pygame.draw.circle(surf, (235, 240, 250, 220), (int(p.x), int(p.y)), int(p.size))
            elif p.kind in ("vagalumes", "vagalumes_frios"):
                cor = (120, 220, 255) if p.kind == "vagalumes_frios" else (245, 230, 120)
                b = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(self.t * 3 + p.seed * 3))
                g = _glow(int(p.size * 4), cor)
                gg = pygame.transform.rotozoom(g, 0, max(0.3, b))
                surf.blit(gg, (int(p.x - gg.get_width() / 2), int(p.y - gg.get_height() / 2)),
                          special_flags=pygame.BLEND_RGBA_ADD)
                pygame.draw.circle(surf, (*cor, int(230 * b)), (int(p.x), int(p.y)), max(1, int(p.size * b)))
            elif p.kind == "nevoa":
                layer = pygame.Surface((int(p.size * 2), int(p.size)), pygame.SRCALPHA)
                pygame.draw.ellipse(layer, (180, 190, 175, 26), layer.get_rect())
                surf.blit(layer, (int(p.x - p.size), int(p.y - p.size / 2)))
            elif p.kind == "bolhas":
                a = int(160 * t01)
                pygame.draw.circle(surf, (120, 160, 140, a), (int(p.x), int(p.y)), int(p.size), 1)
            elif p.kind in ("poeira", "poeira_leve", "combate_poeira"):
                a = int(150 * t01)
                cor = (235, 210, 140) if p.kind != "combate_poeira" else (200, 190, 170)
                pygame.draw.circle(surf, (*cor, a), (int(p.x), int(p.y)), max(1, int(p.size)))
