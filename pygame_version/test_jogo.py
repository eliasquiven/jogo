# -*- coding: utf-8 -*-
"""Arnês de testes headless de Crônicas de Pedravale (versão Pygame).

Roda SEM display (SDL dummy) e valida:
  - integridade do grafo de história (destinos existem, finais terminais,
    alcançabilidade, specs de combate/loot);
  - progressão por eventos únicos (sem farm infinito de recompensas);
  - render headless de todas as telas (título, narrativa, combate, mapa…);
  - dezenas de playthroughs aleatórios chegando a finais.

Uso:  python test_jogo.py        (a partir da pasta pygame_version)
Sai com código != 0 se qualquer asserção falhar.
"""

import os
import sys
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame  # noqa: E402
import core    # noqa: E402

FALHAS = []


def checa(cond, msg):
    print(("  ok  " if cond else "  FALHA ") + msg)
    if not cond:
        FALHAS.append(msg)


def teste_grafo():
    print("== Integridade do grafo de história ==")
    H = core.Historia()
    nos = H.nos
    # Todo destino existe; specs de combate/loot são válidos.
    destinos_ok = True
    for chave, no in nos.items():
        for esc in no.get("escolhas", []):
            d = esc.get("destino")
            if d is not None and d not in nos:
                destinos_ok = False
                print("    destino inexistente:", chave, "->", d)
            comb = esc.get("combate")
            if comb is not None and not isinstance(comb, dict):
                destinos_ok = False
            loot = esc.get("loot")
            if loot is not None and loot not in (True, "arma", "armadura"):
                destinos_ok = False
    checa(destinos_ok, "todos os destinos existem e specs de combate/loot válidos")
    # Finais são terminais.
    finais_reais = [k for k, n in nos.items() if n.get("escolhas", None) == []]
    term_ok = all(n.get("final") for k, n in nos.items() if n.get("escolhas", None) == [])
    checa(term_ok and len(finais_reais) >= 4, f"{len(finais_reais)} finais terminais (>=4)")
    # Alcançabilidade a partir de 'inicio'.
    vistos, pilha = set(), ["inicio"]
    while pilha:
        c = pilha.pop()
        if c in vistos or c not in nos:
            continue
        vistos.add(c)
        for e in nos[c].get("escolhas", []):
            if e.get("destino"):
                pilha.append(e["destino"])
    inalcancaveis = set(nos) - vistos
    checa(not inalcancaveis, f"todos os {len(nos)} nós alcançáveis a partir de 'inicio'"
          + (f" (inalcançáveis: {inalcancaveis})" if inalcancaveis else ""))


def teste_progressao():
    print("== Progressão por eventos únicos (issue #2) ==")
    from game.app import Game
    g = Game()
    g.jogador = core.Personagem("T", "Outro", "Cavaleiro", "Normal")
    H = g.historia
    # Recompensa de hub só uma vez.
    selene = H.get("taverna")["escolhas"][1]
    g.no_atual = "taverna"
    checa(g._escolha_visivel(selene, "taverna:1"), "escolha com recompensa visível na 1ª vez")
    g.processar_escolha(selene, "taverna:1")
    checa("taverna:__evento__" in g.jogador.eventos, "evento do nó registrado")
    checa("taverna:1" in g.jogador.eventos, "evento único registrado")
    g.no_atual = "taverna"
    checa(not g._escolha_visivel(selene, "taverna:1"), "escolha some na revisita (sem farm)")
    checa(not g._escolha_visivel(H.get("taverna")["escolhas"][0], "taverna:0"),
          "ramo alternativo do mesmo evento bloqueado")
    checa(not g._escolha_visivel(H.get("taverna")["escolhas"][2], "taverna:2"),
          "outra recompensa do mesmo evento bloqueada")
    checa(g._escolha_visivel(H.get("taverna")["escolhas"][3], "taverna:3"), "saída continua repetível")
    # Nó esgotado injeta saída segura.
    g.no_atual = "taverna_rumor"
    g.processar_escolha(H.get("taverna_rumor")["escolhas"][0], "taverna_rumor:0")
    g.no_atual = "taverna_rumor"
    g._render_escolhas_no()
    labels = [b.label for b in g.painel.todos_botoes()]
    checa(any("Seguir em frente" in s for s in labels), "nó esgotado oferece saída (anti-soft-lock)")
    # Grind (explorar) permanece repetível.
    g.jogador.eventos.append("explorar:0")
    checa(g._escolha_visivel(H.get("explorar")["escolhas"][0], "explorar:0"), "grind 'explorar' permanece repetível")


def teste_render():
    print("== Render headless de todas as telas ==")
    from game.app import Game
    g = Game()
    ok = True
    try:
        for _ in range(3):
            g._update(1 / 60); g._draw()
        g.jogador = core.Personagem("R", "Outro", "Mago", "Normal")
        g.ir_para_no("entrada_caverna")
        g.destino_pos_combate = "pre_chefe"
        g.iniciar_combate({"chefe": True})
        for _ in range(5):
            g._update(1 / 60); g._draw()
        g.tela_inventario(); g._update(1 / 60); g._draw()
        g._cenario_pre_mapa = "vila"; g.tela_mapa(); g._update(1 / 60); g._draw()
        for chave in g.historia.nos:  # render de cada cenário
            g.no_atual = chave; g.modo = "narrativa"; g.cenario = g.cenario_do_no(chave)
            g._update(1 / 60); g._draw()
    except Exception:
        import traceback; traceback.print_exc()
        ok = False
    checa(ok, "todas as telas renderizam sem exceção (inclui chefe/dragão)")


def teste_playthroughs(n=30):
    print(f"== {n} playthroughs aleatórios até um final ==")
    from game.app import Game
    random.seed(123)
    finais = 0
    max_ev = 0
    for _ in range(n):
        g = Game(); g.jogador = core.Personagem("H", "Outro", random.choice(list(core.CLASSES)), "Fácil")
        g.ir_para_no("inicio")
        for _ in range(500):
            no = g.historia.get(g.no_atual) or {}
            if no.get("final"):
                break
            if g.modo == "combate" and g.combate and not g.combate.terminado:
                atks = core.ATAQUES[g.jogador.classe]
                a = random.choice([x for x in atks if g.jogador.recurso >= x["custo"]] or [atks[0]])
                g.combate.jogador_ataca(a); continue
            escolhas = [(i, e) for i, e in enumerate(no.get("escolhas", []))
                        if g._escolha_visivel(e, f"{g.no_atual}:{i}")]
            if not escolhas:
                g.ir_para_no(g._fallback_destino(no)); continue
            i, e = random.choice(escolhas)
            g.processar_escolha(e, f"{g.no_atual}:{i}")
        if (g.historia.get(g.no_atual) or {}).get("final"):
            finais += 1
        max_ev = max(max_ev, len(g.jogador.eventos))
    checa(finais >= int(n * 0.9), f"{finais}/{n} chegaram a um final")
    checa(max_ev <= 40, f"eventos únicos por jogo limitados (máx {max_ev} <= 40 — sem farm infinito)")


def main():
    pygame.init()
    pygame.display.set_mode((640, 480))
    teste_grafo()
    teste_progressao()
    teste_render()
    teste_playthroughs()
    pygame.quit()
    print("\n" + "=" * 56)
    if FALHAS:
        print(f"❌ {len(FALHAS)} falha(s):")
        for f in FALHAS:
            print("   -", f)
        sys.exit(1)
    print("✅ Todas as checagens passaram.")


if __name__ == "__main__":
    main()
