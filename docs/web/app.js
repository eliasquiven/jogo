const SAVE_VERSION = 2;
const SAVE_KEY = "cronicas_pedravale_save";

function webPath(path) {
  return new URL(path, import.meta.url).toString();
}

function assetPath(path) {
  return new URL(`../assets/${path}`, import.meta.url).toString();
}

const RARIDADES = {
  "Comum": 1.0,
  "Raro": 1.4,
  "Épico": 1.9,
  "Lendário": 2.5,
};

const PESOS_RARIDADE = {
  "Comum": 62,
  "Raro": 27,
  "Épico": 9,
  "Lendário": 2,
};

const DIFICULDADES = {
  "Fácil": { inimigo: 0.88, desc: "Inimigos mais fracos. Bom para a história." },
  "Normal": { inimigo: 1.0, desc: "Experiência equilibrada." },
  "Difícil": { inimigo: 1.13, desc: "Inimigos mais perigosos." },
};

const CLASSES = {
  "Cavaleiro": {
    descricao: "Tanque corpo a corpo. HP alto, defesa alta, usa Vigor.",
    hp: 120,
    recurso: 50,
    nome_recurso: "Vigor",
    dano: 12,
    defesa: 12,
    crit: 0.08,
    evasao: 0.05,
  },
  "Mago": {
    descricao: "Dano mágico alto, HP baixo, usa MP.",
    hp: 80,
    recurso: 100,
    nome_recurso: "MP",
    dano: 18,
    defesa: 5,
    crit: 0.1,
    evasao: 0.08,
  },
  "Arqueiro": {
    descricao: "Ágil, crítico alto, usa Energia.",
    hp: 95,
    recurso: 70,
    nome_recurso: "Energia",
    dano: 15,
    defesa: 7,
    crit: 0.25,
    evasao: 0.18,
  },
};

const ATAQUES = {
  "Cavaleiro": [
    { nome: "Golpe Simples", custo: 0, mult: 1.0, desc: "Um golpe básico." },
    { nome: "Investida", custo: 10, mult: 1.3, desc: "Avança com força." },
    { nome: "Golpe Pesado", custo: 22, mult: 1.9, desc: "Golpe devastador." },
    { nome: "Provocar", custo: 6, mult: 0.6, efeito: "defesa_buff", desc: "Postura defensiva." },
  ],
  "Mago": [
    { nome: "Choque Arcano", custo: 0, mult: 0.9, desc: "Descarga arcana básica." },
    { nome: "Bola de Fogo", custo: 22, mult: 1.8, desc: "Alto dano." },
    { nome: "Lança de Gelo", custo: 16, mult: 1.3, efeito: "gelo", desc: "Causa dano contínuo." },
    { nome: "Cura", custo: 26, mult: 1.6, efeito: "cura", desc: "Restaura HP." },
  ],
  "Arqueiro": [
    { nome: "Tiro Rápido", custo: 0, mult: 0.95, desc: "Disparo simples." },
    { nome: "Flecha Precisa", custo: 10, mult: 1.2, crit_bonus: 0.2, desc: "Mais crítico." },
    { nome: "Chuva de Flechas", custo: 26, mult: 1.7, desc: "Salva de flechas." },
    { nome: "Tiro Perfurante", custo: 18, mult: 1.5, efeito: "ignora_defesa", desc: "Ignora defesa." },
  ],
};

const BESTIARIO = {
  "Slime": { hp: 30, dano: 7, defesa: 2, xp: 18, crit: 0.02, evasao: 0.02, veneno: 0.3 },
  "Goblin": { hp: 40, dano: 12, defesa: 3, xp: 26, crit: 0.06, evasao: 0.1, veneno: 0 },
  "Lobo": { hp: 52, dano: 18, defesa: 4, xp: 34, crit: 0.15, evasao: 0.18, veneno: 0 },
  "Esqueleto": { hp: 60, dano: 17, defesa: 7, xp: 40, crit: 0.08, evasao: 0.06, veneno: 0 },
  "Orc": { hp: 96, dano: 26, defesa: 9, xp: 60, crit: 0.09, evasao: 0.06, veneno: 0 },
  "Troll": { hp: 150, dano: 34, defesa: 12, xp: 95, crit: 0.08, evasao: 0.03, veneno: 0 },
};

const GANHO_NIVEL = { pontos_atributo: 3, hp_max: 12, recurso_max: 6, dano: 2, defesa: 1 };
const ATRIBUTO_GANHOS = { hp: 10, dano: 3, defesa: 2, recurso: 10 };
const PREFIXOS_INIMIGO = ["", "", "", "Feroz ", "Esfomeado ", "Ancião ", "Corrompido ", "Sombrio ", "das Cavernas "];
const NOMES_ARMA = {
  "Cavaleiro": ["Espada", "Machado", "Maça", "Lâmina", "Montante"],
  "Mago": ["Cajado", "Varinha", "Orbe", "Cetro", "Grimório"],
  "Arqueiro": ["Arco", "Besta", "Arco Longo", "Estilingue de Guerra"],
};
const NOMES_ARMADURA = ["Couraça", "Cota de Malha", "Túnica Encantada", "Peitoral", "Manto Reforçado"];

const CENARIO_NO = {
  inicio: "vila", exigir_ouro: "vila", apos_goblin: "vila", vila_hub: "vila",
  taverna: "vila", taverna_rumor: "vila", forja: "vila", templo: "vila",
  encruzilhada: "campo", explorar: "campo", floresta: "floresta",
  floresta_liberta: "floresta", floresta_profunda: "floresta", bruxa: "floresta",
  fonte_feerica: "floresta", fonte_bencao: "floresta", pantano: "campo",
  altar_afogado: "campo", pantano_fundo: "campo", montanha: "campo",
  cavaleiro_caido: "campo", desfiladeiro: "campo", reino: "vila", arena: "vila",
  arena_vitoria: "vila", feiticeiro_aliado: "vila", feiticeiro_ameaca: "vila",
  entrada_caverna: "caverna", furtividade: "caverna", lago_subterraneo: "caverna",
  reliquia_sussurra: "caverna", pre_chefe: "caverna", pre_chefe2: "covil",
  decisao_final: "covil", final_heroi: "amanhecer", final_vilao: "covil",
  final_neutro: "campo", final_guardiao: "amanhecer",
};

