# -*- coding: utf-8 -*-
"""
core.py — Lógica pura de Crônicas de Pedravale (SEM dependência de Tkinter).

Extraído verbatim de rpg_medieval.py: constantes de balanceamento, Item,
Personagem, Inimigo, Combate e Historia. A camada de UI (Pygame) fornece a
um controlador os métodos que a classe Combate espera via `self.gj`:
    log(texto, tag), render_combate(combate), fim_combate(resultado),
    dropar_loot(inimigo).
"""

from __future__ import annotations
from typing import Optional
import random


# === CONSTANTES E BALANCEAMENTO ===

ARQUIVO_SAVE = "save_pedravale.json"
# Versão do schema do save. Incremente ao mudar o formato de dados gravado;
# carregar_jogo usa isto para migrar/avisar sobre saves de versões diferentes.
SAVE_VERSION = 2

# --- Sistema de raridade: multiplicadores claros sobre os stats base ---
RARIDADES = {
    "Comum":     1.0,
    "Raro":      1.4,
    "Épico":     1.9,
    "Lendário":  2.5,
}

# Pesos de drop: lendários são genuinamente raros.
PESOS_RARIDADE = {
    "Comum":    62,
    "Raro":     27,
    "Épico":     9,
    "Lendário":  2,
}

# --- Dificuldade: multiplica HP e dano dos inimigos (inclusive o chefe). ---
DIFICULDADES = {
    "Fácil":   {"inimigo": 0.88, "desc": "Inimigos mais fracos. Bom para a história."},
    "Normal":  {"inimigo": 1.00, "desc": "Experiência equilibrada (recomendado)."},
    "Difícil": {"inimigo": 1.13, "desc": "Inimigos mais perigosos. Para veteranos."},
}
DIFICULDADE_PADRAO = "Normal"

# --- Constantes de combate (ajuste o "feel" do jogo aqui) ---
CRIT_MULT            = 1.8     # multiplicador de dano em acerto crítico
DEFESA_REDUCAO       = 0.5     # fração de dano recebido ao Defender (50%)
DEFEND_REGEN_FRAC    = 0.18    # fração do recurso máx. recuperada ao Defender
CAPTURA_BASE         = 0.05    # chance de captura com alvo de HP cheio
CAPTURA_INCLINACAO   = 0.75    # quanto a chance sobe conforme o HP do alvo cai
CAPTURA_ESFERA_BONUS = 0.15    # bônus da Esfera de Selamento
CAPTURA_MIN          = 0.05
CAPTURA_MAX          = 0.92
FUGA_CHANCE_NORMAL   = 0.60    # chefes não permitem fuga (ver Combate.jogador_foge)
DROP_BONUS_CHEFE        = 25   # bônus de raridade nos drops do chefe
DROP_EQUIP_CHANCE_CHEFE  = 1.0
DROP_EQUIP_CHANCE_NORMAL = 0.5
DROP_CONSUMIVEL_CHANCE   = 0.6
ALIADO_ALVO_CHANCE   = 0.40    # chance de o inimigo atacar um aliado em vez do herói

# --- Ganhos automáticos ao subir de nível e por ponto de atributo ---
GANHO_NIVEL    = {"pontos_atributo": 3, "hp_max": 12, "recurso_max": 6, "dano": 2, "defesa": 1}
ATRIBUTO_GANHOS = {"hp": 10, "dano": 3, "defesa": 2, "recurso": 10}

# --- Definição das classes jogáveis (stats base balanceados) ---
# recurso = nome do recurso de habilidade (Vigor / MP / Energia)
CLASSES = {
    "Cavaleiro": {
        "descricao": "Tanque corpo a corpo. HP alto, defesa alta, sem MP. Usa Vigor.",
        "hp":       120,
        "recurso":  50,      # Vigor
        "nome_recurso": "Vigor",
        "dano":     12,
        "defesa":   12,
        "crit":     0.08,
        "evasao":   0.05,
    },
    "Mago": {
        "descricao": "Glass cannon. HP baixo, defesa baixa, dano mágico altíssimo. Usa MP.",
        "hp":       80,
        "recurso":  100,     # MP
        "nome_recurso": "MP",
        "dano":     18,
        "defesa":   5,
        "crit":     0.10,
        "evasao":   0.08,
    },
    "Arqueiro": {
        "descricao": "DPS ágil. HP médio, dano à distância alto, ótimo crítico/evasão. Usa Energia.",
        "hp":       95,
        "recurso":  70,      # Energia
        "nome_recurso": "Energia",
        "dano":     15,
        "defesa":   7,
        "crit":     0.25,
        "evasao":   0.18,
    },
}

# --- Ataques por classe ---
# Cada classe começa com um ATAQUE BÁSICO de custo 0 (nunca fica sem ações),
# seguido das habilidades que consomem o recurso da classe.
# mult        = multiplicador de dano sobre o dano total do personagem
# custo       = custo do recurso da classe
# efeito      = efeito especial opcional
# crit_bonus  = bônus de chance de crítico do golpe
ATAQUES = {
    "Cavaleiro": [
        {"nome": "Golpe Simples", "custo": 0,  "mult": 1.0,
         "desc": "Um golpe básico, sem custo de Vigor."},
        {"nome": "Investida",    "custo": 10, "mult": 1.3, "desc": "Avança e atinge o alvo com força."},
        {"nome": "Golpe Pesado", "custo": 22, "mult": 1.9, "desc": "Um golpe devastador, mas caro."},
        {"nome": "Provocar",     "custo": 6,  "mult": 0.6, "efeito": "defesa_buff",
         "desc": "Provoca o inimigo e assume postura defensiva (-dano no próximo turno)."},
    ],
    "Mago": [
        {"nome": "Choque Arcano", "custo": 0, "mult": 0.9,
         "desc": "Descarga arcana básica, sem custo de MP."},
        {"nome": "Bola de Fogo", "custo": 22, "mult": 1.8, "desc": "Esfera flamejante de alto dano."},
        {"nome": "Lança de Gelo","custo": 16, "mult": 1.3, "efeito": "gelo",
         "desc": "Atinge e enregela o alvo, causando dano contínuo de frio (3 turnos)."},
        {"nome": "Cura",         "custo": 26, "mult": 1.6, "efeito": "cura",
         "desc": "Restaura uma boa quantidade de HP."},
    ],
    "Arqueiro": [
        {"nome": "Tiro Rápido",  "custo": 0,  "mult": 0.95,
         "desc": "Disparo rápido e barato, sem custo de Energia."},
        {"nome": "Flecha Precisa", "custo": 10, "mult": 1.2, "crit_bonus": 0.20,
         "desc": "Tiro certeiro com alta chance de crítico."},
        {"nome": "Chuva de Flechas","custo": 26, "mult": 1.7,
         "desc": "Salva de flechas que cobre o alvo."},
        {"nome": "Tiro Perfurante", "custo": 18, "mult": 1.5, "efeito": "ignora_defesa",
         "desc": "Atravessa a armadura, ignorando a defesa do alvo."},
    ],
}

# --- Bestiário medieval clássico (stats base, escalados por nível depois) ---
# veneno: chance de aplicar dano contínuo ao jogador
# Curva de ameaça: Slime/Goblin são triviais (ensinam o combate), e a tensão
# real cresce até o Troll, o predador-ápice comum (perigoso de verdade).
BESTIARIO = {
    "Slime":     {"hp": 30,  "dano": 7,  "defesa": 2,  "xp": 18, "crit": 0.02, "evasao": 0.02, "veneno": 0.30},
    "Goblin":    {"hp": 40,  "dano": 12, "defesa": 3,  "xp": 26, "crit": 0.06, "evasao": 0.10, "veneno": 0.0},
    "Lobo":      {"hp": 52,  "dano": 18, "defesa": 4,  "xp": 34, "crit": 0.15, "evasao": 0.18, "veneno": 0.0},
    "Esqueleto": {"hp": 60,  "dano": 17, "defesa": 7,  "xp": 40, "crit": 0.08, "evasao": 0.06, "veneno": 0.0},
    "Orc":       {"hp": 96,  "dano": 26, "defesa": 9,  "xp": 60, "crit": 0.09, "evasao": 0.06, "veneno": 0.0},
    "Troll":     {"hp": 150, "dano": 34, "defesa": 12, "xp": 95, "crit": 0.08, "evasao": 0.03, "veneno": 0.0},
}

