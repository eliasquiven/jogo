# -*- coding: utf-8 -*-
"""ui.py — widgets de interface em Pygame.

Como o Pygame não tem widgets, aqui vivem: botões com hover, um painel
inferior com rolagem (mouse), entrada de texto, barras de vida/recurso, modal
de confirmação e o render do "console" narrativo sobre o cenário.
"""

import pygame
from . import theme


def wrap_text(texto, font, larg_max):
    """Quebra texto em linhas que cabem em `larg_max` (respeita \\n)."""
    linhas = []
    for paragrafo in texto.split("\n"):
        if not paragrafo:
            linhas.append("")
            continue
        atual = ""
        for palavra in paragrafo.split(" "):
            teste = palavra if not atual else atual + " " + palavra
            if font.size(teste)[0] <= larg_max:
                atual = teste
            else:
                if atual:
                    linhas.append(atual)
                atual = palavra
        if atual:
            linhas.append(atual)
    return linhas


def medir_console(rect_w, log_buffer):
    """Altura (px) necessária para renderizar `log_buffer` em `rect_w` de largura.

    Espelha o acúmulo vertical de render_console para que a cena possa ceder
    exatamente o espaço de que o texto precisa (sem sobrar bloco preto vazio)."""
    larg = rect_w - 28
    total = 12 + 8  # margem inferior + corte superior de render_console
    for texto, tag in log_buffer:
        if not texto.strip():
            total += 6
            continue
        tam = 17 if tag == "titulo" else 15
        bold = tag in ("titulo", "crit", "heroi", "vilao")
        font = theme.fonte(tam, bold)
        for _linha in wrap_text(texto, font, larg):
            total += font.get_height() + 2
        total += 4
    return total


def render_console(surf, rect, log_buffer):
    """Desenha a caixa de texto narrativa (últimas mensagens), de baixo p/ cima."""
    x, y, w, h = rect
    painel = pygame.Surface((w, h), pygame.SRCALPHA)
    painel.fill((13, 11, 9, 232))
    surf.blit(painel, (x, y))
    pygame.draw.rect(surf, theme.BORDA, rect, 2)

    larg = w - 28
    yy = y + h - 12
    for texto, tag in reversed(log_buffer):
        if not texto.strip():
            yy -= 6
            continue
        cor = theme.COR_TAG.get(tag, theme.TEXTO)
        bold = tag in ("titulo", "crit", "heroi", "vilao")
        tam = 17 if tag == "titulo" else 15
        font = theme.fonte(tam, bold)
        linhas = wrap_text(texto, font, larg)
        for linha in reversed(linhas):
            img = font.render(linha, True, cor)
            yy -= img.get_height() + 2
            if yy < y + 8:
                return
            surf.blit(img, (x + 14, yy))
        yy -= 4