const BG_BY_SCENE = {
  vila: assetPath("vila.png"),
  floresta: assetPath("floresta.png"),
  caverna: assetPath("caverna_veludo.png"),
  covil: assetPath("covil.png"),
  campo: assetPath("mapa.jpg"),
  amanhecer: assetPath("titulo.jpg"),
  mapa: assetPath("mapa.jpg"),
  titulo: assetPath("titulo.jpg"),
};

const ENEMY_TILES = {
  Slime: [0, 9],
  Goblin: [1, 9],
};

const HERO_TILES = {
  Cavaleiro: [0, 8],
  Mago: [0, 7],
  Arqueiro: [4, 9],
};

const app = {
  story: {},
  player: null,
  currentNode: null,
  mode: "loading",
  combat: null,
  destinationAfterCombat: null,
  log: [],
  images: {},
  frame: 0,
};

const el = {
  canvas: document.querySelector("#scene"),
  status: document.querySelector("#status"),
  log: document.querySelector("#log"),
  controls: document.querySelector("#controls"),
  title: document.querySelector("#top-title"),
  subtitle: document.querySelector("#top-subtitle"),
  inventory: document.querySelector("#btn-inventory"),
  map: document.querySelector("#btn-map"),
  save: document.querySelector("#btn-save"),
};

const ctx = el.canvas.getContext("2d");

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function choice(list) {
  return list[Math.floor(Math.random() * list.length)];
}

function weightedChoice(weights) {
  const entries = Object.entries(weights);
  const total = entries.reduce((sum, [, weight]) => sum + weight, 0);
  let roll = Math.random() * total;
  for (const [name, weight] of entries) {
    roll -= weight;
    if (roll <= 0) return name;
  }
  return entries[0][0];
}

function hasOwn(obj, key) {
  return Object.prototype.hasOwnProperty.call(obj, key);
}

function itemValue(item) {
  return Math.round((item.valor_base || 0) * (RARIDADES[item.raridade] || 1));
}

function itemFullName(item) {
  if (item.tipo === "arma") return `[${item.raridade}] ${item.nome} (+${itemValue(item)} dano)`;
  if (item.tipo === "armadura") return `[${item.raridade}] ${item.nome} (+${itemValue(item)} def)`;
  return item.nome;
}

function sortearRaridade(bonus = 0) {
  const weights = { ...PESOS_RARIDADE };
  if (bonus) {
    weights["Lendário"] += bonus;
    weights["Épico"] += bonus;
    weights["Comum"] = Math.max(0, weights["Comum"] - 2 * bonus);
  }
  return weightedChoice(weights);
}

function gerarArma(nivel, classe, raridade = null, bonus = 0) {
  const names = NOMES_ARMA[classe] || NOMES_ARMA.Cavaleiro;
  return {
    nome: choice(names),
    tipo: "arma",
    raridade: raridade || sortearRaridade(bonus),
    valor_base: 5 + nivel * 2 + randInt(0, nivel + 2),
    efeito: {},
    descricao: "Uma arma de batalha.",
  };
}

function gerarArmadura(nivel, raridade = null, bonus = 0) {
  return {
    nome: choice(NOMES_ARMADURA),
    tipo: "armadura",
    raridade: raridade || sortearRaridade(bonus),
    valor_base: 3 + Math.floor(nivel * 1.5) + randInt(0, nivel + 1),
    efeito: {},
    descricao: "Proteção contra golpes.",
  };
}

function gerarConsumivel(tipo = "cura") {
  const catalog = {
    cura: { nome: "Poção de Cura", tipo: "consumivel", raridade: "Comum", valor_base: 0, efeito: { cura: 45 }, descricao: "Restaura 45 de HP." },
    cura_g: { nome: "Poção de Cura Maior", tipo: "consumivel", raridade: "Raro", valor_base: 0, efeito: { cura: 90 }, descricao: "Restaura 90 de HP." },
    recurso: { nome: "Poção de Energia", tipo: "consumivel", raridade: "Comum", valor_base: 0, efeito: { recurso: 40 }, descricao: "Restaura 40 do recurso da classe." },
    antidoto: { nome: "Antídoto", tipo: "consumivel", raridade: "Comum", valor_base: 0, efeito: { antidoto: true, cura: 10 }, descricao: "Remove veneno e cura 10 de HP." },
    captura: { nome: "Esfera de Selamento", tipo: "captura", raridade: "Raro", valor_base: 0, efeito: { captura: true }, descricao: "Aumenta a chance de capturar um inimigo enfraquecido." },
  };
  return structuredClone(catalog[tipo] || catalog.cura);
}

function xpParaNivel(nivel) {
  return Math.floor(80 * ((nivel - 1) ** 1.45)) + 60 * (nivel - 1);
}

function createPlayer(nome, genero, classe, dificuldade) {
  const base = CLASSES[classe];
  return {
    nome,
    genero,
    classe,
    dificuldade,
    nome_recurso: base.nome_recurso,
    hp_max: base.hp,
    hp: base.hp,
    recurso_max: base.recurso,
    recurso: base.recurso,
    dano: base.dano,
    defesa: base.defesa,
    crit: base.crit,
    evasao: base.evasao,
    nivel: 1,
    xp: 0,
    xp_prox: xpParaNivel(2),
    pontos_atributo: 0,
    karma: 0,
    veneno: 0,
    flags: [],
    eventos: [],
    inventario: [gerarConsumivel("cura"), gerarConsumivel("cura"), gerarConsumivel("recurso"), gerarConsumivel("captura")],
    aliados: [],
    arma: null,
    armadura: null,
  };
}

function normalizePlayer(raw) {
  const classe = CLASSES[raw?.classe] ? raw.classe : "Cavaleiro";
  const p = createPlayer(raw?.nome || "Herói", raw?.genero || "Outro", classe, raw?.dificuldade || "Normal");
  Object.assign(p, raw || {});
  p.flags = Array.isArray(p.flags) ? p.flags.map(String) : [];
  p.eventos = Array.isArray(p.eventos) ? p.eventos.map(String) : [];
  p.inventario = Array.isArray(p.inventario) ? p.inventario.filter(Boolean) : [];
  p.aliados = Array.isArray(p.aliados) ? p.aliados.filter(Boolean) : [];
  return p;
}

function danoTotal(player = app.player) {
  return player.dano + (player.arma ? itemValue(player.arma) : 0);
}

function defesaTotal(player = app.player) {
  return player.defesa + (player.armadura ? itemValue(player.armadura) : 0);
}

function alinhamento(player = app.player) {
  if (!player) return "-";
  if (player.karma >= 5) return "Herói";
  if (player.karma <= -5) return "Vilão";
  return "Neutro";
}