# Prefixos para dar sensação de geração dinâmica.
PREFIXOS_INIMIGO = ["", "", "", "Feroz ", "Esfomeado ", "Ancião ", "Corrompido ", "Sombrio ", "das Cavernas "]

# Nomes de arma por classe (a arma de cada classe encaixa melhor nela).
NOMES_ARMA = {
    "Cavaleiro": ["Espada", "Machado", "Maça", "Lâmina", "Montante"],
    "Mago":      ["Cajado", "Varinha", "Orbe", "Cetro", "Grimório"],
    "Arqueiro":  ["Arco", "Besta", "Arco Longo", "Estilingue de Guerra"],
}
NOMES_ARMADURA = ["Couraça", "Cota de Malha", "Túnica Encantada", "Peitoral", "Manto Reforçado"]

# === UTILITÁRIOS ===

def sortear_raridade(bonus_lendario: int = 0) -> str:
    """Sorteia uma raridade de acordo com os pesos. bonus_lendario aumenta
    a chance de itens Épico/Lendário (usado em drops de chefe), retirando
    peso do pool Comum para que o ganho de raridade seja perceptível."""
    pesos = dict(PESOS_RARIDADE)
    if bonus_lendario:
        pesos["Lendário"] += bonus_lendario
        pesos["Épico"] += bonus_lendario
        pesos["Comum"] = max(0, pesos["Comum"] - 2 * bonus_lendario)
    opcoes = list(pesos.keys())
    return random.choices(opcoes, weights=[pesos[o] for o in opcoes], k=1)[0]


def clamp(valor, minimo, maximo):
    """Mantém um valor dentro de um intervalo (funciona para int e float)."""
    return max(minimo, min(maximo, valor))


def cor_por_fracao(frac: float) -> str:
    """Verde > amarelo > vermelho conforme a fração de HP cai."""
    if frac > 0.6:
        return "#7fc97f"
    if frac > 0.3:
        return "#f2c14e"
    return "#e06a5b"


def item_tera_efeito(jogador, item):
    """Diz se usar este consumível teria QUALQUER efeito no estado atual
    (evita gastar item/turno à toa)."""
    ef = item.efeito
    if ef.get("antidoto") and jogador.veneno > 0:
        return True
    if "cura" in ef and jogador.hp < jogador.hp_max:
        return True
    if "recurso" in ef and jogador.recurso < jogador.recurso_max:
        return True
    return False

# === ITEM E FÁBRICAS ===

class Item:
    """Representa qualquer item do jogo.

    tipo: "arma" | "armadura" | "consumivel" | "captura"
    valor_base: dano (arma) ou defesa (armadura).
    efeito: dict para consumíveis, ex.: {"cura": 40} ou {"recurso": 30}.
    """

    def __init__(self, nome: str, tipo: str, raridade: str = "Comum",
                 valor_base: int = 0, efeito: Optional[dict] = None,
                 descricao: str = "") -> None:
        self.nome = nome
        self.tipo = tipo
        self.raridade = raridade if raridade in RARIDADES else "Comum"
        self.valor_base = valor_base
        self.efeito = efeito or {}
        self.descricao = descricao

    @property
    def valor(self) -> int:
        """Valor final = base * multiplicador de raridade (arredondado)."""
        return round(self.valor_base * RARIDADES.get(self.raridade, 1.0))

    @property
    def nome_completo(self) -> str:
        if self.tipo in ("arma", "armadura"):
            sufixo = "dano" if self.tipo == "arma" else "def"
            return f"[{self.raridade}] {self.nome} (+{self.valor} {sufixo})"
        return f"{self.nome}"

    # --- Serialização para salvar/carregar ---
    def to_dict(self) -> dict:
        return {
            "nome": self.nome, "tipo": self.tipo, "raridade": self.raridade,
            "valor_base": self.valor_base, "efeito": self.efeito,
            "descricao": self.descricao,
        }

    @staticmethod
    def from_dict(d: dict) -> "Item":
        # Tolerante a saves antigos/parciais.
        return Item(
            d.get("nome", "Item"), d.get("tipo", "consumivel"),
            d.get("raridade", "Comum"), d.get("valor_base", 0),
            d.get("efeito"), d.get("descricao", ""),
        )


# --- Fábricas de itens -------------------------------------------------

def gerar_arma(nivel: int, classe: str, raridade: Optional[str] = None,
               bonus_lendario: int = 0) -> Item:
    """Cria uma arma escalada pelo nível, adequada à classe.
    Se `raridade` for informada, força essa raridade (ex.: recompensa fixa)."""
    raridade = raridade or sortear_raridade(bonus_lendario)
    nome = random.choice(NOMES_ARMA.get(classe, NOMES_ARMA["Cavaleiro"]))
    base = 5 + nivel * 2 + random.randint(0, nivel + 2)
    return Item(nome, "arma", raridade, base, descricao="Uma arma de batalha.")


def gerar_armadura(nivel: int, raridade: Optional[str] = None,
                   bonus_lendario: int = 0) -> Item:
    """Cria uma armadura escalada pelo nível.
    Se `raridade` for informada, força essa raridade."""
    raridade = raridade or sortear_raridade(bonus_lendario)
    nome = random.choice(NOMES_ARMADURA)
    base = 3 + int(nivel * 1.5) + random.randint(0, nivel + 1)
    return Item(nome, "armadura", raridade, base, descricao="Proteção contra golpes.")


def gerar_consumivel(tipo: str = "cura") -> Item:
    """Cria poções e itens de captura."""
    catalogo = {
        "cura":      Item("Poção de Cura", "consumivel", "Comum", efeito={"cura": 45},
                          descricao="Restaura 45 de HP."),
        "cura_g":    Item("Poção de Cura Maior", "consumivel", "Raro", efeito={"cura": 90},
                          descricao="Restaura 90 de HP."),
        "recurso":   Item("Poção de Energia", "consumivel", "Comum", efeito={"recurso": 40},
                          descricao="Restaura 40 do recurso da classe."),
        "antidoto":  Item("Antídoto", "consumivel", "Comum", efeito={"antidoto": True, "cura": 10},
                          descricao="Remove veneno e cura 10 de HP."),
        "captura":   Item("Esfera de Selamento", "captura", "Raro", efeito={"captura": True},
                          descricao="Aumenta a chance de capturar um inimigo enfraquecido."),
    }
    return catalogo[tipo]

# === PERSONAGEM ===

