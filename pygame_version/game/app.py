# -*- coding: utf-8 -*-
"""app.py — controlador e loop principal (Pygame).

Espelha o GerenciadorJogo do original em Tkinter: máquina de estados de telas
(título, criação, narrativa, combate, mapa, inventário, atributos) e fornece à
classe core.Combate os métodos esperados via `self.gj`: log, render_combate,
fim_combate, dropar_loot.
"""

import os
import sys
import json
import math
import random

import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core
from . import theme, ui, backgrounds, particles
from .assets import Assets, altura_inimigo

LARG_INI, ALT_INI = 980, 740
LARG_MIN, ALT_MIN = 760, 600
STATUS_H = 50
# Em monitores largos, a UI fica numa coluna centralizada desta largura máx.
# (evita cenas esticadas em faixas e bordas com proporção estranha).
CONTENT_MAX_W = 1400
# Razão máxima largura/altura da cena — acima disso, a arte é centralizada
# em vez de virar uma faixa fina e larga.
CENA_AR_MAX = 1.9
SAVE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "save_pedravale.json")

CENARIO_NO = {
    "inicio": "vila", "exigir_ouro": "vila", "apos_goblin": "vila",
    "vila_hub": "vila", "taverna": "taverna", "taverna_rumor": "taverna",
    "forja": "forja", "templo": "trono",
    "encruzilhada": "campo", "explorar": "campo",
    "floresta": "floresta", "floresta_liberta": "floresta",
    "floresta_profunda": "floresta", "bruxa": "floresta",
    "fonte_feerica": "floresta", "fonte_bencao": "floresta",
    "pantano": "pantano", "altar_afogado": "pantano", "pantano_fundo": "pantano",
    "montanha": "montanha", "cavaleiro_caido": "montanha", "desfiladeiro": "montanha",
    "reino": "trono", "arena": "reino", "arena_vitoria": "reino",
    "feiticeiro_aliado": "trono", "feiticeiro_ameaca": "trono",
    "entrada_caverna": "caverna", "furtividade": "caverna",
    "lago_subterraneo": "lago", "reliquia_sussurra": "lago",
    "pre_chefe": "caverna", "pre_chefe2": "covil", "decisao_final": "covil",
    "final_heroi": "amanhecer", "final_vilao": "covil",
    "final_neutro": "campo", "final_guardiao": "amanhecer",
}