function gerarInimigo(nivelJogador, spec, difMult) {
  if (spec?.chefe) {
    const nivel = nivelJogador + 1;
    const fator = 1 + (nivel - 1) * 0.29;
    return {
      nome: choice(["Dragão Negro Vorthak", "Dragão Anciã Ignara", "Dragão das Cinzas"]),
      hp_max: Math.floor(220 * fator * difMult),
      hp: Math.floor(220 * fator * difMult),
      dano: Math.floor(28 * fator * difMult),
      defesa: Math.floor(12 * fator),
      xp: Math.floor(180 * fator),
      nivel,
      crit: 0.12,
      evasao: 0.05,
      veneno: 0,
      chefe: true,
      dot_turnos: 0,
      dot_dano: 0,
    };
  }
  const tipo = spec?.aleatorio ? choice(Object.keys(BESTIARIO)) : (spec?.tipo || choice(Object.keys(BESTIARIO)));
  const base = BESTIARIO[tipo] || BESTIARIO.Goblin;
  const nivel = Math.max(1, nivelJogador + randInt(-1, 1));
  const fatorDef = 1 + (nivel - 1) * 0.22;
  const fatorDano = 1 + (nivel - 1) * 0.32;
  const variacao = 0.9 + Math.random() * 0.25;
  const nome = `${choice(PREFIXOS_INIMIGO)}${tipo}`.trim();
  return {
    nome,
    hp_max: Math.floor(base.hp * fatorDef * variacao * difMult),
    hp: Math.floor(base.hp * fatorDef * variacao * difMult),
    dano: Math.floor(base.dano * fatorDano * variacao * difMult),
    defesa: Math.floor(base.defesa * fatorDef),
    xp: Math.floor(base.xp * fatorDef),
    nivel,
    crit: base.crit,
    evasao: base.evasao,
    veneno: base.veneno,
    chefe: false,
    dot_turnos: 0,
    dot_dano: 0,
  };
}

function log(message, tag = "") {
  app.log.push({ message, tag });
  if (app.log.length > 80) app.log = app.log.slice(-80);
  renderLog();
}

function clearLog() {
  app.log = [];
  renderLog();
}

function sceneForNode(nodeId) {
  return CENARIO_NO[nodeId] || "campo";
}

function eventoUnico(escolha) {
  if (escolha.repetivel) return false;
  return Boolean(escolha.loot || escolha.pocao || escolha.aliado || escolha.set_flag || escolha.combate || hasOwn(escolha, "karma"));
}

function eventoGrupoId(nodeId) {
  return `${nodeId}:__evento__`;
}

function eventoNoConcluido(nodeId) {
  const prefix = `${nodeId}:`;
  return app.player.eventos.includes(eventoGrupoId(nodeId)) || app.player.eventos.some((eventId) => eventId.startsWith(prefix));
}

function saidaSegura(escolha) {
  if (eventoUnico(escolha)) return false;
  const label = (escolha.label || "").toLowerCase();
  return ["sair", "voltar", "recuar", "seguir em frente"].some((term) => label.includes(term));
}

function noTemEvento(node) {
  return (node.escolhas || []).some(eventoUnico);
}

function escolhaDeEvento(node, escolha) {
  if (eventoUnico(escolha)) return true;
  return noTemEvento(node) && !saidaSegura(escolha);
}

function fallbackDestino(node) {
  for (const escolha of node.escolhas || []) {
    if (escolha.destino && !escolha.combate) return escolha.destino;
  }
  return node.escolhas?.[0]?.destino || "vila_hub";
}

function escolhaVisivel(escolha, eventId) {
  const nodeId = eventId ? eventId.split(":").slice(0, -1).join(":") : app.currentNode;
  const node = app.story[nodeId];
  if (node && eventoNoConcluido(nodeId) && escolhaDeEvento(node, escolha)) return false;
  if (eventId && eventoUnico(escolha) && app.player.eventos.includes(eventId)) return false;

  if (escolha.requer_karma) {
    const [op, value] = escolha.requer_karma;
    if (op === ">=" && !(app.player.karma >= value)) return false;
    if (op === "<=" && !(app.player.karma <= value)) return false;
  }

  if (escolha.requer_flag) {
    const flags = Array.isArray(escolha.requer_flag) ? escolha.requer_flag : [escolha.requer_flag];
    if (!flags.every((flag) => app.player.flags.includes(flag))) return false;
  }

  return true;
}

function concederItem(item) {
  log(`Você obteve: ${itemFullName(item)}`, "good");
  if (item.tipo === "arma") {
    if (!app.player.arma || itemValue(item) > itemValue(app.player.arma)) {
      if (app.player.arma) app.player.inventario.push(app.player.arma);
      app.player.arma = item;
      log("Equipado automaticamente.", "system");
    } else {
      app.player.inventario.push(item);
    }
    return;
  }
  if (item.tipo === "armadura") {
    if (!app.player.armadura || itemValue(item) > itemValue(app.player.armadura)) {
      if (app.player.armadura) app.player.inventario.push(app.player.armadura);
      app.player.armadura = item;
      log("Equipada automaticamente.", "system");
    } else {
      app.player.inventario.push(item);
    }
    return;
  }
  app.player.inventario.push(item);
}

function processChoice(escolha, eventId) {
  const node = app.story[app.currentNode];
  if (eventId && node && escolhaDeEvento(node, escolha)) {
    const groupId = eventoGrupoId(app.currentNode);
    if (!app.player.eventos.includes(groupId)) app.player.eventos.push(groupId);
    if (eventoUnico(escolha) && !app.player.eventos.includes(eventId)) app.player.eventos.push(eventId);
  }

  if (hasOwn(escolha, "karma") && escolha.karma !== 0) {
    app.player.karma += escolha.karma;
    log(`Karma ${escolha.karma > 0 ? "+" : ""}${escolha.karma} (total: ${app.player.karma}).`, escolha.karma > 0 ? "good" : "bad");
  }

  if (escolha.loot) {
    if (escolha.loot === "arma") concederItem(gerarArma(app.player.nivel, app.player.classe));
    else if (escolha.loot === "armadura") concederItem(gerarArmadura(app.player.nivel));
    else concederItem(Math.random() < 0.5 ? gerarArma(app.player.nivel, app.player.classe) : gerarArmadura(app.player.nivel));
  }

  if (escolha.pocao) concederItem(gerarConsumivel(escolha.pocao));

  if (escolha.aliado) {
    app.player.aliados.push({ nome: escolha.aliado, dano: 8, hp: 40, hp_max: 40 });
    log(`${escolha.aliado} juntou-se a você.`, "good");
  }

  if (escolha.set_flag && !app.player.flags.includes(escolha.set_flag)) {
    app.player.flags.push(escolha.set_flag);
    log("Você sente que algo importante mudou em sua jornada.", "title");
  }

  if (escolha.combate) {
    app.destinationAfterCombat = escolha.destino;
    startCombat(escolha.combate);
  } else {
    goToNode(escolha.destino);
  }
}