def barra(surf, cx, y, w, atual, maximo, cor, etiqueta):
    """Barra horizontal centrada em cx com rótulo acima."""
    x0 = int(cx - w / 2)
    frac = max(0.0, min(1.0, atual / maximo)) if maximo else 0.0
    pygame.draw.rect(surf, (21, 19, 15), (x0, y, w, 14))
    pygame.draw.rect(surf, (0, 0, 0), (x0, y, w, 14), 1)
    if frac > 0:
        pygame.draw.rect(surf, cor, (x0 + 1, y + 1, max(3, int((w - 2) * frac)), 12))
    font = theme.fonte(12, True)
    img = font.render(f"{etiqueta}  {max(0, atual)}/{maximo}", True, theme.TEXTO)
    surf.blit(img, (cx - img.get_width() // 2, y - 16))


class Button:
    def __init__(self, label, callback, cor=None, icone=None):
        self.label = label
        self.callback = callback
        self.cor = cor or theme.BOTAO
        self.icone = icone
        self.rect = pygame.Rect(0, 0, 0, 0)

    def draw(self, surf, mouse, clip_top, clip_bottom):
        r = self.rect
        if r.bottom < clip_top or r.top > clip_bottom:
            return
        hover = r.collidepoint(mouse)
        cor = theme.BOTAO_HOVER if hover else self.cor
        pygame.draw.rect(surf, cor, r, border_radius=4)
        pygame.draw.rect(surf, theme.BORDA, r, 2, border_radius=4)
        font = theme.fonte(15)
        x = r.x + 10
        if self.icone:
            iy = r.y + (r.h - self.icone.get_height()) // 2
            surf.blit(self.icone, (x, iy))
            x += self.icone.get_width() + 8
        larg = r.w - (x - r.x) - 10
        linhas = wrap_text(self.label, font, larg)
        total_h = len(linhas) * (font.get_height())
        yy = r.y + (r.h - total_h) // 2
        for linha in linhas:
            img = font.render(linha, True, theme.TEXTO)
            surf.blit(img, (x, yy))
            yy += font.get_height()


class TextInput:
    def __init__(self, texto=""):
        self.texto = texto
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.ativo = True
        self._cursor_t = 0.0

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return "enter"
            elif event.unicode and event.unicode.isprintable() and len(self.texto) < 20:
                self.texto += event.unicode
        return None

    def update(self, dt):
        self._cursor_t += dt

    def draw(self, surf):
        pygame.draw.rect(surf, (21, 19, 15), self.rect)
        pygame.draw.rect(surf, theme.BORDA, self.rect, 2)
        font = theme.fonte(18)
        cursor = "|" if (int(self._cursor_t * 2) % 2 == 0 and self.ativo) else ""
        img = font.render(self.texto + cursor, True, theme.TEXTO)
        surf.blit(img, (self.rect.x + 8, self.rect.y + (self.rect.h - img.get_height()) // 2))


class PainelInferior:
    """Pilha vertical de linhas (botões/labels/input) com rolagem se exceder."""
    GAP = 6

    def __init__(self):
        self.linhas = []       # list de ("buttons",[Button..]) | ("label",txt,cor) | ("input",TextInput) | ("space",px)
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.scroll = 0
        self.altura_total = 0
        self._max_scroll = 0

    def limpar(self):
        self.linhas = []
        self.scroll = 0

    def add_botoes(self, botoes, alturas=None):
        self.linhas.append(("buttons", botoes))

    def add_label(self, texto, cor=None):
        self.linhas.append(("label", texto, cor or theme.TEXTO))

    def add_input(self, ti):
        self.linhas.append(("input", ti))

    def add_espaco(self, px=8):
        self.linhas.append(("space", px))

    def todos_botoes(self):
        out = []
        for linha in self.linhas:
            if linha[0] == "buttons":
                out.extend(linha[1])
        return out

    def _altura_linha(self, linha, larg):
        if linha[0] == "buttons":
            font = theme.fonte(15)
            maxh = 36
            n = len(linha[1])
            bw = (larg - (n - 1) * self.GAP) / max(1, n)
            for b in linha[1]:
                ic = (b.icone.get_width() + 8) if b.icone else 0
                ls = wrap_text(b.label, font, bw - 20 - ic)
                maxh = max(maxh, len(ls) * font.get_height() + 16)
            return int(maxh)
        if linha[0] == "label":
            font = theme.fonte(14)
            ls = wrap_text(linha[1], font, larg)
            return len(ls) * (font.get_height() + 1) + 4
        if linha[0] == "input":
            return 38
        if linha[0] == "space":
            return linha[1]
        return 0

    def altura_conteudo(self, larg_total):
        """Altura (px) que a pilha de linhas ocupa numa largura de painel `larg_total`."""
        larg = larg_total - 16
        y = 0
        for linha in self.linhas:
            y += self._altura_linha(linha, larg) + 4
        return y

    def layout(self, rect):
        self.rect = pygame.Rect(rect)
        larg = self.rect.w - 16
        y = 0
        for linha in self.linhas:
            h = self._altura_linha(linha, larg)
            if linha[0] == "buttons":
                n = len(linha[1])
                bw = (larg - (n - 1) * self.GAP) / max(1, n)
                for i, b in enumerate(linha[1]):
                    b.rect = pygame.Rect(int(self.rect.x + 8 + i * (bw + self.GAP)), y, int(bw), h)
                    b._y_rel = y
            elif linha[0] == "input":
                linha[1].rect = pygame.Rect(self.rect.x + 8, y, larg, h - 6)
                linha[1]._y_rel = y
            y += h + 4
        self.altura_total = y
        self._max_scroll = max(0, self.altura_total - self.rect.h)
        self.scroll = max(0, min(self.scroll, self._max_scroll))

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll = max(0, min(self._max_scroll, self.scroll - event.y * 28))
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.rect.collidepoint(event.pos):
                return None
            mx, my = event.pos
            my_virtual = my + self.scroll
            for b in self.todos_botoes():
                # rect.y é absoluto (offset aplicado no draw); reconstruímos virtual
                top = self.rect.y + b._y_rel
                if b.rect.x <= mx <= b.rect.right and top <= my_virtual <= top + b.rect.h:
                    return b.callback
        return None

    def update(self, dt):
        for linha in self.linhas:
            if linha[0] == "input":
                linha[1].update(dt)

    def draw(self, surf, mouse):
        pygame.draw.rect(surf, theme.PAINEL, self.rect)
        prev_clip = surf.get_clip()
        surf.set_clip(self.rect)
        font_l = theme.fonte(14)
        y = 0
        larg = self.rect.w - 16
        for linha in self.linhas:
            h = self._altura_linha(linha, larg)
            if linha[0] == "buttons":
                for b in linha[1]:
                    saved = b.rect.copy()
                    b.rect = pygame.Rect(saved.x, self.rect.y + y - self.scroll, saved.w, saved.h)
                    b.draw(surf, mouse, self.rect.top, self.rect.bottom)
                    b.rect = saved
            elif linha[0] == "label":
                yy = self.rect.y + y - self.scroll
                for ln in wrap_text(linha[1], font_l, larg):
                    img = font_l.render(ln, True, linha[2])
                    surf.blit(img, (self.rect.x + 8, yy))
                    yy += font_l.get_height() + 1
            elif linha[0] == "input":
                ti = linha[1]
                saved = ti.rect.copy()
                ti.rect = pygame.Rect(saved.x, self.rect.y + y - self.scroll, saved.w, saved.h)
                ti.draw(surf)
                ti.rect = saved
            y += h + 4
        surf.set_clip(prev_clip)
        # indicador de rolagem
        if self._max_scroll > 0:
            bar_h = max(20, int(self.rect.h * self.rect.h / self.altura_total))
            bar_y = self.rect.y + int((self.rect.h - bar_h) * self.scroll / self._max_scroll)
            pygame.draw.rect(surf, theme.BORDA, (self.rect.right - 6, bar_y, 4, bar_h), border_radius=2)


class Modal:
    def __init__(self, mensagem, opcoes):
        # opcoes: list de (label, callback)
        self.mensagem = mensagem
        self.opcoes = opcoes
        self.botoes = [Button(lbl, cb) for lbl, cb in opcoes]

    def layout(self, w, h):
        bw, bh = 460, 220
        self.rect = pygame.Rect((w - bw) // 2, (h - bh) // 2, bw, bh)
        for i, b in enumerate(self.botoes):
            b.rect = pygame.Rect(self.rect.x + 20, self.rect.y + 90 + i * 42, bw - 40, 36)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self.botoes:
                if b.rect.collidepoint(event.pos):
                    return b.callback
        return None

    def draw(self, surf, mouse):
        w, h = surf.get_size()
        over = pygame.Surface((w, h), pygame.SRCALPHA)
        over.fill((0, 0, 0, 150))
        surf.blit(over, (0, 0))
        pygame.draw.rect(surf, theme.PAINEL, self.rect, border_radius=6)
        pygame.draw.rect(surf, theme.OURO, self.rect, 2, border_radius=6)
        font = theme.fonte(15)
        yy = self.rect.y + 16
        for ln in wrap_text(self.mensagem, font, self.rect.w - 32):
            surf.blit(font.render(ln, True, theme.TEXTO), (self.rect.x + 16, yy))
            yy += font.get_height() + 2
        for b in self.botoes:
            b.draw(surf, mouse, 0, h)
