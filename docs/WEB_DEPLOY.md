# Versão web de Crônicas de Pedravale

Esta pasta contém a aplicação estática pronta para GitHub Pages.

## Rodar localmente

```bash
python3 -m http.server 4173 --directory docs
```

Depois abra:

```text
http://localhost:4173/
```

## Publicar no GitHub Pages com GitHub Actions

Este repositório já inclui o workflow `.github/workflows/pages.yml`, que publica
automaticamente o conteúdo de `docs/`.

No repositório do GitHub:

1. Entre em **Settings > Pages**.
2. Em **Source**, escolha **GitHub Actions**.
3. Faça commit e push para a branch `main`.
4. Acesse a aba **Actions** e aguarde o workflow **Deploy GitHub Pages** concluir.

O GitHub Pages servirá `docs/index.html`.

## Publicar usando branch `/docs`

Se preferir não usar GitHub Actions, também funciona pelo modo clássico.

No repositório do GitHub:

1. Entre em **Settings > Pages**.
2. Em **Source**, escolha **Deploy from a branch**.
3. Em **Branch**, escolha `main`.
4. Em **Folder**, escolha `/docs`.
5. Salve.

O GitHub Pages servirá `docs/index.html`.

## Como a versão web está organizada

- `index.html`: shell da aplicação.
- `web/app.js`: regras, UI, combate, inventário, atributos, mapa e save.
- `web/story.json`: história exportada da versão Python.
- `web/styles.css`: layout responsivo.
- `assets/`: imagens necessárias no GitHub Pages.

O progresso do jogador é salvo no `localStorage` do navegador.