function goToNode(nodeId) {
  const node = app.story[nodeId];
  if (!node) {
    log(`Trecho '${nodeId}' não encontrado. Retornando com segurança.`, "system");
    nodeId = "vila_hub";
  }
  app.mode = "narrative";
  app.currentNode = nodeId;
  app.combat = null;
  const current = app.story[nodeId];
  log("-".repeat(38), "system");
  log(current.texto, current.final ? "title" : "");

  if (current.final || (current.escolhas || []).length === 0) {
    controls([
      button("Jogar novamente", () => renderTitle(), "primary"),
      button("Apagar save", () => {
        localStorage.removeItem(SAVE_KEY);
        renderTitle();
      }, "secondary"),
    ]);
  } else {
    renderChoices();
  }
  renderAll();
}

function renderChoices() {
  app.mode = "narrative";
  const node = app.story[app.currentNode];
  const items = [];
  let visible = 0;
  (node.escolhas || []).forEach((escolha, idx) => {
    const eventId = `${app.currentNode}:${idx}`;
    if (!escolhaVisivel(escolha, eventId)) return;
    visible += 1;
    items.push(button(escolha.label, () => processChoice(escolha, eventId), visible === 1 ? "primary" : ""));
  });
  if (visible === 0) {
    items.push(button("Seguir em frente", () => goToNode(fallbackDestino(node)), "primary"));
  }
  items.push(button("Inventário", renderInventory, "secondary"));
  items.push(button("Mapa", renderMap, "secondary"));
  items.push(button("Salvar", saveGame, "secondary"));
  items.push(button("Sair para o título", renderTitle, "secondary"));
  controls(items);
  renderAll();
}

function startCombat(spec) {
  const dif = DIFICULDADES[app.player.dificuldade]?.inimigo || 1;
  const enemy = gerarInimigo(app.player.nivel, spec, dif);
  app.player.veneno = 0;
  app.combat = { enemy, turno: 1, jogadorDefendendo: false, terminado: false };
  app.mode = "combat";
  log("=".repeat(38), "system");
  log(`COMBATE: ${enemy.nome} (Nv.${enemy.nivel}) aparece.`, "title");
  log(`HP ${enemy.hp} | Dano ${enemy.dano} | Defesa ${enemy.defesa}`, "system");
  renderCombatControls();
  renderAll();
}

function calcDano(base, mult, critChance, defesaAlvo, ignoraDefesa = false) {
  let dano = base * mult;
  const crit = Math.random() < critChance;
  if (crit) dano *= 1.8;
  if (!ignoraDefesa) dano -= defesaAlvo;
  return { dano: Math.max(1, Math.round(dano)), crit };
}

function renderCombatControls() {
  const items = [
    button("Atacar", renderAttackMenu, "primary"),
    button("Defender", playerDefend),
    button("Usar item", renderCombatItems),
  ];
  if (!app.combat.enemy.chefe) {
    items.push(button("Capturar", renderCaptureMenu));
    items.push(button("Fugir", playerRun, "secondary"));
  }
  controls(items);
}

function renderAttackMenu() {
  const items = ATAQUES[app.player.classe].map((attack) => {
    const cost = attack.custo ? `${attack.custo} ${app.player.nome_recurso}` : "sem custo";
    return button(`${attack.nome} (${cost}) - ${attack.desc}`, () => playerAttack(attack), attack.custo <= app.player.recurso ? "" : "secondary");
  });
  items.push(button("Voltar", renderCombatControls, "secondary"));
  controls(items);
}

function playerAttack(attack) {
  if (!app.combat || app.combat.terminado) return;
  if (app.player.recurso < attack.custo) {
    log(`${app.player.nome_recurso} insuficiente para ${attack.nome}.`, "system");
    return;
  }
  app.player.recurso -= attack.custo;
  const enemy = app.combat.enemy;

  if (attack.efeito === "cura") {
    const amount = Math.floor(danoTotal() * attack.mult);
    log(`Você conjura ${attack.nome} e recupera ${healPlayer(amount)} de HP.`, "good");
    afterPlayerAction();
    return;
  }

  if (attack.efeito === "defesa_buff") {
    app.combat.jogadorDefendendo = true;
    log("Você assume postura defensiva.", "system");
  }

  if (Math.random() < enemy.evasao) {
    log(`${enemy.nome} esquivou de ${attack.nome}.`, "system");
  } else {
    const result = calcDano(danoTotal(), attack.mult, app.player.crit + (attack.crit_bonus || 0), enemy.defesa, attack.efeito === "ignora_defesa");
    enemy.hp -= result.dano;
    log(`${result.crit ? "CRÍTICO! " : ""}${attack.nome} causa ${result.dano} de dano.`, result.crit ? "title" : "");
    if (attack.efeito === "gelo") {
      enemy.dot_turnos = 3;
      enemy.dot_dano = Math.max(4, Math.floor(danoTotal() / 4));
      log("O alvo sofrerá dano de frio por 3 turnos.", "system");
    }
  }
  afterPlayerAction();
}

function playerDefend() {
  app.combat.jogadorDefendendo = true;
  const regen = Math.floor(app.player.recurso_max * 0.18);
  app.player.recurso = clamp(app.player.recurso + regen, 0, app.player.recurso_max);
  log(`Você se defende e recupera ${regen} de ${app.player.nome_recurso}.`, "system");
  afterPlayerAction();
}

function renderCombatItems() {
  const usable = app.player.inventario.filter((item) => item.tipo === "consumivel");
  const items = usable.map((item) => button(`${item.nome} - ${item.descricao}`, () => useCombatItem(item)));
  if (!items.length) items.push(note("Nenhum consumível disponível."));
  items.push(button("Voltar", renderCombatControls, "secondary"));
  controls(items);
}

function itemWouldWork(item) {
  const ef = item.efeito || {};
  return Boolean((ef.antidoto && app.player.veneno > 0) || (ef.cura && app.player.hp < app.player.hp_max) || (ef.recurso && app.player.recurso < app.player.recurso_max));
}

