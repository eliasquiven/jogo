# Crônicas de Pedravale — Versão Pygame (gráfica)

Reescrita da camada visual do RPG em **Pygame**, com **sprites pixel-art**
(assets Kenney CC0 + pixel-art próprio) e **animações turbinadas** (brasas,
neve, vagalumes com brilho, névoa, gotas, lava pulsante, poeira mágica), bem
acima das animações do original em Tkinter.

A **lógica do jogo é a mesma** do original: a árvore narrativa de ~120 escolhas,
karma, combate por turnos, inventário, captura de aliados, 4 finais — tudo
reaproveitado de `core.py` (cópia fiel, sem Tkinter).

## Como rodar

Requer **Python 3.8+** e **pygame**:

```bash
# usando o venv do projeto (já tem pygame instalado):
./jogar_pygame.sh

# ou manualmente:
pip install pygame
python main.py
```

> Diferente da versão Tkinter, esta **não** precisa de `python3-tk` — só do pygame.

## Estrutura

```
pygame_version/
├── main.py              # ponto de entrada
├── core.py              # lógica pura (Item, Personagem, Inimigo, Combate, Historia)
├── assets/              # sprites Kenney CC0 + atribuição
└── game/
    ├── theme.py         # paleta, fontes, helpers
    ├── assets.py        # carregador de sprites (Kenney + pixel-art próprio)
    ├── backgrounds.py   # 14 cenários
    ├── particles.py     # motor de partículas de ambiente
    ├── ui.py            # botões, painel rolável, barras, modal, console
    └── app.py           # controlador, loop e todas as telas
```

## Controles

- **Mouse**: clicar nos botões; roda do mouse rola listas longas (inventário).
- **Teclado em combate**: `1` Atacar · `2` Defender · `3` Item · `4` Capturar · `5` Fugir.
- Na criação de personagem, digite o nome e tecle **Enter**.

Assets: ver `assets/ATTRIBUTION.md` (Kenney, CC0).
