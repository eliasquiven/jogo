# 🐉 Guia do Jogador — Crônicas de Pedravale

Bem-vindo(a)! Este guia é para **qualquer pessoa**, mesmo quem nunca mexeu com
programação. Em poucos minutos você estará jogando.

*Crônicas de Pedravale* é um RPG de aventura medieval em que **você decide a
história**: cada escolha muda o rumo, o seu **Karma** (herói ou vilão) e até o
**final** que você vai ver. Tem combates por turnos, monstros para capturar,
itens para equipar e segredos para descobrir.

---

## ▶️ Como começar a jogar (passo a passo)

O jogo precisa de **Python 3.9+** e da biblioteca **pygame**. São 3 passinhos.

### 1. Instale o Python
- **Windows / macOS:** baixe em [python.org/downloads](https://www.python.org/downloads/)
  e instale. No Windows, **marque "Add Python to PATH"** durante a instalação.
- **Linux (Ubuntu/Debian):** `sudo apt install python3 python3-pip`

### 2. Instale o pygame
Abra um **Terminal** (no Windows, o *Prompt de Comando*) e digite:

```bash
pip install pygame
```

(Se der erro de "pip não encontrado", tente `python -m pip install pygame`;
no Linux/macOS pode ser `python3 -m pip install pygame`.)

### 3. Abra o jogo
Ainda no terminal, entre na pasta do jogo e rode:

```bash
cd pygame_version
python main.py
```

No **Linux/macOS** dá para usar o atalho `./jogar_pygame.sh` (dois cliques,
ou `./jogar_pygame.sh` no terminal).

Pronto, divirta-se! 🎉

---

## 🎮 Como se joga

O jogo acontece em **uma única janela**, dividida em três partes:

```
┌───────────────────────────────────────────────┐
│  Barra de status: nome, classe, HP, Karma...   │  ← seus números
├───────────────────────────────────────────────┤
│                                                │
│        PALCO (cenário desenhado + texto)       │  ← a cena e a história
│                                                │
├───────────────────────────────────────────────┤
│   [ Botões de escolha / ações de combate ]     │  ← o que você clica
└───────────────────────────────────────────────┘
```

- **Fora de combate:** clique nos **botões de escolha** para seguir a história.
  Há ainda os botões **Inventário**, **Mapa**, **Salvar** e **Sair**.
- **Em combate:** use os botões ou os **atalhos do teclado**:

  | Tecla | Ação |
  |:----:|------|
  | **1** | Atacar |
  | **2** | Defender (reduz o dano e recupera um pouco de recurso) |
  | **3** | Usar Item (poções) |
  | **4** | Capturar (recrutar o monstro enfraquecido) |
  | **5** | Fugir (não funciona contra chefes) |

---

## 🛡️ Escolha sua classe

No começo você cria seu personagem (nome, gênero, classe e dificuldade):

| Classe | Estilo | Resumo |
|--------|--------|--------|
| ⚔️ **Cavaleiro** | Tanque | Muito HP e defesa. Aguenta porrada e usa **Vigor**. |
| 🔮 **Mago** | Dano mágico | Frágil, mas com dano altíssimo e cura. Usa **MP**. |
| 🏹 **Arqueiro** | Ágil | Dano à distância, ótimo crítico e esquiva. Usa **Energia**. |

> **Dica para iniciantes:** o **Cavaleiro** é o mais perdoador. O **Mago** é o
> mais poderoso, mas exige cuidado para não morrer.

---

## 💡 Dicas rápidas

- **Salve sempre** antes de uma batalha difícil (botão **Salvar**).
- **Capturar** monstros (ação **4**) funciona melhor quando o inimigo está com
  **pouca vida**. Use a **Esfera de Selamento** para aumentar a chance. Aliados
  capturados lutam ao seu lado — mas podem cair em combate!
- **Equipe o melhor item:** abra o **Inventário** e equipe armas/armaduras.
  Itens **Lendários** são raros e fortes.
- Seu **Karma** muda conforme suas escolhas: ações nobres sobem (Herói), ações
  cruéis descem (Vilão). Algumas escolhas e **finais só aparecem** se o seu
  Karma for bem alto ou bem baixo.
- Explore! Vagar pelos arredores rende batalhas, XP e tesouros antes de seguir.

---

## ✨ Segredo: os Fragmentos da Aurora

Espalhados pelo mundo há **três Fragmentos da Aurora** (no pântano, nas
montanhas e no saber de um feiticeiro). Quem reunir os três desbloqueia um
**final secreto** — o melhor de todos. Fique atento aos lugares que você visita
e às pistas no caminho. 😉

---

## 🆘 Resolvendo problemas

| Problema | Solução |
|----------|---------|
| **"No module named 'pygame'"** | O pygame não está instalado nesse Python. Rode `pip install pygame` (ou `python -m pip install pygame`). |
| **"python não é reconhecido"** (Windows) | Reinstale o Python marcando **"Add Python to PATH"**, ou use `py main.py` no lugar de `python main.py`. |
| `./jogar_pygame.sh` abre um editor de texto | Abra um Terminal na pasta e rode `chmod +x jogar_pygame.sh` e depois `./jogar_pygame.sh`. |
| `pip install` falha por "externally managed" (Linux) | Use um ambiente isolado: `python3 -m venv .venv && source .venv/bin/activate && pip install pygame`. |
| A janela abre muito pequena/grande | Arraste a borda da janela para redimensionar; a cena se ajusta sozinha. |

---

## 🧩 Para quem quer ir além

- **Código do jogo:** fica em `pygame_version/` — lógica em `core.py`, apresentação
  em `game/` (Pygame). Rode com `python main.py` dentro de `pygame_version/`.
- **Ambiente isolado (recomendado):** `python -m venv .venv` e `pip install pygame`.
- **Testes:** `python pygame_version/test_jogo.py` (roda headless, sem abrir janela).
- Os sprites usam arte **pixel-art** (packs Kenney CC0 + arte dedicada); as
  animações de ambiente são geradas em tempo real.

Boa jornada, herói! 🗡️🐲