function useCombatItem(item) {
  if (!itemWouldWork(item)) {
    log(`${item.nome} não teria efeito agora.`, "system");
    return;
  }
  applyConsumable(item);
  app.player.inventario.splice(app.player.inventario.indexOf(item), 1);
  afterPlayerAction();
}

function applyConsumable(item) {
  const ef = item.efeito || {};
  if (ef.antidoto) {
    app.player.veneno = 0;
    log(`${item.nome}: veneno neutralizado.`, "good");
  }
  if (ef.cura) log(`${item.nome}: +${healPlayer(ef.cura)} HP.`, "good");
  if (ef.recurso) {
    app.player.recurso = clamp(app.player.recurso + ef.recurso, 0, app.player.recurso_max);
    log(`${item.nome}: +${ef.recurso} ${app.player.nome_recurso}.`, "good");
  }
}

function renderCaptureMenu() {
  const chance = captureChance(false);
  const chanceSphere = captureChance(true);
  const items = [
    note(`Chance atual: ${Math.floor(chance * 100)}%. Quanto menor o HP do alvo, maior a chance.`),
    button(`Tentar capturar (${Math.floor(chance * 100)}%)`, () => playerCapture(false), "primary"),
  ];
  if (app.player.inventario.some((item) => item.efeito?.captura)) {
    items.push(button(`Usar Esfera de Selamento (${Math.floor(chanceSphere * 100)}%)`, () => {
      const idx = app.player.inventario.findIndex((item) => item.efeito?.captura);
      if (idx >= 0) app.player.inventario.splice(idx, 1);
      playerCapture(true);
    }));
  }
  items.push(button("Voltar", renderCombatControls, "secondary"));
  controls(items);
}

function captureChance(usouEsfera) {
  const enemy = app.combat.enemy;
  let chance = 0.05 + (1 - enemy.hp / enemy.hp_max) * 0.75;
  if (usouEsfera) chance += 0.15;
  return clamp(chance, 0.05, 0.92);
}

function playerCapture(usouEsfera) {
  const enemy = app.combat.enemy;
  if (enemy.chefe) {
    log("Criaturas tão poderosas não podem ser capturadas.", "system");
    return;
  }
  const chance = captureChance(usouEsfera);
  if (Math.random() < chance) {
    app.combat.terminado = true;
    app.player.aliados.push({ nome: enemy.nome, dano: Math.max(4, Math.floor(enemy.dano / 2)), hp: enemy.hp_max, hp_max: enemy.hp_max });
    log(`${enemy.nome} juntou-se a você.`, "good");
    finishCombat("captura");
  } else {
    log(`A captura falhou (${Math.floor(chance * 100)}%).`, "system");
    afterPlayerAction();
  }
}

function playerRun() {
  if (app.combat.enemy.chefe) {
    log("Não há para onde fugir.", "system");
    return;
  }
  if (Math.random() < 0.6) {
    log("Você conseguiu fugir do combate.", "system");
    finishCombat("fuga");
  } else {
    log("A fuga falhou.", "system");
    afterPlayerAction();
  }
}

function afterPlayerAction() {
  const enemy = app.combat.enemy;
  for (const ally of app.player.aliados) {
    if (enemy.hp <= 0) break;
    const damage = Math.max(1, ally.dano - Math.floor(enemy.defesa / 2));
    enemy.hp -= damage;
    log(`${ally.nome} ataca por ${damage}.`, "system");
  }

  if (enemy.dot_turnos > 0 && enemy.hp > 0) {
    enemy.hp -= enemy.dot_dano;
    enemy.dot_turnos -= 1;
    log(`O frio causa ${enemy.dot_dano} de dano adicional.`, "system");
  }

  if (enemy.hp <= 0) {
    winCombat();
    return;
  }

  enemyTurn();
  if (app.combat.terminado) return;
  app.combat.turno += 1;
  log(`Turno ${app.combat.turno}.`, "system");
  renderCombatControls();
  renderAll();
}

function enemyTurn() {
  const enemy = app.combat.enemy;
  if (app.player.veneno > 0) {
    const damage = 4 + enemy.nivel;
    app.player.hp -= damage;
    app.player.veneno -= 1;
    log(`Veneno causa ${damage} de dano.`, "bad");
    if (app.player.hp <= 0) {
      loseCombat();
      return;
    }
  }

  if (app.player.aliados.length && Math.random() < 0.4) {
    const ally = choice(app.player.aliados);
    const result = calcDano(enemy.dano, 1, enemy.crit, 0);
    ally.hp -= result.dano;
    log(`${enemy.nome} ataca ${ally.nome} por ${result.dano}.`, "bad");
    app.player.aliados = app.player.aliados.filter((item) => item.hp > 0);
    app.combat.jogadorDefendendo = false;
    return;
  }

  if (Math.random() < app.player.evasao) {
    log(`Você esquiva do ataque de ${enemy.nome}.`, "system");
  } else {
    const result = calcDano(enemy.dano, 1, enemy.crit, defesaTotal());
    let damage = result.dano;
    if (app.combat.jogadorDefendendo) damage = Math.max(1, Math.floor(damage * 0.5));
    app.player.hp -= damage;
    log(`${result.crit ? "CRÍTICO! " : ""}${enemy.nome} causa ${damage} de dano.`, result.crit ? "bad" : "");
    if (enemy.veneno && Math.random() < enemy.veneno) {
      app.player.veneno = 3;
      log("Você foi envenenado.", "bad");
    }
  }

  app.combat.jogadorDefendendo = false;
  if (app.player.hp <= 0) loseCombat();
}

function winCombat() {
  const enemy = app.combat.enemy;
  app.combat.terminado = true;
  app.player.veneno = 0;
  log(`${enemy.nome} foi derrotado.`, "good");
  const levels = gainXp(enemy.xp);
  log(`+${enemy.xp} XP.`, "system");
  if (levels) log(`Você subiu para o nível ${app.player.nivel}.`, "good");
  dropLoot(enemy);
  finishCombat("vitoria");
}

function loseCombat() {
  app.combat.terminado = true;
  app.player.veneno = 0;
  log("Você foi derrotado.", "bad");
  controls([
    button("Voltar ao título", renderTitle, "primary"),
    button("Carregar save", loadGame, "secondary"),
  ]);
  renderAll();
}

function finishCombat() {
  app.combat = null;
  if (app.player.pontos_atributo > 0) renderAttributes(() => goToNode(app.destinationAfterCombat));
  else goToNode(app.destinationAfterCombat);
}