class Personagem:
    """O herói (ou vilão) controlado pelo jogador."""

    def __init__(self, nome: str, genero: str, classe: str,
                 dificuldade: str = DIFICULDADE_PADRAO) -> None:
        self.nome = nome
        self.genero = genero
        self.classe = classe
        self.dificuldade = dificuldade if dificuldade in DIFICULDADES else DIFICULDADE_PADRAO

        base = CLASSES[classe]
        self.nome_recurso = base["nome_recurso"]
        self.hp_max = base["hp"]
        self.hp = base["hp"]
        self.recurso_max = base["recurso"]
        self.recurso = base["recurso"]
        self.dano = base["dano"]
        self.defesa = base["defesa"]
        self.crit = base["crit"]
        self.evasao = base["evasao"]

        self.nivel = 1
        self.xp = 0
        self.xp_prox = self._xp_para_nivel(2)
        self.pontos_atributo = 0

        self.karma = 0                # >0 herói, <0 vilão
        self.veneno = 0               # turnos de veneno restantes
        self.flags = []               # marcos de história (ex.: fragmentos coletados)
        self.eventos = []             # ids de escolhas únicas já feitas ("no:idx")

        self.inventario = []          # lista de Item
        self.aliados = []             # lista de dicts {"nome","dano","hp","hp_max"}
        self.arma = None
        self.armadura = None

        # Itens iniciais
        self.inventario.append(gerar_consumivel("cura"))
        self.inventario.append(gerar_consumivel("cura"))
        self.inventario.append(gerar_consumivel("recurso"))
        self.inventario.append(gerar_consumivel("captura"))

    # --- Dificuldade -------------------------------------------------
    @property
    def dif_mult(self) -> float:
        return DIFICULDADES.get(self.dificuldade, DIFICULDADES[DIFICULDADE_PADRAO])["inimigo"]

    # --- Curva de XP -------------------------------------------------
    @staticmethod
    def _xp_para_nivel(nivel: int) -> int:
        """XP necessário para alcançar determinado nível (curva suave)."""
        return int(80 * ((nivel - 1) ** 1.45)) + 60 * (nivel - 1)

    # --- Stats efetivos (com equipamento) ----------------------------
    @property
    def dano_total(self) -> int:
        return self.dano + (self.arma.valor if self.arma else 0)

    @property
    def defesa_total(self) -> int:
        return self.defesa + (self.armadura.valor if self.armadura else 0)

    # --- Operações de combate ----------------------------------------
    def curar(self, qtd: int) -> int:
        antes = self.hp
        self.hp = clamp(self.hp + qtd, 0, self.hp_max)
        return self.hp - antes

    def gastar_recurso(self, qtd: int) -> bool:
        if self.recurso < qtd:
            return False
        self.recurso -= qtd
        return True

    def restaurar_recurso(self, qtd: int) -> None:
        self.recurso = clamp(self.recurso + qtd, 0, self.recurso_max)

    def esta_vivo(self) -> bool:
        return self.hp > 0

    # --- Progressão --------------------------------------------------
    def ganhar_xp(self, qtd: int) -> int:
        """Adiciona XP e retorna quantos níveis subiu (para feedback)."""
        self.xp += qtd
        niveis = 0
        while self.xp >= self.xp_prox:
            self.xp -= self.xp_prox
            self.nivel += 1
            niveis += 1
            self.pontos_atributo += GANHO_NIVEL["pontos_atributo"]
            # Ganhos automáticos ao subir de nível
            self.hp_max += GANHO_NIVEL["hp_max"]
            self.recurso_max += GANHO_NIVEL["recurso_max"]
            self.dano += GANHO_NIVEL["dano"]
            self.defesa += GANHO_NIVEL["defesa"]
            self.hp = self.hp_max          # cura total ao subir
            self.recurso = self.recurso_max
            self.xp_prox = self._xp_para_nivel(self.nivel + 1)
        return niveis

    # --- Inventário/equipamento --------------------------------------
    def equipar(self, item: Item) -> None:
        """Equipa arma/armadura, devolvendo o item antigo ao inventário."""
        if item.tipo == "arma":
            if self.arma:
                self.inventario.append(self.arma)
            self.arma = item
        elif item.tipo == "armadura":
            if self.armadura:
                self.inventario.append(self.armadura)
            self.armadura = item
        if item in self.inventario:
            self.inventario.remove(item)

    @property
    def alinhamento(self) -> str:
        if self.karma >= 5:
            return "Herói"
        if self.karma <= -5:
            return "Vilão"
        return "Neutro"

    # --- Serialização -------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "nome": self.nome, "genero": self.genero, "classe": self.classe,
            "dificuldade": self.dificuldade,
            "hp_max": self.hp_max, "hp": self.hp,
            "recurso_max": self.recurso_max, "recurso": self.recurso,
            "nome_recurso": self.nome_recurso,
            "dano": self.dano, "defesa": self.defesa,
            "crit": self.crit, "evasao": self.evasao,
            "nivel": self.nivel, "xp": self.xp, "xp_prox": self.xp_prox,
            "pontos_atributo": self.pontos_atributo, "karma": self.karma,
            "veneno": self.veneno, "flags": list(self.flags),
            "eventos": list(self.eventos),
            "inventario": [i.to_dict() for i in self.inventario],
            "aliados": self.aliados,
            "arma": self.arma.to_dict() if self.arma else None,
            "armadura": self.armadura.to_dict() if self.armadura else None,
        }

    @staticmethod
    def from_dict(d: dict) -> "Personagem":
        """Reconstrói um Personagem tolerando saves antigos/parciais (usa .get)."""
        p = Personagem(
            d.get("nome", "Herói"), d.get("genero", "Outro"),
            d.get("classe", "Cavaleiro"), d.get("dificuldade", DIFICULDADE_PADRAO),
        )
        p.hp_max = d.get("hp_max", p.hp_max); p.hp = d.get("hp", p.hp_max)
        p.recurso_max = d.get("recurso_max", p.recurso_max)
        p.recurso = d.get("recurso", p.recurso_max)
        p.nome_recurso = d.get("nome_recurso", p.nome_recurso)
        p.dano = d.get("dano", p.dano); p.defesa = d.get("defesa", p.defesa)
        p.crit = d.get("crit", p.crit); p.evasao = d.get("evasao", p.evasao)
        p.nivel = d.get("nivel", 1); p.xp = d.get("xp", 0)
        p.xp_prox = d.get("xp_prox", Personagem._xp_para_nivel(p.nivel + 1))
        p.pontos_atributo = d.get("pontos_atributo", 0)
        p.karma = d.get("karma", 0)
        p.veneno = d.get("veneno", 0)
        flags = d.get("flags", [])
        p.flags = [str(f) for f in flags] if isinstance(flags, list) else []
        eventos = d.get("eventos", [])
        p.eventos = [str(e) for e in eventos] if isinstance(eventos, list) else []
        # Itens/equipamento: tolera entradas malformadas em vez de quebrar.
        p.inventario = [Item.from_dict(i) for i in d.get("inventario", []) if isinstance(i, dict)]
        p.arma = Item.from_dict(d["arma"]) if isinstance(d.get("arma"), dict) else None
        p.armadura = Item.from_dict(d["armadura"]) if isinstance(d.get("armadura"), dict) else None
        # Aliados: normaliza para o formato esperado pelo combate (evita KeyError tardio).
        p.aliados = []
        for a in d.get("aliados", []):
            if not isinstance(a, dict):
                continue
            try:
                hp_max = int(a.get("hp_max", a.get("hp", 30)))
                p.aliados.append({
                    "nome": str(a.get("nome", "Aliado")),
                    "dano": int(a.get("dano", 4)),
                    "hp": int(a.get("hp", hp_max)),
                    "hp_max": hp_max,
                })
            except (ValueError, TypeError):
                continue
        return p

# === INIMIGO ===

class Inimigo:
    """Um monstro ou inimigo enfrentado em combate."""

    def __init__(self, nome: str, hp: int, dano: int, defesa: int, xp: int,
                 nivel: int, crit: float = 0.05, evasao: float = 0.05,
                 veneno: float = 0.0, chefe: bool = False) -> None:
        self.nome = nome
        self.hp_max = hp
        self.hp = hp
        self.dano = dano
        self.defesa = defesa
        self.xp = xp
        self.nivel = nivel
        self.crit = crit
        self.evasao = evasao
        self.veneno = veneno
        self.chefe = chefe
        # Dano contínuo recebido (ex.: gelo do Mago)
        self.dot_turnos = 0
        self.dot_dano = 0

    def esta_vivo(self) -> bool:
        return self.hp > 0

    @property
    def defesa_total(self) -> int:
        # Simetria com Personagem.defesa_total; permite buffs/equip futuros.
        return self.defesa

    @property
    def fracao_hp(self) -> float:
        return self.hp / self.hp_max if self.hp_max else 0