REGIOES_MAPA = [("Pedravale", 0.16, 0.32, ("vila",)),
                ("Floresta", 0.40, 0.64, ("floresta",)),
                ("Aldoria", 0.64, 0.30, ("reino", "trono")),
                ("Cavernas", 0.86, 0.62, ("caverna", "covil", "lago"))]


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Crônicas de Pedravale — RPG de Aventura")
        self.screen = pygame.display.set_mode((LARG_INI, ALT_INI), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.rodando = True

        self.assets = Assets()
        self.particles = particles.ParticleSystem()

        self.jogador = None
        self.combate = None
        self.historia = core.Historia()
        self.no_atual = None
        self.destino_pos_combate = None

        self.modo = "titulo"
        self.cenario = "campo"
        self.log_buffer = []
        self.painel = ui.PainelInferior()
        self.modal = None
        self.text_input = None
        self._on_enter_nome = None
        self._attr_callback = None

        # criação
        self._novo_nome = None
        self._novo_genero = None
        self._nova_classe = None

        # animação / efeitos
        self.fx = []
        self._prev_hp = {}
        self._cfg_part = None
        self.t = 0.0
        self.title_dragon_x = -120

        self.tela_titulo()

    # ================= utilidades de tela =================
    def _rects(self):
        W, H = self.screen.get_size()
        # coluna de conteúdo centralizada (limita a largura em telas largas)
        cw = min(W, CONTENT_MAX_W)
        cx = (W - cw) // 2
        # painel cresce com o conteúdo (sem espaço morto sob os botões)
        cont_h = self.painel.altura_conteudo(cw) + 12
        panel_h = max(120, min(int(H * 0.45), cont_h))
        stage = pygame.Rect(cx + 8, STATUS_H + 4, cw - 16, H - STATUS_H - panel_h - 12)
        panel = pygame.Rect(cx, H - panel_h, cw, panel_h)
        return W, H, stage, panel

    def _frac_console(self):
        return {"mapa": 0.30, "combate": 0.30}.get(self.modo, 0.50)

    def _cena_console_rects(self, stage):
        if self.modo in ("combate", "mapa"):
            # fração fixa: a arena/mapa precisa de área previsível
            cena_h = int(stage.h * (1 - self._frac_console()))
        else:
            # título/narrativa/menu: o console cede à cena o que o texto não usa
            medido = ui.medir_console(stage.w, self.log_buffer)
            console_h = max(72, min(int(stage.h * 0.5), medido))
            cena_h = stage.h - console_h
        cena = pygame.Rect(stage.x, stage.y, stage.w, cena_h)
        console = pygame.Rect(stage.x, stage.y + cena_h, stage.w, stage.h - cena_h)
        # evita cena em faixa larga: centraliza a arte se exceder a proporção
        if self.modo != "combate" and cena.h > 0 and cena.w > cena.h * CENA_AR_MAX:
            nova_w = int(cena.h * CENA_AR_MAX)
            cena.x += (cena.w - nova_w) // 2
            cena.w = nova_w
        return cena, console

    def log(self, texto="", tag="narrativa"):
        self.log_buffer.append((texto, tag))
        if len(self.log_buffer) > 60:
            self.log_buffer = self.log_buffer[-60:]

    def limpar_log(self):
        self.log_buffer = []

    def cenario_do_no(self, chave):
        return CENARIO_NO.get(chave, "campo")

    def _botao(self, label, cb, cor=None, icone=None):
        return ui.Button(label, cb, cor=cor, icone=icone)

    # ================= TELA DE TÍTULO =================
    def tela_titulo(self):
        self.combate = None
        self.jogador = None
        self.modo = "titulo"
        self.cenario = "campo"
        self.text_input = None
        self.limpar_log()
        self.painel.limpar()
        self.log("Um RPG de aventura por escolhas, em um reino medieval ameaçado.\n", "narrativa")
        self.log("Suas decisões moldam a história, seus aliados e o destino da terra.", "sistema")
        self.log("Cada escolha soma Karma de Herói (+) ou Vilão (-), levando a finais distintos.\n", "sistema")
        self.painel.add_botoes([self._botao("Novo Jogo", self.criacao_nome)])
        if os.path.exists(SAVE_FILE):
            self.painel.add_botoes([self._botao("Carregar Jogo", self.carregar_jogo)])
        self.painel.add_botoes([self._botao("Sair", self.pedir_sair)])

    # ================= CRIAÇÃO =================
    def criacao_nome(self):
        self.modo = "menu"
        self.cenario = "reino"
        self.limpar_log()
        self.log("CRIAÇÃO DE PERSONAGEM — Nome", "titulo")
        self.log("Digite o nome do seu herói e tecle Enter (ou clique Confirmar).\n", "narrativa")
        self.text_input = ui.TextInput(self._novo_nome or "")
        self._on_enter_nome = self._confirmar_nome
        self.painel.limpar()
        self.painel.add_input(self.text_input)
        self.painel.add_botoes([self._botao("Confirmar nome", self._confirmar_nome)])
        self.painel.add_botoes([self._botao("<- Voltar", self.tela_titulo, cor=(51, 48, 42))])

    def _confirmar_nome(self):
        nome = (self.text_input.texto if self.text_input else "").strip()
        if not nome:
            self._modal("O nome não pode ficar vazio.", [("Ok", self._fechar_modal)])
            return
        self._novo_nome = nome[:20]
        self.text_input = None
        self.criacao_genero()

    def criacao_genero(self):
        self.text_input = None
        self.log(f"\nNome escolhido: {self._novo_nome}", "sistema")
        self.log("CRIAÇÃO DE PERSONAGEM — Gênero", "titulo")
        self.painel.limpar()
        for g in ("Masculino", "Feminino", "Outro"):
            self.painel.add_botoes([self._botao(g, lambda gen=g: self._set_genero(gen))])
        self.painel.add_botoes([self._botao("<- Voltar", self.criacao_nome, cor=(51, 48, 42))])

    def _set_genero(self, genero):
        self._novo_genero = genero
        self.criacao_classe()

    def criacao_classe(self):
        self.log(f"Gênero: {self._novo_genero}\n", "sistema")
        self.log("CRIAÇÃO DE PERSONAGEM — Classe", "titulo")
        for nome_classe, dados in core.CLASSES.items():
            self.log(f"- {nome_classe}: {dados['descricao']}", "narrativa")
            self.log(f"   HP {dados['hp']} | {dados['nome_recurso']} {dados['recurso']} | "
                     f"Dano {dados['dano']} | Defesa {dados['defesa']}", "sistema")
        self.painel.limpar()
        for nome_classe in core.CLASSES:
            self.painel.add_botoes([self._botao(f"Escolher {nome_classe}",
                                                lambda c=nome_classe: self._set_classe(c))])

    def _set_classe(self, classe):
        self._nova_classe = classe
        self.criacao_dificuldade()

    def criacao_dificuldade(self):
        self.log(f"Classe: {self._nova_classe}\n", "sistema")
        self.log("CRIAÇÃO DE PERSONAGEM — Dificuldade", "titulo")
        for nome_dif, dados in core.DIFICULDADES.items():
            self.log(f"- {nome_dif}: {dados['desc']}", "narrativa")
        self.painel.limpar()
        for nome_dif in core.DIFICULDADES:
            self.painel.add_botoes([self._botao(f"Jogar em {nome_dif}",
                                                lambda d=nome_dif: self._finalizar_criacao(d))])

    def _finalizar_criacao(self, dificuldade):
        try:
            self.jogador = core.Personagem(self._novo_nome, self._novo_genero,
                                           self._nova_classe, dificuldade)
        except Exception as e:
            self._modal(f"Não foi possível criar o personagem: {e}", [("Ok", self._fechar_modal)])
            return
        self.limpar_log()
        self.log(f"Bem-vindo(a), {self.jogador.nome}, o(a) {self.jogador.classe}!", "titulo")
        self.log(f"Dificuldade: {dificuldade}. Sua jornada começa agora...\n", "sistema")
        self.ir_para_no("inicio")

    # ================= NAVEGAÇÃO =================
    def ir_para_no(self, chave):
        no = self.historia.get(chave)
        if not no:
            self.modo = "menu"
            self.painel.limpar()
            self.log(f"\n[Aviso: trecho '{chave}' não encontrado. Retornando com segurança.]", "sistema")
            self.painel.add_botoes([self._botao("Tela inicial", self.tela_titulo)])
            return
        self.no_atual = chave
        self.combate = None
        self.modo = "narrativa"
        self.cenario = self.cenario_do_no(chave)
        self.log("\n" + ("-" * 56), "sistema")
        self.log(no["texto"], "narrativa")
        if no.get("final"):
            self.painel.limpar()
            self.painel.add_botoes([self._botao("Jogar novamente", self.tela_titulo)])
            if os.path.exists(SAVE_FILE):
                try:
                    os.remove(SAVE_FILE)
                except OSError:
                    pass
            return
        self._render_escolhas_no()

    def _render_escolhas_no(self):
        no = self.historia.get(self.no_atual)
        if not no:
            return
        self.modo = "narrativa"
        self.cenario = self.cenario_do_no(self.no_atual)
        self.painel.limpar()
        visiveis = 0
        for idx, escolha in enumerate(no.get("escolhas", [])):
            eid = f"{self.no_atual}:{idx}"
            if not self._escolha_visivel(escolha, eid):
                continue
            self.painel.add_botoes([self._botao(escolha["label"],
                                                lambda e=escolha, _id=eid: self.processar_escolha(e, _id))])
            visiveis += 1
        if visiveis == 0:
            destino = self._fallback_destino(no)
            self.painel.add_botoes([self._botao("Seguir em frente",
                                                lambda d=destino: self.ir_para_no(d))])
        cinza = (51, 48, 42)
        self.painel.add_botoes([
            self._botao("Inventário", self.tela_inventario, cor=cinza),
            self._botao("Mapa", self.tela_mapa, cor=cinza),
            self._botao("Salvar", self.salvar_jogo, cor=cinza),
            self._botao("Sair", self.menu_sair, cor=cinza),
        ])

    @staticmethod
    def _evento_unico(escolha):
        """Escolha com efeito duradouro que só pode ocorrer uma vez."""
        if escolha.get("repetivel"):
            return False
        return bool(escolha.get("loot") or escolha.get("pocao") or escolha.get("aliado")
                    or escolha.get("set_flag") or "karma" in escolha or escolha.get("combate"))

    @staticmethod
    def _evento_grupo_id(no_chave):
        return f"{no_chave}:__evento__"

    def _evento_no_concluido(self, no_chave):
        gid = self._evento_grupo_id(no_chave)
        prefixo = f"{no_chave}:"
        return gid in self.jogador.eventos or any(e.startswith(prefixo) for e in self.jogador.eventos)

    def _saida_segura(self, escolha):
        if self._evento_unico(escolha):
            return False
        label = escolha.get("label", "").lower()
        return any(p in label for p in ("sair", "voltar", "recuar", "seguir em frente"))

    def _no_tem_evento(self, no):
        return any(self._evento_unico(e) for e in no.get("escolhas", []))

    def _escolha_de_evento(self, no, escolha):
        if self._evento_unico(escolha):
            return True
        return self._no_tem_evento(no) and not self._saida_segura(escolha)

    def _fallback_destino(self, no):
        """Destino seguro quando um nó fica sem escolhas visíveis (evita travar)."""
        for e in no.get("escolhas", []):
            if e.get("destino") and not e.get("combate"):
                return e["destino"]
        if no.get("escolhas"):
            return no["escolhas"][0].get("destino") or "vila_hub"
        return "vila_hub"

    def _escolha_visivel(self, escolha, evento_id=None):
        no_chave = self.no_atual
        if evento_id:
            no_chave = evento_id.rsplit(":", 1)[0]
        no = self.historia.get(no_chave) if no_chave else None
        if no and self._evento_no_concluido(no_chave) and self._escolha_de_evento(no, escolha):
            return False
        if evento_id and self._evento_unico(escolha) and evento_id in self.jogador.eventos:
            return False
        req = escolha.get("requer_karma")
        if req:
            op, val = req
            k = self.jogador.karma
            if op == ">=" and not (k >= val):
                return False
            if op == "<=" and not (k <= val):
                return False
        req_f = escolha.get("requer_flag")
        if req_f:
            necessarias = [req_f] if isinstance(req_f, str) else list(req_f)
            if not all(f in self.jogador.flags for f in necessarias):
                return False
        return True

    def processar_escolha(self, escolha, evento_id=None):
        # Registra o evento do nó para bloquear alternativas na revisita.
        no = self.historia.get(self.no_atual) if self.no_atual else None
        if evento_id and no and self._escolha_de_evento(no, escolha):
            gid = self._evento_grupo_id(self.no_atual)
            if gid not in self.jogador.eventos:
                self.jogador.eventos.append(gid)
            if self._evento_unico(escolha) and evento_id not in self.jogador.eventos:
                self.jogador.eventos.append(evento_id)
        if escolha.get("karma"):
            self.jogador.karma += escolha["karma"]
            sinal = "+" if escolha["karma"] > 0 else ""
            tag = "heroi" if escolha["karma"] > 0 else "vilao"
            self.log(f"  * Karma {sinal}{escolha['karma']} (total: {self.jogador.karma}).", tag)
        if escolha.get("loot"):
            tipo = escolha["loot"]
            if tipo == "arma":
                self.conceder_item(core.gerar_arma(self.jogador.nivel, self.jogador.classe))
            elif tipo == "armadura":
                self.conceder_item(core.gerar_armadura(self.jogador.nivel))
            else:
                self.conceder_item(random.choice([
                    core.gerar_arma(self.jogador.nivel, self.jogador.classe),
                    core.gerar_armadura(self.jogador.nivel)]))
        if escolha.get("pocao"):
            self.conceder_item(core.gerar_consumivel(escolha["pocao"]))
        if escolha.get("aliado"):
            self.jogador.aliados.append({"nome": escolha["aliado"], "dano": 8, "hp": 40, "hp_max": 40})
            self.log(f"  > {escolha['aliado']} juntou-se a você!", "heroi")
        if escolha.get("set_flag"):
            fl = escolha["set_flag"]
            if fl not in self.jogador.flags:
                self.jogador.flags.append(fl)
                self.log("  * Você sente que algo importante mudou em sua jornada.", "titulo")
        if escolha.get("combate"):
            self.destino_pos_combate = escolha["destino"]
            self.iniciar_combate(escolha["combate"])
        else:
            self.ir_para_no(escolha["destino"])

    def conceder_item(self, item):
        self.log(f"  + Você obteve: {item.nome_completo}", "cura")
        if item.tipo == "arma":
            atual = self.jogador.arma.valor if self.jogador.arma else 0
            if item.valor > atual:
                self.jogador.equipar(item)
                self.log("     -> Equipado automaticamente (melhor que o anterior).", "sistema")
            else:
                self.jogador.inventario.append(item)
        elif item.tipo == "armadura":
            atual = self.jogador.armadura.valor if self.jogador.armadura else 0
            if item.valor > atual:
                self.jogador.equipar(item)
                self.log("     -> Equipada automaticamente (melhor que a anterior).", "sistema")
            else:
                self.jogador.inventario.append(item)
        else:
            self.jogador.inventario.append(item)

    def dropar_loot(self, inimigo):
        bonus = core.DROP_BONUS_CHEFE if inimigo.chefe else 0
        chance_equip = core.DROP_EQUIP_CHANCE_CHEFE if inimigo.chefe else core.DROP_EQUIP_CHANCE_NORMAL
        if random.random() < chance_equip:
            if random.choice(["arma", "armadura"]) == "arma":
                self.conceder_item(core.gerar_arma(self.jogador.nivel, self.jogador.classe, bonus_lendario=bonus))
            else:
                self.conceder_item(core.gerar_armadura(self.jogador.nivel, bonus_lendario=bonus))
        if random.random() < core.DROP_CONSUMIVEL_CHANCE:
            self.conceder_item(core.gerar_consumivel(random.choice(["cura", "recurso", "antidoto"])))

    # ================= MAPA =================
    def tela_mapa(self):
        if not self.jogador:
            return
        self._cenario_pre_mapa = self.cenario
        self.modo = "mapa"
        self.painel.limpar()
        self.log("Mapa de Pedravale e arredores.", "sistema")
        self.painel.add_botoes([self._botao("<- Voltar", self._render_escolhas_no, cor=(51, 48, 42))])

    # ================= INVENTÁRIO =================
    def tela_inventario(self):
        if not self.jogador or self.combate:
            return
        self.modo = "menu"
        self.cenario = self.cenario_do_no(self.no_atual) if self.no_atual else "reino"
        p = self.jogador
        self.painel.limpar()
        arma = p.arma.nome_completo if p.arma else "(nenhuma)"
        armadura = p.armadura.nome_completo if p.armadura else "(nenhuma)"
        self.painel.add_label(f"Equipado — Arma: {arma}  |  Armadura: {armadura}", theme.TEXTO)
        self.painel.add_label(f"Dano {p.dano_total} · Defesa {p.defesa_total} · "
                              f"HP {p.hp}/{p.hp_max} · {p.nome_recurso} {p.recurso}/{p.recurso_max}",
                              (154, 160, 166))
        equipaveis = [i for i in p.inventario if i.tipo in ("arma", "armadura")]
        consumiveis = [i for i in p.inventario if i.tipo == "consumivel"]
        especiais = [i for i in p.inventario if i.tipo == "captura"]
        if equipaveis:
            self.painel.add_label("— Equipamentos —", theme.OURO)
            for item in equipaveis:
                self.painel.add_botoes([self._botao(f"Equipar {item.nome_completo}",
                                                    lambda it=item: self._equipar_inv(it))])
        if consumiveis:
            self.painel.add_label("— Consumíveis (usar agora) —", theme.OURO)
            for item in consumiveis:
                self.painel.add_botoes([self._botao(f"Usar {item.nome} — {item.descricao}",
                                                    lambda it=item: self._usar_item_fora(it))])
        if especiais:
            self.painel.add_label(f"— Esferas de Selamento: {len(especiais)} —", theme.OURO)
        if not (equipaveis or consumiveis or especiais):
            self.painel.add_label("(inventário vazio)", (154, 160, 166))
        self.painel.add_botoes([self._botao("<- Voltar", self._render_escolhas_no, cor=(51, 48, 42))])

    def _equipar_inv(self, item):
        self.jogador.equipar(item)
        self.log(f"  + Equipado: {item.nome_completo}", "sistema")
        self.tela_inventario()

    def _usar_item_fora(self, item):
        if item not in self.jogador.inventario:
            return
        if not core.item_tera_efeito(self.jogador, item):
            self._modal(f"{item.nome} não teria efeito agora.", [("Ok", self._fechar_modal)])
            return
        ef = item.efeito
        if ef.get("antidoto"):
            self.jogador.veneno = 0
            self.log(f"  + {item.nome}: veneno neutralizado.", "cura")
        if "cura" in ef:
            curado = self.jogador.curar(ef["cura"])
            if curado:
                self.log(f"  + {item.nome}: +{curado} de HP.", "cura")
        if "recurso" in ef:
            self.jogador.restaurar_recurso(ef["recurso"])
            self.log(f"  + {item.nome}: +{ef['recurso']} de {self.jogador.nome_recurso}.", "cura")
        self.jogador.inventario.remove(item)
        self.tela_inventario()

    # ================= COMBATE =================
    def iniciar_combate(self, spec):
        dif = self.jogador.dif_mult
        if spec.get("chefe"):
            inimigo = core.gerar_inimigo(self.jogador.nivel, chefe=True, dif_mult=dif)
        elif spec.get("aleatorio"):
            inimigo = core.gerar_inimigo(self.jogador.nivel, dif_mult=dif)
        else:
            inimigo = core.gerar_inimigo(self.jogador.nivel, tipo=spec.get("tipo"), dif_mult=dif)
        self.combate = core.Combate(self, self.jogador, inimigo)
        self.modo = "combate"
        self.cenario = self.cenario_do_no(self.no_atual)
        self._prev_hp = {"ini": inimigo.hp, "heroi": self.jogador.hp}
        self.fx = []
        self.log("\n" + ("=" * 56), "sistema")
        self.log(f"> COMBATE! {inimigo.nome} (Nv.{inimigo.nivel}) aparece!", "titulo")
        self.log(f"   HP {inimigo.hp} | Dano {inimigo.dano} | Defesa {inimigo.defesa}", "sistema")
        self.render_combate(self.combate)

    def render_combate(self, combate):
        self.combate = combate
        self.modo = "combate"
        self._spawn_fx_combate()
        ini = combate.inimigo
        self.painel.limpar()
        linha1 = [self._botao("Atacar (1)", self.menu_ataques),
                  self._botao("Defender (2)", self._acao_defender),
                  self._botao("Usar Item (3)", self.menu_itens)]
        self.painel.add_botoes(linha1)
        if not ini.chefe:
            self.painel.add_botoes([self._botao("Capturar (4)", self.menu_captura),
                                    self._botao("Fugir (5)", self._acao_fugir)])

    def _acao_defender(self):
        if self.combate and not self.combate.terminado:
            self.combate.jogador_defende()

    def _acao_fugir(self):
        if self.combate and not self.combate.terminado:
            self.combate.jogador_foge()

    def menu_ataques(self):
        if not self.combate or self.combate.terminado:
            return
        self.painel.limpar()
        self.painel.add_label("Escolha um ataque:", theme.TEXTO)
        for atk in core.ATAQUES[self.jogador.classe]:
            custo = atk["custo"]
            custo_txt = "sem custo" if custo == 0 else f"{custo} {self.jogador.nome_recurso}"
            self.painel.add_botoes([self._botao(f"{atk['nome']} ({custo_txt}) — {atk['desc']}",
                                                lambda a=atk: self._fazer_ataque(a))])
        self.painel.add_botoes([self._botao("<- Voltar", lambda: self.render_combate(self.combate), cor=(51, 48, 42))])

    def _fazer_ataque(self, atk):
        if self.combate and not self.combate.terminado:
            self.combate.jogador_ataca(atk)

    def menu_itens(self):
        if not self.combate or self.combate.terminado:
            return
        self.painel.limpar()
        consumiveis = [i for i in self.jogador.inventario if i.tipo == "consumivel"]
        self.painel.add_label("Inventário (consumíveis):", theme.TEXTO)
        if not consumiveis:
            self.painel.add_label("(nenhum item utilizável)", (154, 160, 166))
        for item in consumiveis:
            self.painel.add_botoes([self._botao(f"{item.nome} — {item.descricao}",
                                                lambda it=item: self._usar_item_combate(it))])
        self.painel.add_botoes([self._botao("<- Voltar", lambda: self.render_combate(self.combate), cor=(51, 48, 42))])

    def _usar_item_combate(self, item):
        if self.combate and not self.combate.terminado:
            self.combate.jogador_usa_item(item)

    def menu_captura(self):
        if not self.combate or self.combate.terminado:
            return
        ini = self.combate.inimigo
        if ini.chefe:
            self.log("  x Criaturas tão poderosas não podem ser capturadas!", "sistema")
            return
        self.painel.limpar()
        chance = self.combate.chance_captura(False)
        chance_esfera = self.combate.chance_captura(True)
        self.painel.add_label(f"Capturar {ini.nome}? Chance: {int(chance*100)}% "
                              f"(quanto menor o HP do alvo, maior a chance)", theme.TEXTO)
        self.painel.add_botoes([self._botao(f"Tentar capturar — mãos livres ({int(chance*100)}%)",
                                            lambda: self._capturar(False))])
        if any(i.efeito.get("captura") for i in self.jogador.inventario):
            self.painel.add_botoes([self._botao(f"Usar Esfera de Selamento ({int(chance_esfera*100)}%)",
                                                self._capturar_esfera)])
        self.painel.add_botoes([self._botao("<- Voltar", lambda: self.render_combate(self.combate), cor=(51, 48, 42))])

    def _capturar(self, usou):
        if self.combate and not self.combate.terminado:
            self.combate.jogador_captura(usou)

    def _capturar_esfera(self):
        if self.combate.inimigo.chefe:
            self.render_combate(self.combate)
            return
        for i in self.jogador.inventario:
            if i.efeito.get("captura"):
                self.jogador.inventario.remove(i)
                break
        self.combate.jogador_captura(usou_esfera=True)

    def fim_combate(self, resultado):
        if resultado == "derrota":
            self.log("\n  ! Você foi derrotado...", "vilao")
            self.combate = None
            self.painel.limpar()
            self.painel.add_botoes([self._botao("Tela inicial", self.tela_titulo)])
            return
        self.combate = None
        if self.jogador.pontos_atributo > 0:
            self.tela_atributos(lambda: self.ir_para_no(self.destino_pos_combate))
        else:
            self.ir_para_no(self.destino_pos_combate)

    # ================= ATRIBUTOS =================
    def tela_atributos(self, ao_concluir):
        self._attr_callback = ao_concluir
        self.modo = "menu"
        self.cenario = "reino"
        p = self.jogador
        self.painel.limpar()
        self.painel.add_label(f"Você tem {p.pontos_atributo} ponto(s) de atributo para distribuir.", theme.OURO)
        self.painel.add_label(f"HP máx {p.hp_max} | Dano {p.dano} | Defesa {p.defesa} | "
                              f"{p.nome_recurso} máx {p.recurso_max}", theme.TEXTO)
        g = core.ATRIBUTO_GANHOS
        botoes = [self._botao(f"+{g['hp']} HP", lambda: self._gastar_attr("hp")),
                  self._botao(f"+{g['dano']} Dano", lambda: self._gastar_attr("dano")),
                  self._botao(f"+{g['defesa']} Defesa", lambda: self._gastar_attr("defesa")),
                  self._botao(f"+{g['recurso']} {p.nome_recurso}", lambda: self._gastar_attr("recurso"))]
        self.painel.add_botoes(botoes)
        self.painel.add_botoes([self._botao("Concluir distribuição", self._concluir_attr, cor=(51, 48, 42))])

    def _gastar_attr(self, atributo):
        p = self.jogador
        if p.pontos_atributo <= 0:
            return
        p.pontos_atributo -= 1
        g = core.ATRIBUTO_GANHOS
        if atributo == "hp":
            p.hp_max += g["hp"]; p.hp += g["hp"]
        elif atributo == "dano":
            p.dano += g["dano"]
        elif atributo == "defesa":
            p.defesa += g["defesa"]
        elif atributo == "recurso":
            p.recurso_max += g["recurso"]; p.recurso += g["recurso"]
        self.tela_atributos(self._attr_callback)

    def _concluir_attr(self):
        cb = self._attr_callback
        self._attr_callback = None
        if cb:
            cb()

    # ================= SALVAR / CARREGAR =================
    def salvar_jogo(self):
        if not self.jogador:
            return
        dados = {"versao": core.SAVE_VERSION, "jogador": self.jogador.to_dict(), "no_atual": self.no_atual}
        tmp = SAVE_FILE + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
                f.flush(); os.fsync(f.fileno())
            os.replace(tmp, SAVE_FILE)
            self.log("  * Progresso salvo com sucesso.", "sistema")
        except OSError as e:
            self._modal(f"Não foi possível salvar: {e}", [("Ok", self._fechar_modal)])

    def carregar_jogo(self):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
            if not isinstance(dados, dict) or "jogador" not in dados:
                raise ValueError("estrutura de save inválida")
            self.jogador = core.Personagem.from_dict(dados["jogador"])
            self.limpar_log()
            self.log("Jogo carregado. Bem-vindo de volta!", "titulo")
            self.ir_para_no(dados.get("no_atual") or "inicio")
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
            self._modal(f"Save corrompido ou ilegível: {e}", [("Ok", self.tela_titulo)])

    # ================= SAÍDA =================
    def menu_sair(self):
        if not self.jogador:
            self.pedir_sair()
            return
        self._modal("O que deseja fazer? (Salve antes — progresso não salvo será perdido.)",
                    [("Voltar ao Menu Principal", lambda: (self._fechar_modal(), self.tela_titulo())),
                     ("Sair do Jogo", self._sair_de_vez),
                     ("Cancelar (continuar)", self._fechar_modal)])

    def pedir_sair(self):
        if self.jogador:
            self._modal("Deseja mesmo sair? Progresso não salvo será perdido.",
                        [("Sim, sair", self._sair_de_vez), ("Cancelar", self._fechar_modal)])
        else:
            self._sair_de_vez()

    def _sair_de_vez(self):
        self.rodando = False

    # ================= MODAL =================
    def _modal(self, msg, opcoes):
        self.modal = ui.Modal(msg, opcoes)

    def _fechar_modal(self):
        self.modal = None

    # ================= EFEITOS DE COMBATE =================
    def _spawn_fx_combate(self):
        if not self.combate:
            return
        p = self.jogador
        ini = self.combate.inimigo
        W, H, stage, panel = self._rects()
        cena, _ = self._cena_console_rects(stage)
        chao = int(cena.h * 0.82)
        ant_i = self._prev_hp.get("ini")
        if ant_i is not None and ini.hp < ant_i:
            self.fx.append({"t": "flash", "alvo": "inimigo", "vida": 0.16})
            self.fx.append({"t": "dano", "x": cena.w * 0.72, "y": chao - altura_inimigo(ini.nome) * 0.5,
                            "v": ant_i - ini.hp, "vida": 0.7})
        ant_h = self._prev_hp.get("heroi")
        if ant_h is not None and p.hp < ant_h:
            self.fx.append({"t": "flash", "alvo": "heroi", "vida": 0.16})
            self.fx.append({"t": "dano", "x": cena.w * 0.26, "y": chao - 90, "v": ant_h - p.hp, "vida": 0.7})
        self._prev_hp = {"ini": ini.hp, "heroi": p.hp}

    # ================= LOOP =================
    def run(self):
        while self.rodando:
            dt = self.clock.tick(60) / 1000.0
            self.t += dt
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.pedir_sair()
                continue
            if event.type == pygame.VIDEORESIZE:
                w = max(LARG_MIN, event.w); h = max(ALT_MIN, event.h)
                self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
                continue
            if self.modal:
                cb = self.modal.handle_event(event)
                if cb:
                    cb()
                continue
            if self.text_input and event.type == pygame.KEYDOWN:
                r = self.text_input.handle(event)
                if r == "enter" and self._on_enter_nome:
                    self._on_enter_nome()
                continue
            if event.type == pygame.KEYDOWN and self.modo == "combate" and self.combate and not self.combate.terminado:
                self._tecla_combate(event.key)
            cb = self.painel.handle_event(event)
            if cb:
                cb()

    def _tecla_combate(self, key):
        if key == pygame.K_1:
            self.menu_ataques()
        elif key == pygame.K_2:
            self._acao_defender()
        elif key == pygame.K_3:
            self.menu_itens()
        elif key == pygame.K_4:
            self.menu_captura()
        elif key == pygame.K_5:
            self._acao_fugir()

    def _update(self, dt):
        W, H, stage, panel = self._rects()
        cena, console = self._cena_console_rects(stage)
        cfg = (self.cenario, self.modo, cena.w, cena.h)
        if cfg != self._cfg_part:
            self.particles.configurar(self.cenario, self.modo, cena.w, cena.h)
            self._cfg_part = cfg
        self.particles.update(dt)
        self.painel.layout(panel)
        self.painel.update(dt)
        if self.text_input:
            self.text_input.update(dt)
        if self.modal:
            self.modal.layout(W, H)
        # efeitos
        vivos = []
        for f in self.fx:
            f["vida"] -= dt
            if f["vida"] > 0:
                if f["t"] == "dano":
                    f["y"] -= 40 * dt
                vivos.append(f)
        self.fx = vivos
        self.title_dragon_x += 26 * dt
        if self.title_dragon_x > W + 120:
            self.title_dragon_x = -160

    # ================= DESENHO =================
    def _draw(self):
        self.screen.fill(theme.FUNDO)
        W, H, stage, panel = self._rects()
        if stage.h < 40 or stage.w < 40:
            return
        cena, console = self._cena_console_rects(stage)
        cena_surf = self.screen.subsurface(cena)
        # fundo + partículas
        titulo_img = False
        if self.modo == "titulo":
            titulo_img = backgrounds.desenhar_titulo(cena_surf, cena.w, cena.h)
        elif self.modo == "mapa":
            self._desenhar_mapa(cena_surf, cena.w, cena.h)
        elif self.modo == "combate" and self.combate:
            backgrounds.desenhar_fundo(cena_surf, cena.w, cena.h, self.cenario)
        else:
            backgrounds.desenhar_fundo(cena_surf, cena.w, cena.h, self.cenario)
        if self.modo != "mapa":
            self.particles.draw(cena_surf)
        # sprites
        if self.modo == "titulo":
            if not titulo_img:
                # a arte dedicada (titulo.jpg) já traz o título embutido;
                # só desenhamos texto/dragão no fundo procedural de fallback.
                self._desenhar_titulo_extra(cena_surf, cena.w, cena.h)
        elif self.modo == "combate" and self.combate:
            self._desenhar_combate(cena_surf, cena.w, cena.h)
        # console de texto
        ui.render_console(self.screen, console, self.log_buffer)
        # barra de status
        self._desenhar_status(W)
        # painel
        mouse = pygame.mouse.get_pos()
        self.painel.draw(self.screen, mouse)
        if self.modal:
            self.modal.layout(W, H)
            self.modal.draw(self.screen, mouse)

    def _desenhar_status(self, W):
        pygame.draw.rect(self.screen, theme.PAINEL, (0, 0, W, STATUS_H))
        if not self.jogador:
            t = theme.fonte(16, True).render("CRÔNICAS DE PEDRAVALE", True, theme.OURO)
            self.screen.blit(t, (12, (STATUS_H - t.get_height()) // 2))
            return
        p = self.jogador
        arma = p.arma.nome_completo if p.arma else "(sem arma)"
        armadura = p.armadura.nome_completo if p.armadura else "(sem armadura)"
        aliados = f"  ·  Aliados: {len(p.aliados)}" if p.aliados else ""
        l1 = (f"{p.nome} · {p.classe} Nv.{p.nivel} [{p.dificuldade}] · HP {p.hp}/{p.hp_max} · "
              f"{p.nome_recurso} {p.recurso}/{p.recurso_max} · XP {p.xp}/{p.xp_prox} · "
              f"Karma {p.karma} ({p.alinhamento}){aliados}")
        l2 = f"Dano {p.dano_total} · Defesa {p.defesa_total} · Arma: {arma} · Armadura: {armadura}"
        f = theme.fonte(12, True)
        self.screen.blit(f.render(l1, True, theme.TEXTO), (12, 6))
        self.screen.blit(theme.fonte(12).render(l2, True, (200, 190, 170)), (12, 26))

    def _desenhar_titulo_extra(self, surf, w, h):
        # dragão voando (fundo procedural)
        dragao = self.assets.inimigo("Dragao", 64, face=-1)
        bob = math.sin(self.t * 2) * 10
        surf.blit(dragao, (int(self.title_dragon_x), int(h * 0.3 + bob)))
        self._titulo_texto(surf, w, h)

    def _titulo_texto(self, surf, w, h, sombra=False):
        # título (também usado sobre a arte dedicada, que é recortada na cena larga)
        t1 = theme.fonte(38, True).render("CRÔNICAS DE PEDRAVALE", True, theme.OURO)
        t2 = theme.fonte(17).render("RPG de Aventura por Escolhas", True, theme.TEXTO)
        x1, y1 = (w - t1.get_width()) // 2, int(h * 0.14)
        x2, y2 = (w - t2.get_width()) // 2, int(h * 0.14) + 46
        if sombra:
            s1 = theme.fonte(38, True).render("CRÔNICAS DE PEDRAVALE", True, (10, 6, 4))
            s2 = theme.fonte(17).render("RPG de Aventura por Escolhas", True, (10, 6, 4))
            surf.blit(s1, (x1 + 2, y1 + 2)); surf.blit(s2, (x2 + 2, y2 + 2))
        surf.blit(t1, (x1, y1))
        surf.blit(t2, (x2, y2))

    def _desenhar_combate(self, surf, w, h):
        p = self.jogador
        ini = self.combate.inimigo
        chao = int(h * 0.82)
        # herói
        h_alt = min(int(h * 0.42), 150)
        sp_h = self.assets.heroi(p.classe, h_alt, face=1)
        hx = int(w * 0.26)
        flash_h = any(f["t"] == "flash" and f["alvo"] == "heroi" for f in self.fx)
        self._blit_sprite(surf, sp_h, hx, chao, flash_h)
        # inimigo
        i_alt = min(int(h * 0.6), altura_inimigo(ini.nome))
        sp_i = self.assets.inimigo(ini.nome, i_alt, face=-1)
        ix = int(w * 0.72)
        flash_i = any(f["t"] == "flash" and f["alvo"] == "inimigo" for f in self.fx)
        self._blit_sprite(surf, sp_i, ix, chao, flash_i)
        # barras
        ui.barra(surf, hx, chao - h_alt - 26, 180, p.hp, p.hp_max,
                 theme.cor_por_fracao(p.hp / p.hp_max if p.hp_max else 0), p.nome[:12])
        ui.barra(surf, hx, chao - h_alt - 4, 180, p.recurso, p.recurso_max, (111, 177, 224), p.nome_recurso)
        ui.barra(surf, ix, chao - i_alt - 26, 190, max(0, ini.hp), ini.hp_max,
                 theme.cor_por_fracao(ini.fracao_hp), ini.nome[:16])
        if p.veneno > 0:
            v = theme.fonte(12, True).render("ENVENENADO", True, (176, 127, 208))
            surf.blit(v, (hx - v.get_width() // 2, chao - h_alt - 44))
        # aliados
        for idx, a in enumerate(p.aliados[:3]):
            ax = int(w * (0.07 + idx * 0.06))
            ah = 64
            sp_a = self.assets.aliado(a["nome"], ah, face=1)
            self._blit_sprite(surf, sp_a, ax, chao + 6 + idx * 3, False)
            hp_max = max(1, a.get("hp_max", a["hp"]))
            frac = max(0.0, min(1.0, a["hp"] / hp_max))
            by = chao + 6 + idx * 3 - ah - 8
            pygame.draw.rect(surf, (21, 19, 15), (ax - 20, by, 40, 5))
            if frac > 0:
                pygame.draw.rect(surf, theme.cor_por_fracao(frac), (ax - 19, by + 1, int(38 * frac), 3))
            nm = theme.fonte(11, True).render(a["nome"].split(",")[0][:10], True, (127, 201, 127))
            surf.blit(nm, (ax - nm.get_width() // 2, by - 14))
        if len(p.aliados) > 3:
            extra = theme.fonte(11).render(f"+{len(p.aliados)-3} aliado(s)", True, (127, 201, 127))
            surf.blit(extra, (int(w * 0.04), chao + 18))
        # dano flutuante
        for f in self.fx:
            if f["t"] == "dano":
                a = max(0, min(255, int(255 * f["vida"] / 0.7)))
                img = theme.fonte(22, True).render(f"-{f['v']}", True, (255, 106, 91))
                img.set_alpha(a)
                surf.blit(img, (int(f["x"] - img.get_width() / 2), int(f["y"])))

    def _blit_sprite(self, surf, sp, cx, base, flash):
        x = cx - sp.get_width() // 2
        y = base - sp.get_height()
        surf.blit(sp, (x, y))
        if flash:
            fl = sp.copy()
            fl.fill((255, 255, 255, 150), special_flags=pygame.BLEND_RGBA_MULT)
            white = pygame.Surface(sp.get_size(), pygame.SRCALPHA)
            white.fill((255, 255, 255, 120))
            mask = pygame.mask.from_surface(sp)
            ms = mask.to_surface(setcolor=(255, 255, 255, 130), unsetcolor=(0, 0, 0, 0))
            surf.blit(ms, (x, y))

    def _desenhar_mapa(self, surf, w, h):
        if backgrounds.desenhar_mapa(surf, w, h):
            # A arte já traz regiões e título; só marcamos onde o jogador está.
            atual = getattr(self, "_cenario_pre_mapa", self.cenario)
            for _nome, fx, fy, cens in REGIOES_MAPA:
                if atual in cens:
                    x, y = int(fx * w), int(fy * h)
                    aqui = theme.fonte(12, True).render("* Você está aqui *", True, (255, 240, 200))
                    sombra = theme.fonte(12, True).render("* Você está aqui *", True, (30, 18, 10))
                    bx = x - aqui.get_width() // 2
                    surf.blit(sombra, (bx + 1, y + 17))
                    surf.blit(aqui, (bx, y + 16))
            return
        surf.fill((203, 176, 131))
        pygame.draw.rect(surf, (122, 92, 52), (10, 10, w - 20, h - 20), 3)
        pts = [(r[1], r[2]) for r in REGIOES_MAPA]
        for i in range(len(pts) - 1):
            pygame.draw.line(surf, (122, 92, 52), (pts[i][0] * w, pts[i][1] * h),
                             (pts[i + 1][0] * w, pts[i + 1][1] * h), 3)
        atual = getattr(self, "_cenario_pre_mapa", self.cenario)
        for nome, fx, fy, cens in REGIOES_MAPA:
            x, y = int(fx * w), int(fy * h)
            pygame.draw.circle(surf, (138, 58, 42), (x, y), 11)
            pygame.draw.circle(surf, (58, 26, 16), (x, y), 11, 2)
            nm = theme.fonte(13, True).render(nome, True, (42, 28, 14))
            surf.blit(nm, (x - nm.get_width() // 2, y - 30))
            if atual in cens:
                aqui = theme.fonte(11, True).render("* Você está aqui *", True, (138, 58, 42))
                surf.blit(aqui, (x - aqui.get_width() // 2, y + 16))
        titulo = theme.fonte(15, True).render("MAPA DE PEDRAVALE E ARREDORES", True, (42, 28, 14))
        surf.blit(titulo, ((w - titulo.get_width()) // 2, 20))