function gainXp(amount) {
  app.player.xp += amount;
  let levels = 0;
  while (app.player.xp >= app.player.xp_prox) {
    app.player.xp -= app.player.xp_prox;
    app.player.nivel += 1;
    levels += 1;
    app.player.pontos_atributo += GANHO_NIVEL.pontos_atributo;
    app.player.hp_max += GANHO_NIVEL.hp_max;
    app.player.recurso_max += GANHO_NIVEL.recurso_max;
    app.player.dano += GANHO_NIVEL.dano;
    app.player.defesa += GANHO_NIVEL.defesa;
    app.player.hp = app.player.hp_max;
    app.player.recurso = app.player.recurso_max;
    app.player.xp_prox = xpParaNivel(app.player.nivel + 1);
  }
  return levels;
}

function dropLoot(enemy) {
  const bonus = enemy.chefe ? 25 : 0;
  const equipChance = enemy.chefe ? 1 : 0.5;
  if (Math.random() < equipChance) {
    concederItem(Math.random() < 0.5 ? gerarArma(app.player.nivel, app.player.classe, null, bonus) : gerarArmadura(app.player.nivel, null, bonus));
  }
  if (Math.random() < 0.6) {
    concederItem(gerarConsumivel(choice(["cura", "recurso", "antidoto"])));
  }
}

function healPlayer(amount) {
  const before = app.player.hp;
  app.player.hp = clamp(app.player.hp + amount, 0, app.player.hp_max);
  return app.player.hp - before;
}

function renderInventory() {
  if (!app.player) return;
  app.mode = "inventory";
  const items = [
    note(`Arma: ${app.player.arma ? itemFullName(app.player.arma) : "(nenhuma)"}`),
    note(`Armadura: ${app.player.armadura ? itemFullName(app.player.armadura) : "(nenhuma)"}`),
  ];
  const equip = app.player.inventario.filter((item) => item.tipo === "arma" || item.tipo === "armadura");
  const consumables = app.player.inventario.filter((item) => item.tipo === "consumivel");
  const spheres = app.player.inventario.filter((item) => item.tipo === "captura");

  if (equip.length) items.push(label("Equipamentos"));
  for (const item of equip) items.push(button(`Equipar ${itemFullName(item)}`, () => equipItem(item)));

  if (consumables.length) items.push(label("Consumíveis"));
  for (const item of consumables) items.push(button(`Usar ${item.nome} - ${item.descricao}`, () => useInventoryItem(item)));

  if (spheres.length) items.push(note(`Esferas de Selamento: ${spheres.length}`));
  if (!equip.length && !consumables.length && !spheres.length) items.push(note("Inventário vazio."));
  items.push(button("Voltar", renderChoices, "secondary"));
  controls(items);
  renderAll();
}

function equipItem(item) {
  const slot = item.tipo;
  if (slot === "arma") {
    if (app.player.arma) app.player.inventario.push(app.player.arma);
    app.player.arma = item;
  } else {
    if (app.player.armadura) app.player.inventario.push(app.player.armadura);
    app.player.armadura = item;
  }
  app.player.inventario.splice(app.player.inventario.indexOf(item), 1);
  log(`Equipado: ${itemFullName(item)}`, "system");
  renderInventory();
}

function useInventoryItem(item) {
  if (!itemWouldWork(item)) {
    log(`${item.nome} não teria efeito agora.`, "system");
    return;
  }
  applyConsumable(item);
  app.player.inventario.splice(app.player.inventario.indexOf(item), 1);
  renderInventory();
}

function renderAttributes(callback) {
  app.mode = "attributes";
  const items = [
    note(`Você tem ${app.player.pontos_atributo} ponto(s) de atributo.`),
    note(`HP ${app.player.hp_max} | Dano ${app.player.dano} | Defesa ${app.player.defesa} | ${app.player.nome_recurso} ${app.player.recurso_max}`),
    button(`+${ATRIBUTO_GANHOS.hp} HP`, () => spendAttribute("hp", callback)),
    button(`+${ATRIBUTO_GANHOS.dano} Dano`, () => spendAttribute("dano", callback)),
    button(`+${ATRIBUTO_GANHOS.defesa} Defesa`, () => spendAttribute("defesa", callback)),
    button(`+${ATRIBUTO_GANHOS.recurso} ${app.player.nome_recurso}`, () => spendAttribute("recurso", callback)),
    button("Concluir", callback, "primary"),
  ];
  controls(items);
  renderAll();
}

function spendAttribute(attr, callback) {
  if (app.player.pontos_atributo <= 0) return;
  app.player.pontos_atributo -= 1;
  if (attr === "hp") {
    app.player.hp_max += ATRIBUTO_GANHOS.hp;
    app.player.hp += ATRIBUTO_GANHOS.hp;
  } else if (attr === "dano") app.player.dano += ATRIBUTO_GANHOS.dano;
  else if (attr === "defesa") app.player.defesa += ATRIBUTO_GANHOS.defesa;
  else {
    app.player.recurso_max += ATRIBUTO_GANHOS.recurso;
    app.player.recurso += ATRIBUTO_GANHOS.recurso;
  }
  renderAttributes(callback);
}

function renderMap() {
  if (!app.player) return;
  app.mode = "map";
  controls([
    note("Mapa de Pedravale e arredores."),
    button("Voltar", renderChoices, "secondary"),
  ]);
  renderAll();
}

function saveGame() {
  if (!app.player) return;
  localStorage.setItem(SAVE_KEY, JSON.stringify({
    versao: SAVE_VERSION,
    jogador: app.player,
    no_atual: app.currentNode,
  }));
  log("Progresso salvo no navegador.", "good");
  renderAll();
}

function loadGame() {
  const raw = localStorage.getItem(SAVE_KEY);
  if (!raw) {
    log("Nenhum save encontrado.", "system");
    return;
  }
  try {
    const data = JSON.parse(raw);
    app.player = normalizePlayer(data.jogador);
    clearLog();
    log("Jogo carregado. Bem-vindo de volta.", "title");
    goToNode(data.no_atual || "inicio");
  } catch (error) {
    log(`Save corrompido: ${error.message}`, "bad");
  }
}

function renderTitle() {
  app.mode = "title";
  app.player = null;
  app.combat = null;
  app.currentNode = null;
  clearLog();
  log("Crônicas de Pedravale", "title");
  log("Um RPG de aventura por escolhas em um reino medieval ameaçado.");
  const items = [
    button("Novo jogo", renderCharacterCreation, "primary"),
  ];
  if (localStorage.getItem(SAVE_KEY)) items.push(button("Carregar jogo", loadGame));
  controls(items);
  renderAll();
}