def gerar_inimigo(nivel_jogador: int, tipo: Optional[str] = None,
                  chefe: bool = False, dif_mult: float = 1.0) -> Inimigo:
    """Gera um inimigo escalado para evitar combates triviais ou impossíveis.

    O escalonamento gira em torno do nível do jogador (±1) para manter o
    desafio justo. Chefes (Dragão) recebem stats bem maiores. `dif_mult`
    multiplica HP e dano conforme a dificuldade escolhida.
    """
    if chefe:
        nivel = nivel_jogador + 1
        fator = 1 + (nivel - 1) * 0.29
        nome = random.choice(["Dragão Negro Vorthak", "Dragão Anciã Ignara", "Dragão das Cinzas"])
        return Inimigo(
            nome,
            hp=int(220 * fator * dif_mult), dano=int(28 * fator * dif_mult),
            defesa=int(12 * fator),
            xp=int(180 * fator), nivel=nivel, crit=0.12, evasao=0.05, chefe=True,
        )

    tipo = tipo or random.choice(list(BESTIARIO.keys()))
    base = BESTIARIO[tipo]
    # Nível do inimigo perto do jogador, com leve variação.
    nivel = max(1, nivel_jogador + random.randint(-1, 1))
    # HP/defesa e dano escalam separadamente: o dano sobe mais rápido para que
    # os inimigos continuem ameaçadores conforme o herói ganha HP e defesa.
    # (No nível 1 ambos valem 1.0, então o começo de jogo segue suave.)
    fator_def  = 1 + (nivel - 1) * 0.22   # HP, defesa, XP
    fator_dano = 1 + (nivel - 1) * 0.32   # dano ofensivo
    variacao = random.uniform(0.9, 1.15)   # variação para sensação dinâmica
    prefixo = random.choice(PREFIXOS_INIMIGO)
    nome = f"{prefixo}{tipo}".strip()

    return Inimigo(
        nome,
        hp=int(base["hp"] * fator_def * variacao * dif_mult),
        dano=int(base["dano"] * fator_dano * variacao * dif_mult),
        defesa=int(base["defesa"] * fator_def),
        xp=int(base["xp"] * fator_def),
        nivel=nivel,
        crit=base["crit"], evasao=base["evasao"], veneno=base["veneno"],
    )

# === COMBATE ===

