# -*- coding: utf-8 -*-
"""Crônicas de Pedravale — versão Pygame (gráfica, com assets Kenney CC0).

Executar:  python main.py   (com pygame instalado)
"""

import os
import sys

# garante que o pacote `game` e `core` sejam encontrados
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.app import Game


def main():
    Game().run()


if __name__ == "__main__":
    main()