function renderCharacterCreation() {
  app.mode = "creation";
  clearLog();
  log("Criação de personagem", "title");
  log("Escolha nome, gênero, classe e dificuldade para começar.");

  const name = input("Nome", "nome", "Herói");
  const gender = select("Gênero", "genero", ["Masculino", "Feminino", "Outro"]);
  const klass = select("Classe", "classe", Object.keys(CLASSES));
  const diff = select("Dificuldade", "dificuldade", Object.keys(DIFICULDADES), "Normal");
  const classInfo = document.createElement("div");
  classInfo.className = "choice-note";

  const updateInfo = () => {
    const data = CLASSES[klass.querySelector("select").value];
    classInfo.textContent = `${data.descricao} HP ${data.hp} | ${data.nome_recurso} ${data.recurso} | Dano ${data.dano} | Defesa ${data.defesa}`;
  };
  klass.querySelector("select").addEventListener("change", updateInfo);
  updateInfo();

  controls([
    name,
    gender,
    klass,
    diff,
    classInfo,
    button("Começar jornada", () => {
      const playerName = name.querySelector("input").value.trim().slice(0, 20);
      if (!playerName) {
        log("O nome não pode ficar vazio.", "bad");
        return;
      }
      app.player = createPlayer(
        playerName,
        gender.querySelector("select").value,
        klass.querySelector("select").value,
        diff.querySelector("select").value,
      );
      clearLog();
      log(`Bem-vindo(a), ${app.player.nome}, o(a) ${app.player.classe}.`, "title");
      goToNode("inicio");
    }, "primary"),
    button("Voltar", renderTitle, "secondary"),
  ]);
  renderAll();
}

function renderStatus() {
  if (!app.player) {
    el.status.innerHTML = `
      <div class="stat"><span>Status</span><strong>Sem personagem</strong></div>
      <div class="stat"><span>Save</span><strong>${localStorage.getItem(SAVE_KEY) ? "Disponível" : "Vazio"}</strong></div>
    `;
    return;
  }
  const p = app.player;
  el.status.innerHTML = "";
  el.status.append(
    stat("Nome", `${p.nome} Nv.${p.nivel}`),
    stat("Classe", p.classe),
    stat("HP", `${p.hp}/${p.hp_max}`, p.hp / p.hp_max, "var(--green)"),
    stat(p.nome_recurso, `${p.recurso}/${p.recurso_max}`, p.recurso / p.recurso_max, "var(--blue)"),
    stat("Dano/Defesa", `${danoTotal()}/${defesaTotal()}`),
    stat("Karma", `${p.karma} (${alinhamento()})`),
  );
}

function stat(labelText, value, frac = null, color = "var(--green)") {
  const node = document.createElement("div");
  node.className = "stat";
  node.innerHTML = `<span></span><strong></strong>`;
  node.querySelector("span").textContent = labelText;
  node.querySelector("strong").textContent = value;
  if (frac !== null) {
    const bar = document.createElement("div");
    bar.className = "bar";
    bar.innerHTML = `<i style="width:${clamp(frac, 0, 1) * 100}%; background:${color}"></i>`;
    node.append(bar);
  }
  return node;
}

function renderLog() {
  el.log.innerHTML = "";
  for (const entry of app.log) {
    const div = document.createElement("div");
    div.className = `entry ${entry.tag || ""}`;
    if (entry.tag === "title") div.classList.add("title");
    if (entry.tag === "good") div.classList.add("good");
    if (entry.tag === "bad") div.classList.add("bad");
    if (entry.tag === "system") div.classList.add("system");
    div.textContent = entry.message;
    el.log.append(div);
  }
  el.log.scrollTop = el.log.scrollHeight;
}

function controls(nodes) {
  el.controls.innerHTML = "";
  for (const node of nodes) el.controls.append(node);
}

function button(text, onClick, kind = "") {
  const node = document.createElement("button");
  node.type = "button";
  node.textContent = text;
  if (kind) node.className = kind;
  node.addEventListener("click", onClick);
  return node;
}

function note(text) {
  const node = document.createElement("div");
  node.className = "choice-note";
  node.textContent = text;
  return node;
}

function label(text) {
  const node = document.createElement("div");
  node.className = "section-label";
  node.textContent = text;
  return node;
}

function input(labelText, id, value = "") {
  const wrap = document.createElement("div");
  wrap.className = "field";
  wrap.innerHTML = `<label for="${id}"></label><input id="${id}" type="text">`;
  wrap.querySelector("label").textContent = labelText;
  wrap.querySelector("input").value = value;
  return wrap;
}

function select(labelText, id, options, value = options[0]) {
  const wrap = document.createElement("div");
  wrap.className = "field";
  const labelNode = document.createElement("label");
  labelNode.setAttribute("for", id);
  labelNode.textContent = labelText;
  const selectNode = document.createElement("select");
  selectNode.id = id;
  for (const option of options) {
    const item = document.createElement("option");
    item.value = option;
    item.textContent = option;
    if (option === value) item.selected = true;
    selectNode.append(item);
  }
  wrap.append(labelNode, selectNode);
  return wrap;
}

function renderHeader() {
  el.title.textContent = app.player ? `${app.player.nome} em Pedravale` : "Crônicas de Pedravale";
  el.subtitle.textContent = app.currentNode ? `${app.currentNode} | ${app.mode}` : "RPG de aventura por escolhas";
  const enabled = Boolean(app.player);
  el.inventory.disabled = !enabled || app.mode === "combat";
  el.map.disabled = !enabled || app.mode === "combat";
  el.save.disabled = !enabled;
}

function renderAll() {
  renderStatus();
  renderHeader();
  drawScene();
}

function image(path) {
  return app.images[path];
}

function loadImage(path) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve([path, img]);
    img.onerror = () => resolve([path, null]);
    img.src = path;
  });
}

function drawScene() {
  const w = el.canvas.width;
  const h = el.canvas.height;
  ctx.clearRect(0, 0, w, h);
  const scene = app.mode === "map" ? "mapa" : (app.mode === "title" || app.mode === "creation" ? "titulo" : sceneForNode(app.currentNode));
  const bg = image(BG_BY_SCENE[scene] || BG_BY_SCENE.campo);
  if (bg) drawCover(bg, 0, 0, w, h);
  else {
    ctx.fillStyle = "#15191a";
    ctx.fillRect(0, 0, w, h);
  }
  ctx.fillStyle = "rgba(0, 0, 0, 0.22)";
  ctx.fillRect(0, 0, w, h);

  if (app.mode === "combat" && app.combat) drawCombat(w, h);
  else if (app.mode === "map") drawMapLabels(w, h);
  else drawSceneTitle(w, h);
}