class Combate:
    """Gerencia uma batalha por turnos.

    Recebe o GerenciadorJogo (gj) para escrever no log e atualizar a UI.
    Ao terminar, chama gj.fim_combate(resultado), onde resultado é um de:
    "vitoria", "derrota", "fuga", "captura". O destino pós-combate é de
    responsabilidade do GerenciadorJogo (destino_pos_combate).
    """

    def __init__(self, gj, jogador: Personagem,
                 inimigo: Inimigo) -> None:
        self.gj = gj
        self.jogador = jogador
        self.inimigo = inimigo
        self.jogador_defendendo = False
        self.terminado = False
        self.turno = 1
        # Cada combate começa "limpo": veneno residual não atravessa batalhas.
        self.jogador.veneno = 0

    # --- Chance de captura (fonte única da verdade) ------------------
    def chance_captura(self, usou_esfera: bool = False) -> float:
        c = CAPTURA_BASE + (1 - self.inimigo.fracao_hp) * CAPTURA_INCLINACAO
        if usou_esfera:
            c += CAPTURA_ESFERA_BONUS
        return clamp(c, CAPTURA_MIN, CAPTURA_MAX)

    # --- Cálculo de dano genérico ------------------------------------
    def _calc_dano(self, base, mult, crit_chance, defesa_alvo, ignora_def=False):
        dano = base * mult
        crit = random.random() < crit_chance
        if crit:
            dano *= CRIT_MULT
        if not ignora_def:
            dano -= defesa_alvo
        return max(1, int(round(dano))), crit

    # --- Ações do jogador --------------------------------------------
    def jogador_ataca(self, ataque):
        if self.terminado:
            return
        custo = ataque.get("custo", 0)
        if self.jogador.recurso < custo:
            self.gj.log(f"  x {self.jogador.nome_recurso} insuficiente para {ataque['nome']}!", "sistema")
            return
        self.jogador.gastar_recurso(custo)

        efeito = ataque.get("efeito")

        # Ataque de cura (Mago)
        if efeito == "cura":
            qtd = int(self.jogador.dano_total * ataque["mult"])
            curado = self.jogador.curar(qtd)
            self.gj.log(f"  + Você conjura {ataque['nome']} e recupera {curado} de HP.", "cura")
            self._pos_acao_jogador()
            return

        # Postura defensiva (Cavaleiro: Provocar)
        if efeito == "defesa_buff":
            self.jogador_defendendo = True
            self.gj.log("  # Você provoca o inimigo e assume postura defensiva.", "sistema")

        # Cálculo de dano ofensivo
        crit_chance = self.jogador.crit + ataque.get("crit_bonus", 0)
        ignora = efeito == "ignora_defesa"

        # Verifica evasão do inimigo
        if random.random() < self.inimigo.evasao:
            self.gj.log(f"  x {self.inimigo.nome} esquivou de {ataque['nome']}!", "sistema")
        else:
            dano, crit = self._calc_dano(
                self.jogador.dano_total, ataque["mult"], crit_chance,
                self.inimigo.defesa_total, ignora_def=ignora,
            )
            self.inimigo.hp -= dano
            if crit:
                self.gj.log(f"  > CRÍTICO! {ataque['nome']} causa {dano} de dano!", "crit")
            else:
                self.gj.log(f"  > {ataque['nome']} causa {dano} de dano.", "dano")
            # Efeito de gelo: dano contínuo de frio sobre o inimigo
            if efeito == "gelo":
                self.inimigo.dot_turnos = 3
                self.inimigo.dot_dano = max(4, self.jogador.dano_total // 4)
                self.gj.log("  * O alvo é enregelado: sofrerá dano de frio por 3 turnos.", "dano")

        self._pos_acao_jogador()

    def jogador_defende(self):
        if self.terminado:
            return
        self.jogador_defendendo = True
        regen = int(self.jogador.recurso_max * DEFEND_REGEN_FRAC)
        self.jogador.restaurar_recurso(regen)
        self.gj.log(f"  # Você se defende (dano reduzido) e recupera {regen} de {self.jogador.nome_recurso}.", "sistema")
        self._pos_acao_jogador()

    def jogador_usa_item(self, item):
        if self.terminado:
            return
        if item not in self.jogador.inventario:
            return
        # Não desperdiça item/turno se não houver efeito (HP/recurso cheios, sem veneno).
        if not item_tera_efeito(self.jogador, item):
            self.gj.log(f"  x {item.nome} não teria efeito agora.", "sistema")
            self.gj.render_combate(self)   # não consome o turno
            return
        ef = item.efeito
        if ef.get("antidoto"):
            self.jogador.veneno = 0
            self.gj.log("  + Antídoto usado: veneno neutralizado.", "cura")
        if "cura" in ef:
            curado = self.jogador.curar(ef["cura"])
            self.gj.log(f"  + {item.nome}: +{curado} de HP.", "cura")
        if "recurso" in ef:
            self.jogador.restaurar_recurso(ef["recurso"])
            self.gj.log(f"  + {item.nome}: +{ef['recurso']} de {self.jogador.nome_recurso}.", "cura")
        self.jogador.inventario.remove(item)
        self._pos_acao_jogador()

    def jogador_captura(self, usou_esfera=False):
        """Chance de captura baseada no HP restante do alvo.
        HP cheio -> ~5%; HP crítico -> ~80%. Esfera de selamento dá bônus.
        Chefes não podem ser capturados (e a tentativa NÃO gasta o turno)."""
        if self.terminado:
            return
        if self.inimigo.chefe:
            self.gj.log("  x Criaturas tão poderosas não podem ser capturadas!", "sistema")
            self.gj.render_combate(self)   # não consome o turno
            return

        chance = self.chance_captura(usou_esfera)

        if random.random() < chance:
            self.terminado = True
            self.jogador.aliados.append({
                "nome": self.inimigo.nome,
                "dano": max(4, self.inimigo.dano // 2),
                "hp": self.inimigo.hp_max,
                "hp_max": self.inimigo.hp_max,
            })
            self.gj.log(f"  * Sucesso! {self.inimigo.nome} (chance {int(chance*100)}%) juntou-se a você!", "heroi")
            self.gj.fim_combate("captura")
        else:
            self.gj.log(f"  x A captura falhou (chance era {int(chance*100)}%). O alvo resiste!", "sistema")
            self._pos_acao_jogador()

    def jogador_foge(self):
        if self.terminado:
            return
        # Não há como fugir da batalha final: o dragão bloqueia toda a saída.
        if self.inimigo.chefe:
            self.gj.log("  x Não há para onde fugir — o dragão bloqueia toda a saída!", "sistema")
            self.gj.render_combate(self)   # não consome o turno
            return
        chance = FUGA_CHANCE_NORMAL
        if random.random() < chance:
            self.terminado = True
            self.gj.log("  > Você conseguiu fugir do combate!", "sistema")
            self.gj.fim_combate("fuga")
        else:
            self.gj.log("  x A fuga falhou! O inimigo bloqueia sua saída.", "sistema")
            self._pos_acao_jogador()

    # --- Encadeamento de turnos --------------------------------------
    def _pos_acao_jogador(self):
        """Executado após cada ação do jogador: aliados atacam, dano contínuo,
        checa fim, depois o inimigo age."""
        if self.terminado:
            return

        # Aliados (vivos) atacam.
        for aliado in self.jogador.aliados:
            if not self.inimigo.esta_vivo():
                break
            dano = max(1, aliado["dano"] - self.inimigo.defesa_total // 2)
            self.inimigo.hp -= dano
            self.gj.log(f"  > Seu aliado {aliado['nome']} ataca por {dano}.", "dano")

        # Dano contínuo de frio (gelo) sobre o inimigo.
        if self.inimigo.dot_turnos > 0 and self.inimigo.esta_vivo():
            self.inimigo.hp -= self.inimigo.dot_dano
            self.inimigo.dot_turnos -= 1
            self.gj.log(f"  * O frio corrói {self.inimigo.nome} (+{self.inimigo.dot_dano} de dano).", "dano")

        if not self.inimigo.esta_vivo():
            self._vitoria()
            return

        self._turno_inimigo()

        if self.terminado:
            return

        self.turno += 1
        self.gj.log(f"  · · · turno {self.turno} · · ·", "sistema")
        self.gj.render_combate(self)

    def _turno_inimigo(self):
        """O inimigo ataca o jogador (ou um aliado)."""
        # Veneno atuando sobre o jogador (dano contínuo).
        if self.jogador.veneno > 0:
            dano_veneno = 4 + self.inimigo.nivel
            self.jogador.hp -= dano_veneno
            self.jogador.veneno -= 1
            self.gj.log(f"  ! Veneno causa {dano_veneno} de dano a você.", "dano")
            if not self.jogador.esta_vivo():
                self._derrota()
                return

        # O inimigo pode mirar num aliado em vez de você.
        if self.jogador.aliados and random.random() < ALIADO_ALVO_CHANCE:
            alvo = random.choice(self.jogador.aliados)
            dano, crit = self._calc_dano(self.inimigo.dano, 1.0, self.inimigo.crit, 0)
            alvo["hp"] -= dano
            marca = "CRÍTICO! " if crit else ""
            self.gj.log(f"  * {marca}{self.inimigo.nome} ataca {alvo['nome']} por {dano}.", "dano")
            if alvo["hp"] <= 0:
                self.gj.log(f"  ! Seu aliado {alvo['nome']} caiu em combate!", "vilao")
                self.jogador.aliados = [a for a in self.jogador.aliados if a["hp"] > 0]
            self.jogador_defendendo = False
            return

        # Verifica evasão do jogador.
        if random.random() < self.jogador.evasao:
            self.gj.log(f"  * Você esquiva do ataque de {self.inimigo.nome}!", "sistema")
        else:
            dano, crit = self._calc_dano(
                self.inimigo.dano, 1.0, self.inimigo.crit, self.jogador.defesa_total,
            )
            if self.jogador_defendendo:
                dano = max(1, int(dano * DEFESA_REDUCAO))
            self.jogador.hp -= dano
            if crit:
                self.gj.log(f"  * CRÍTICO! {self.inimigo.nome} causa {dano} de dano!", "crit")
            else:
                self.gj.log(f"  * {self.inimigo.nome} causa {dano} de dano.", "dano")

            # Inimigo pode aplicar veneno.
            if self.inimigo.veneno and random.random() < self.inimigo.veneno:
                self.jogador.veneno = 3
                self.gj.log("  ! Você foi envenenado!", "sistema")

        self.jogador_defendendo = False   # buff de defesa dura um turno

        if not self.jogador.esta_vivo():
            self._derrota()

    # --- Fim de combate ----------------------------------------------
    def _vitoria(self):
        self.terminado = True
        self.jogador.veneno = 0
        self.gj.log(f"\n  * {self.inimigo.nome} foi derrotado!", "heroi")
        niveis = self.jogador.ganhar_xp(self.inimigo.xp)
        self.gj.log(f"  + {self.inimigo.xp} XP.", "sistema")
        if niveis:
            self.gj.log(f"  * Você subiu para o nível {self.jogador.nivel}! "
                        f"(+{niveis*GANHO_NIVEL['pontos_atributo']} pontos de atributo)", "heroi")
        # Drop de loot
        self.gj.dropar_loot(self.inimigo)
        self.gj.fim_combate("vitoria")

    def _derrota(self):
        self.terminado = True
        self.jogador.veneno = 0
        self.gj.fim_combate("derrota")

# === HISTORIA ===

class Historia:
    """Contém todos os nós narrativos e a lógica de ramificação.

    Cada nó: {"texto": str, "escolhas": [escolha, ...]}
    Cada escolha pode conter:
        label          -> texto do botão
        destino        -> próximo nó
        karma          -> +/- pontos de alinhamento
        combate        -> dict {"tipo": str}, {"chefe": True} ou {"aleatorio": True}
        loot/pocao     -> concede itens
        aliado         -> nome de um aliado narrativo
        requer_karma   -> (operador, valor) p/ mostrar a escolha condicionalmente
        requer_flag    -> nome (ou lista de nomes) de flag(s) necessária(s)
        set_flag       -> registra um marco na jornada (ex.: fragmento coletado)
        final          -> True se for um nó de final
    """

    def __init__(self):
        self.nos = self._construir_historia()

    def get(self, chave):
        return self.nos.get(chave)

    def _construir_historia(self):
        return {
            # =========================================================
            #  ATO I — A VILA DE PEDRAVALE
            # =========================================================
            "inicio": {
                "texto": (
                    "As Crônicas de Pedravale começam.\n\n"
                    "Você chega à pequena vila de Pedravale ao entardecer. Fumaça sobe das "
                    "casas de pedra e os aldeões correm assustados: monstros das Cavernas de "
                    "Veludo voltaram a atacar, e o velho prefeito Aldric implora por ajuda.\n\n"
                    "Dizem que o dragão Vorthak, outrora guardião destas terras, foi corrompido "
                    "por uma relíquia maldita — e que apenas reunindo os três Fragmentos da "
                    "Aurora alguém poderia desfazer o mal pela raiz.\n\n"
                    "Mas isso é lenda. Por ora, um goblin desgarrado avança pela praça em sua "
                    "direção."
                ),
                "escolhas": [
                    {"label": "Proteger os aldeões e enfrentar o goblin", "karma": 2,
                     "combate": {"tipo": "Goblin"}, "destino": "apos_goblin"},
                    {"label": "Exigir ouro antes de mover um dedo", "karma": -2,
                     "destino": "exigir_ouro"},
                    {"label": "Ignorar tudo e seguir direto para as cavernas", "karma": 0,
                     "destino": "entrada_caverna"},
                ],
            },
            "exigir_ouro": {
                "texto": (
                    "Você cruza os braços e exige pagamento. O prefeito Aldric, indignado, "
                    "atira uma bolsa de moedas a seus pés — e com ela, um item esquecido de "
                    "um antigo herói.\n\n"
                    "Enquanto isso, o goblin ataca de qualquer forma."
                ),
                "escolhas": [
                    {"label": "Pegar o saque e lutar contra o goblin", "loot": True,
                     "combate": {"tipo": "Goblin"}, "destino": "apos_goblin"},
                ],
            },
            "apos_goblin": {
                "texto": (
                    "Com o goblin caído, os aldeões observam você com esperança. Aldric explica "
                    "que a fonte do mal está nas Cavernas de Veludo, mas adverte: ninguém que "
                    "partiu apressado jamais voltou. 'Prepare-se na vila primeiro', diz ele, "
                    "oferecendo algo de seu velho arsenal."
                ),
                "escolhas": [
                    {"label": "Aceitar uma arma do arsenal", "loot": "arma",
                     "destino": "vila_hub"},
                    {"label": "Aceitar uma armadura do arsenal", "loot": "armadura",
                     "destino": "vila_hub"},
                    {"label": "Recusar — você não precisa de presentes", "karma": 1,
                     "destino": "vila_hub"},
                ],
            },
            "vila_hub": {
                "texto": (
                    "A praça de Pedravale se abre diante de você. A taverna do Javali Dourado "
                    "ferve de conversas; a forja de Mestre Bran cospe faíscas; e, no alto da "
                    "colina, o sino do Templo da Aurora dobra suave.\n\n"
                    "Para onde você vai antes de partir em jornada?"
                ),
                "escolhas": [
                    {"label": "Entrar na Taverna do Javali Dourado", "destino": "taverna"},
                    {"label": "Visitar a Forja de Mestre Bran", "destino": "forja"},
                    {"label": "Subir ao Templo da Aurora", "destino": "templo"},
                    {"label": "Partir para a encruzilhada e iniciar a jornada",
                     "destino": "encruzilhada"},
                ],
            },
            "taverna": {
                "texto": (
                    "Dentro da taverna, o calor da lareira afasta o frio. No balcão, a "
                    "mercenária Selene afia uma adaga; numa mesa, marinheiros apostam em dados. "
                    "O taverneiro limpa uma caneca e ergue a sobrancelha para você."
                ),
                "escolhas": [
                    {"label": "Pagar uma rodada e ouvir os rumores", "destino": "taverna_rumor"},
                    {"label": "Convencer Selene a juntar-se a você", "karma": 1,
                     "aliado": "Selene, a Mercenária", "destino": "vila_hub"},
                    {"label": "Trapacear no jogo de dados", "karma": -2, "loot": True,
                     "destino": "vila_hub"},
                    {"label": "Sair da taverna", "destino": "vila_hub"},
                ],
            },
            "taverna_rumor": {
                "texto": (
                    "Entre goles, um velho bardo se inclina: 'A relíquia que corrompeu Vorthak "
                    "veio do fundo das Cavernas. Mas há quem diga que, espalhados pelo mundo, "
                    "restam três Fragmentos da Aurora — no pântano afogado, nas montanhas "
                    "geladas e no saber de um feiticeiro preso em Aldoria. Reúna-os, e a relíquia "
                    "poderá ser desfeita... ou refeita.'\n\n"
                    "Ele aceita uma poção como agradecimento e a entrega a você."
                ),
                "escolhas": [
                    {"label": "Agradecer ao bardo e voltar à praça", "pocao": "cura",
                     "destino": "vila_hub"},
                ],
            },
            "forja": {
                "texto": (
                    "Mestre Bran ergue o martelo sobre a bigorna em brasa. 'Aço de Pedravale "
                    "não se dobra fácil', resmunga. 'Mas para quem vai encarar Vorthak... posso "
                    "abrir uma exceção.'"
                ),
                "escolhas": [
                    {"label": "Aceitar uma lâmina recém-forjada", "loot": "arma",
                     "destino": "vila_hub"},
                    {"label": "Aceitar uma armadura reforçada", "loot": "armadura",
                     "destino": "vila_hub"},
                    {"label": "Roubar o aço enquanto Bran se distrai", "karma": -3,
                     "loot": True, "destino": "vila_hub"},
                    {"label": "Agradecer e voltar", "destino": "vila_hub"},
                ],
            },
            "templo": {
                "texto": (
                    "No alto da colina, o Templo da Aurora guarda velas e silêncio. Uma "
                    "sacerdotisa de mãos enrugadas observa você se aproximar do altar dourado."
                ),
                "escolhas": [
                    {"label": "Rezar pela bênção da Aurora", "karma": 1, "pocao": "cura_g",
                     "destino": "vila_hub"},
                    {"label": "(Herói) Deixar uma oferenda generosa", "requer_karma": (">=", 3),
                     "karma": 1, "pocao": "antidoto", "destino": "vila_hub"},
                    {"label": "Saquear as oferendas do altar", "karma": -3, "loot": True,
                     "destino": "vila_hub"},
                    {"label": "Descer de volta à praça", "destino": "vila_hub"},
                ],
            },
            # =========================================================
            #  ATO II — A ENCRUZILHADA E AS QUATRO ESTRADAS
            # =========================================================
            "encruzilhada": {
                "texto": (
                    "Na saída da vila, quatro caminhos se abrem. À esquerda, a Floresta "
                    "Sussurrante. Ao norte, o Pântano dos Afogados, onde a névoa nunca dorme. "
                    "Mais além, o Passo da Montanha leva às terras geladas e ao Reino de "
                    "Aldoria. À frente, a boca escura das Cavernas de Veludo.\n\n"
                    "Você também pode vagar pelos arredores para treinar antes de seguir."
                ),
                "escolhas": [
                    {"label": "Vagar pelos arredores em busca de batalhas (treinar)",
                     "destino": "explorar"},
                    {"label": "Atravessar a Floresta Sussurrante", "destino": "floresta"},
                    {"label": "Entrar no Pântano dos Afogados", "destino": "pantano"},
                    {"label": "Subir o Passo da Montanha", "destino": "montanha"},
                    {"label": "Seguir pela estrada direta a Aldoria", "destino": "reino"},
                    {"label": "Entrar nas Cavernas de Veludo", "destino": "entrada_caverna"},
                ],
            },
            "explorar": {
                "texto": (
                    "Você percorre as trilhas ao redor de Pedravale. O mato range, e há "
                    "sempre algo à espreita disposto a testar sua lâmina."
                ),
                "escolhas": [
                    {"label": "Procurar uma criatura para enfrentar",
                     "combate": {"aleatorio": True}, "destino": "explorar", "repetivel": True},
                    {"label": "Voltar à encruzilhada", "destino": "encruzilhada"},
                ],
            },
            # ----- Floresta Sussurrante -----
            "floresta": {
                "texto": (
                    "A floresta é densa e úmida. Entre as árvores, você encontra um lobo "
                    "ferido preso numa armadilha de caçadores. Ele rosna, mas há dor — e algo "
                    "quase humano — em seus olhos."
                ),
                "escolhas": [
                    {"label": "Libertar o lobo com cuidado", "karma": 2,
                     "destino": "floresta_liberta"},
                    {"label": "Abatê-lo por segurança", "karma": -1,
                     "combate": {"tipo": "Lobo"}, "destino": "floresta_profunda"},
                    {"label": "Tentar capturá-lo em combate", "karma": 0,
                     "combate": {"tipo": "Lobo"}, "destino": "floresta_profunda"},
                ],
            },
            "floresta_liberta": {
                "texto": (
                    "Você liberta o lobo. Em vez de fugir, ele se curva — e decide seguir você. "
                    "Um aliado leal se junta à sua jornada e o guia para o coração da floresta."
                ),
                "escolhas": [
                    {"label": "Seguir mais fundo com o Lobo Leal", "aliado": "Lobo Leal",
                     "destino": "floresta_profunda"},
                ],
            },
            "floresta_profunda": {
                "texto": (
                    "No coração da Floresta Sussurrante, a luz mal penetra. Você percebe duas "
                    "presenças antigas: a cabana torta da bruxa Morgana, de onde sobe uma fumaça "
                    "esverdeada, e uma clareira onde brilha uma fonte feérica de água prateada."
                ),
                "escolhas": [
                    {"label": "Procurar a bruxa Morgana", "destino": "bruxa"},
                    {"label": "Aproximar-se da fonte feérica", "destino": "fonte_feerica"},
                    {"label": "Cortar caminho rumo a Aldoria", "destino": "reino"},
                ],
            },
            "bruxa": {
                "texto": (
                    "Morgana sorri sem dentes. 'Todo poder tem seu preço, andarilho. Posso "
                    "lhe dar um presente sombrio... se aceitar carregar um pouco da minha "
                    "maldição. Ou prefere ir embora de mãos vazias?'"
                ),
                "escolhas": [
                    {"label": "Aceitar o pacto sombrio", "karma": -2, "loot": True,
                     "destino": "floresta_profunda"},
                    {"label": "Recusar e pedir apenas um remédio", "pocao": "cura_g",
                     "destino": "floresta_profunda"},
                    {"label": "Atacar a bruxa e seu servo morto-vivo",
                     "combate": {"tipo": "Esqueleto"}, "karma": 1,
                     "destino": "floresta_profunda"},
                ],
            },
            "fonte_feerica": {
                "texto": (
                    "A água da fonte canta baixinho. Pequenas luzes dançam sobre ela — espíritos "
                    "da mata, curiosos com sua presença. Eles esperam para ver que tipo de "
                    "pessoa você é."
                ),
                "escolhas": [
                    {"label": "(Herói) Pedir a bênção e a companhia da mata",
                     "requer_karma": (">=", 3), "karma": 1, "aliado": "Espírito da Mata",
                     "destino": "fonte_bencao"},
                    {"label": "Beber da água curativa", "pocao": "cura_g",
                     "destino": "floresta_profunda"},
                    {"label": "Profanar a fonte e roubar seu cristal", "karma": -3,
                     "loot": True, "destino": "floresta_profunda"},
                ],
            },
            "fonte_bencao": {
                "texto": (
                    "As luzes envolvem você num calor sereno. Um Espírito da Mata jura segui-lo, "
                    "e a fonte sussurra um segredo: 'O pântano guarda o primeiro Fragmento da "
                    "Aurora. Procure o altar afogado.'"
                ),
                "escolhas": [
                    {"label": "Seguir, agradecido, rumo a Aldoria", "destino": "reino"},
                    {"label": "Voltar e explorar o pântano", "destino": "pantano"},
                ],
            },
            # ----- Pântano dos Afogados -----
            "pantano": {
                "texto": (
                    "O Pântano dos Afogados engole seus passos. Bolhas estouram na água lodosa "
                    "e limos venenosos se contorcem entre as raízes. No meio da névoa, você "
                    "vislumbra uma estrutura de pedra meio submersa: um altar antigo."
                ),
                "escolhas": [
                    {"label": "Investigar o altar afogado", "destino": "altar_afogado"},
                    {"label": "Enfrentar os limos venenosos", "combate": {"tipo": "Slime"},
                     "destino": "pantano_fundo"},
                    {"label": "Recuar para a encruzilhada", "destino": "encruzilhada"},
                ],
            },
            "altar_afogado": {
                "texto": (
                    "Sobre o altar encharcado repousa um caco de cristal que pulsa com luz "
                    "dourada e fria: o PRIMEIRO FRAGMENTO DA AURORA. Símbolos esquecidos "
                    "advertem que reuni-los pode desfazer qualquer relíquia — para o bem ou "
                    "para o mal."
                ),
                "escolhas": [
                    {"label": "Recolher o Fragmento da Aurora", "set_flag": "frag_pantano",
                     "karma": 1, "destino": "pantano_fundo"},
                    {"label": "Deixá-lo onde está e seguir", "destino": "pantano_fundo"},
                ],
            },
            "pantano_fundo": {
                "texto": (
                    "Mais adiante, um troll do brejo guarda a única saída firme do pântano, "
                    "afundado até os joelhos na lama. Não há como contorná-lo."
                ),
                "escolhas": [
                    {"label": "Enfrentar o troll do brejo", "combate": {"tipo": "Troll"},
                     "loot": True, "destino": "encruzilhada"},
                    {"label": "Atraí-lo para o atoleiro e fugir", "karma": 0,
                     "destino": "encruzilhada"},
                ],
            },
            # ----- Passo da Montanha -----
            "montanha": {
                "texto": (
                    "O Passo da Montanha é uma fita de pedra sobre o abismo, batida por vento "
                    "gelado. Flocos de neve cortam o ar. No meio da ponte antiga, um vulto "
                    "imóvel jaz contra o parapeito — uma armadura coberta de gelo."
                ),
                "escolhas": [
                    {"label": "Examinar o cavaleiro caído", "destino": "cavaleiro_caido"},
                    {"label": "Atravessar a ponte depressa", "destino": "desfiladeiro"},
                ],
            },
            "cavaleiro_caido": {
                "texto": (
                    "Sob o gelo, um cavaleiro de Aldoria abraça, mesmo na morte, um caco "
                    "luminoso: o SEGUNDO FRAGMENTO DA AURORA. Ao seu lado, a armadura ainda "
                    "intacta poderia servir a você."
                ),
                "escolhas": [
                    {"label": "Honrar o morto e recolher o Fragmento", "karma": 1,
                     "set_flag": "frag_montanha", "destino": "desfiladeiro"},
                    {"label": "Tomar a armadura do cavaleiro", "loot": "armadura",
                     "set_flag": "frag_montanha", "destino": "desfiladeiro"},
                    {"label": "Saquear tudo e cuspir sobre o corpo", "karma": -2,
                     "loot": True, "set_flag": "frag_montanha", "destino": "desfiladeiro"},
                ],
            },
            "desfiladeiro": {
                "texto": (
                    "No fim da ponte, um orc das montanhas barra a passagem, rugindo contra o "
                    "vento. Atrás dele, lá embaixo no vale, brilham os telhados dourados de "
                    "Aldoria."
                ),
                "escolhas": [
                    {"label": "Enfrentar o orc das montanhas", "combate": {"tipo": "Orc"},
                     "destino": "reino"},
                    {"label": "Descer pela trilha lateral, evitando-o", "karma": 0,
                     "destino": "reino"},
                ],
            },
            # ----- Reino de Aldoria -----
            "reino": {
                "texto": (
                    "Os portões dourados de Aldoria se abrem. A Rainha Lysandra recebe você no "
                    "salão do trono. Ela explica que o dragão Vorthak foi outrora um guardião, "
                    "corrompido pela relíquia sombria. Nas masmorras, um feiticeiro afirma "
                    "saber como desfazê-la — e, no pátio, a arena real oferece glória e "
                    "recompensas a quem provar seu valor."
                ),
                "escolhas": [
                    {"label": "Pedir clemência ao feiticeiro e ouvi-lo", "karma": 2,
                     "destino": "feiticeiro_aliado"},
                    {"label": "Ameaçar o feiticeiro para extrair a verdade", "karma": -2,
                     "destino": "feiticeiro_ameaca"},
                    {"label": "Provar seu valor na arena real", "destino": "arena"},
                    {"label": "Roubar a coroa da rainha enquanto ela fala", "karma": -3,
                     "combate": {"tipo": "Esqueleto"}, "destino": "entrada_caverna"},
                    {"label": "(Herói) Receber a Bênção de Aldoria da rainha",
                     "requer_karma": (">=", 5), "pocao": "cura_g", "karma": 1,
                     "destino": "entrada_caverna"},
                ],
            },
            "arena": {
                "texto": (
                    "A arena ruge. Areia, sol e o clangor de armas. O mestre de cerimônias "
                    "anuncia seu nome e solta o desafiante: um campeão esqueleto erguido por "
                    "necromancia para nunca cansar."
                ),
                "escolhas": [
                    {"label": "Lutar pela glória de Aldoria", "combate": {"tipo": "Esqueleto"},
                     "karma": 1, "destino": "arena_vitoria"},
                    {"label": "Desistir e voltar ao salão", "destino": "reino"},
                ],
            },
            "arena_vitoria": {
                "texto": (
                    "A multidão grita seu nome! A rainha, impressionada, ordena que lhe "
                    "entreguem um prêmio digno do arsenal real antes de você partir para as "
                    "cavernas."
                ),
                "escolhas": [
                    {"label": "Receber o prêmio e seguir às cavernas", "loot": True,
                     "destino": "entrada_caverna"},
                    {"label": "Voltar ao salão do trono", "destino": "reino"},
                ],
            },
            "feiticeiro_aliado": {
                "texto": (
                    "O feiticeiro Eldrin, grato pela clemência, revela o ritual e lhe entrega "
                    "uma poção poderosa. 'Há um TERCEIRO Fragmento da Aurora', sussurra, 'e ele "
                    "não é de pedra — é conhecimento. Eu o entrego a você agora.' Ele jura "
                    "proteger o reino enquanto você parte."
                ),
                "escolhas": [
                    {"label": "Aceitar a poção e o saber, e partir", "pocao": "cura_g",
                     "set_flag": "frag_saber", "destino": "entrada_caverna"},
                ],
            },
            "feiticeiro_ameaca": {
                "texto": (
                    "Sob ameaça, o feiticeiro cospe a informação — mas também uma maldição. "
                    "Você arranca o conhecimento do Terceiro Fragmento, porém a guarda real "
                    "passa a desconfiar de você. Um esqueleto guardião desperta na masmorra."
                ),
                "escolhas": [
                    {"label": "Lutar contra o guardião e seguir", "karma": -1,
                     "combate": {"tipo": "Esqueleto"}, "set_flag": "frag_saber",
                     "destino": "entrada_caverna"},
                ],
            },
            # =========================================================
            #  ATO III — AS CAVERNAS DE VELUDO
            # =========================================================
            "entrada_caverna": {
                "texto": (
                    "As Cavernas de Veludo exalam um frio antinatural. Cristais negros pulsam "
                    "nas paredes. Dois caminhos descem: uma galeria estreita guardada por um "
                    "orc das profundezas, e uma passagem úmida de onde vem o eco de água — um "
                    "lago subterrâneo."
                ),
                "escolhas": [
                    {"label": "Enfrentar o orc na galeria", "combate": {"tipo": "Orc"},
                     "destino": "pre_chefe"},
                    {"label": "Descer até o lago subterrâneo", "destino": "lago_subterraneo"},
                    {"label": "Tentar passar furtivamente pela galeria", "karma": 0,
                     "destino": "furtividade"},
                ],
            },
            "furtividade": {
                "texto": (
                    "Você tenta se esgueirar... mas tropeça num crânio. O orc desperta furioso "
                    "e ainda chama um troll das cavernas! Você terá de lutar."
                ),
                "escolhas": [
                    {"label": "Lutar contra o troll", "combate": {"tipo": "Troll"},
                     "destino": "pre_chefe"},
                ],
            },
            "lago_subterraneo": {
                "texto": (
                    "Um lago negro e imóvel reflete cristais bioluminescentes. No centro, sobre "
                    "uma ilhota, repousa um pedestal vazio — e do fundo das águas sobe um "
                    "sussurro: a própria relíquia sombria chama por você, prometendo poder."
                ),
                "escolhas": [
                    {"label": "Ouvir o que a relíquia sussurra", "destino": "reliquia_sussurra"},
                    {"label": "Ignorar a voz e subir para a galeria", "destino": "entrada_caverna"},
                    {"label": "Seguir direto para o covil do dragão", "destino": "pre_chefe"},
                ],
            },
            "reliquia_sussurra": {
                "texto": (
                    "A voz se enrosca em seus pensamentos. 'Os Fragmentos da Aurora podem me "
                    "destruir... ou podem me REFAZER em algo ainda maior, nas mãos certas.' "
                    "Ela revela a verdade do ritual — e cabe a você decidir o que fará com "
                    "esse conhecimento."
                ),
                "escolhas": [
                    {"label": "Aceitar a verdade sem se deixar tentar", "karma": 1,
                     "set_flag": "verdade", "destino": "lago_subterraneo"},
                    {"label": "Saborear a promessa de poder", "karma": -2,
                     "set_flag": "verdade", "destino": "lago_subterraneo"},
                ],
            },
            "pre_chefe": {
                "texto": (
                    "Você alcança uma vasta câmara. No centro, sobre montanhas de ouro, "
                    "repousa a relíquia sombria — e acima dela, os olhos flamejantes do "
                    "Dragão Vorthak se abrem.\n\n"
                    "Esta é a batalha final. Prepare-se."
                ),
                "escolhas": [
                    {"label": "Usar este momento para descansar e curar (poção grátis)",
                     "pocao": "cura", "destino": "pre_chefe2"},
                    {"label": "Atacar imediatamente, sem hesitar", "karma": 1,
                     "destino": "pre_chefe2"},
                ],
            },
            "pre_chefe2": {
                "texto": "O dragão ruge. O chão treme. Avance.",
                "escolhas": [
                    {"label": "> ENFRENTAR O DRAGÃO VORTHAK", "combate": {"chefe": True},
                     "destino": "decisao_final"},
                ],
            },
            # =========================================================
            #  DESFECHO — A DECISÃO FINAL
            # =========================================================
            "decisao_final": {
                "texto": (
                    "Vorthak cai, exausto. A relíquia sombria fica exposta, pulsando com poder "
                    "imenso. O dragão, agora livre da corrupção, implora: 'Destrua a relíquia... "
                    "ou tome o poder para si.'\n\n"
                    "Esta é sua decisão final — e ela definirá quem você se tornou. Dizem que "
                    "apenas os de coração verdadeiramente puro, os já perdidos nas trevas, ou "
                    "aqueles que reuniram os três Fragmentos da Aurora enxergam certos caminhos."
                ),
                "escolhas": [
                    {"label": "Destruir a relíquia e libertar a terra", "karma": 4,
                     "destino": "final_heroi"},
                    {"label": "Tomar o poder da relíquia para si", "karma": -4,
                     "destino": "final_vilao"},
                    {"label": "Deixar a relíquia selada e partir sem usá-la", "karma": 0,
                     "destino": "final_neutro"},
                    {"label": "(Herói lendário) Canalizar a luz que acumulou e purificar tudo",
                     "requer_karma": (">=", 5), "karma": 1, "destino": "final_heroi"},
                    {"label": "(Vilão temível) Fundir-se à relíquia e ascender como tirano",
                     "requer_karma": ("<=", -5), "karma": -1, "destino": "final_vilao"},
                    {"label": "(* Fragmentos da Aurora *) Forjar a Relíquia da Aurora e "
                              "refazer o pacto dos guardiões",
                     "requer_flag": ["frag_pantano", "frag_montanha", "frag_saber"],
                     "destino": "final_guardiao"},
                ],
            },
            "final_heroi": {
                "texto": (
                    "* FINAL HERÓICO *\n\n"
                    "Você esmaga a relíquia. A luz volta às Cavernas de Veludo e Vorthak, "
                    "redimido, jura proteger Pedravale. Aldeões erguem estátuas em sua honra. "
                    "Seu nome é lembrado por gerações como o Salvador de Pedravale.\n\n"
                    "Fim. Obrigado por jogar!"
                ),
                "escolhas": [], "final": True,
            },
            "final_vilao": {
                "texto": (
                    "! FINAL SOMBRIO !\n\n"
                    "Você absorve o poder da relíquia. Energia obscura percorre suas veias. "
                    "Os reinos tremem diante de seu novo trono de ossos. Pedravale arde, e você "
                    "reina como o Senhor das Cavernas. Ninguém ousa desafiá-lo.\n\n"
                    "Fim. Obrigado por jogar!"
                ),
                "escolhas": [], "final": True,
            },
            "final_neutro": {
                "texto": (
                    "* FINAL AMBÍGUO *\n\n"
                    "Você sela a relíquia e parte em silêncio. A terra fica em paz frágil — "
                    "ninguém sabe seu nome, mas as cavernas dormem novamente. Sua jornada "
                    "continua, em algum lugar além do horizonte.\n\n"
                    "Fim. Obrigado por jogar!"
                ),
                "escolhas": [], "final": True,
            },
            "final_guardiao": {
                "texto": (
                    "*** FINAL SECRETO — O GUARDIÃO DA AURORA ***\n\n"
                    "Os três Fragmentos da Aurora se erguem de suas mãos e se fundem em torno "
                    "da relíquia sombria, dobrando-a à luz. Onde havia maldição, nasce um pacto: "
                    "Vorthak desperta renovado e ajoelha-se ao seu lado, não como servo, mas "
                    "como igual.\n\n"
                    "Você não destrói nem domina o poder — você o GUARDA. Pedravale, Aldoria, a "
                    "floresta, o pântano e as montanhas florescem sob a vigília eterna do "
                    "Guardião e seu dragão. Bardos cantarão esta lenda enquanto houver quem "
                    "ouça.\n\n"
                    "Fim. Você encontrou o caminho que poucos enxergam. Obrigado por jogar!"
                ),
                "escolhas": [], "final": True,
            },
        }