function drawCover(img, x, y, w, h) {
  const scale = Math.max(w / img.width, h / img.height);
  const dw = img.width * scale;
  const dh = img.height * scale;
  ctx.drawImage(img, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh);
}

function drawSceneTitle(w, h) {
  ctx.save();
  ctx.fillStyle = "rgba(12, 14, 15, 0.62)";
  ctx.fillRect(42, h - 158, Math.min(760, w - 84), 100);
  ctx.fillStyle = "#f2eee4";
  ctx.font = "700 42px system-ui, sans-serif";
  ctx.fillText(app.mode === "title" ? "Crônicas de Pedravale" : sceneName(), 64, h - 104);
  ctx.fillStyle = "#d6ae56";
  ctx.font = "22px system-ui, sans-serif";
  ctx.fillText(app.player ? `${app.player.classe} | ${alinhamento()}` : "Aventura por escolhas", 66, h - 70);
  ctx.restore();
}

function sceneName() {
  const names = {
    vila: "Pedravale",
    floresta: "Floresta Sussurrante",
    campo: "Estradas de Pedravale",
    caverna: "Cavernas de Veludo",
    covil: "Covil de Vorthak",
    amanhecer: "Aurora",
  };
  return names[sceneForNode(app.currentNode)] || "Pedravale";
}

function drawCombat(w, h) {
  const enemy = app.combat.enemy;
  drawHero(w * 0.25, h * 0.62, 120);
  drawEnemy(enemy, w * 0.7, h * 0.56, enemy.chefe ? 280 : 150);
  drawHpBar(w * 0.16, h * 0.72, 260, 18, app.player.hp / app.player.hp_max, app.player.nome);
  drawHpBar(w * 0.58, h * 0.72, 320, 18, enemy.hp / enemy.hp_max, enemy.nome);
}

function drawHero(cx, cy, size) {
  const tiny = image(assetPath("tiny_dungeon.png"));
  const tile = HERO_TILES[app.player.classe] || HERO_TILES.Cavaleiro;
  if (tiny) {
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(tiny, tile[0] * 16, tile[1] * 16, 16, 16, cx - size / 2, cy - size, size, size);
    ctx.imageSmoothingEnabled = true;
    return;
  }
  ctx.fillStyle = "#d6ae56";
  ctx.fillRect(cx - size / 3, cy - size, size / 1.5, size);
}

function drawEnemy(enemy, cx, cy, size) {
  const dragon = image(assetPath("dragao_vorthak.png"));
  if (enemy.chefe && dragon) {
    drawContain(dragon, cx - size / 2, cy - size / 2, size, size * 0.8);
    return;
  }
  const tiny = image(assetPath("tiny_dungeon.png"));
  const key = Object.keys(ENEMY_TILES).find((name) => enemy.nome.includes(name));
  if (tiny && key) {
    const tile = ENEMY_TILES[key];
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(tiny, tile[0] * 16, tile[1] * 16, 16, 16, cx - size / 2, cy - size, size, size);
    ctx.imageSmoothingEnabled = true;
    return;
  }
  ctx.fillStyle = "#9f4f45";
  ctx.beginPath();
  ctx.ellipse(cx, cy - size / 2, size / 2, size / 2.4, 0, 0, Math.PI * 2);
  ctx.fill();
}

function drawContain(img, x, y, w, h) {
  const scale = Math.min(w / img.width, h / img.height);
  const dw = img.width * scale;
  const dh = img.height * scale;
  ctx.drawImage(img, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh);
}

function drawHpBar(x, y, w, h, frac, text) {
  ctx.fillStyle = "rgba(0, 0, 0, 0.72)";
  ctx.fillRect(x, y, w, h + 30);
  ctx.fillStyle = "#e6dfd2";
  ctx.font = "18px system-ui, sans-serif";
  ctx.fillText(text, x + 10, y + 21);
  ctx.fillStyle = "#1a1d1e";
  ctx.fillRect(x + 10, y + 28, w - 20, h);
  ctx.fillStyle = frac > 0.6 ? "#7fc97f" : frac > 0.3 ? "#d6ae56" : "#e06a5b";
  ctx.fillRect(x + 10, y + 28, (w - 20) * clamp(frac, 0, 1), h);
}

function drawMapLabels(w, h) {
  const labels = [
    ["Pedravale", 0.16, 0.32],
    ["Floresta", 0.4, 0.64],
    ["Aldoria", 0.64, 0.3],
    ["Cavernas", 0.86, 0.62],
  ];
  ctx.font = "700 24px system-ui, sans-serif";
  for (const [name, px, py] of labels) {
    const x = w * px;
    const y = h * py;
    ctx.fillStyle = "#d6ae56";
    ctx.beginPath();
    ctx.arc(x, y, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "rgba(0, 0, 0, 0.68)";
    ctx.fillRect(x + 12, y - 28, ctx.measureText(name).width + 20, 38);
    ctx.fillStyle = "#f2eee4";
    ctx.fillText(name, x + 22, y - 2);
  }
}

function resizeCanvas() {
  const rect = el.canvas.getBoundingClientRect();
  el.canvas.width = Math.max(640, Math.floor(rect.width));
  el.canvas.height = Math.max(360, Math.floor(rect.height));
  drawScene();
}

async function init() {
  const [story, loadedImages] = await Promise.all([
    fetch(webPath("story.json")).then((response) => response.json()),
    Promise.all([
      assetPath("titulo.jpg"),
      assetPath("vila.png"),
      assetPath("floresta.png"),
      assetPath("caverna_veludo.png"),
      assetPath("covil.png"),
      assetPath("mapa.jpg"),
      assetPath("tiny_dungeon.png"),
      assetPath("dragao_vorthak.png"),
    ].map(loadImage)),
  ]);
  app.story = story;
  for (const [path, img] of loadedImages) app.images[path] = img;
  renderTitle();
  window.addEventListener("resize", resizeCanvas);
  el.inventory.addEventListener("click", renderInventory);
  el.map.addEventListener("click", renderMap);
  el.save.addEventListener("click", saveGame);
  resizeCanvas();
}

init().catch((error) => {
  log(`Erro ao iniciar a versão web: ${error.message}`, "bad");
});
