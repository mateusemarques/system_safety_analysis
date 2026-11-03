"""Parâmetros do protótipo de coalocação (CH 701 elétrico, comando de arfagem).
TODOS os valores marcados PLACEHOLDER são hipóteses de trabalho, para serem trocados por catálogo/FMECA na etapa 3.
Taxas por hora de voo; exposição T = 1 h (probabilidade por hora ~ soma dos produtos das taxas)."""

# --- Taxas de falha de hardware (por hora) ---
RATE = {
    'BAT':   93.1e-6,   # bateria de lítio, NASA/CR-2019-220217 Tab. 3 (aplicada)
    'DCDC':  200e-6,    # "fonte de alimentação", NASA/CR-2019-220217
    'ACE':   47.5e-6,   # controlador do motor do EMA ~ "controlador de motor", NASA/CR-2019-220217
    'MOT':   92.4e-6,   # motor elétrico do EMA, NASA/CR-2019-220217
    'FCC':   47.5e-6,   # PLACEHOLDER: computador de voo igualado ao controlador de motor
    'MECH':  7.44e-6,   # NASA/CR-2001-210647 Tab. 19: sistema longitudinal de GA a cabo, taxa de risco em t = 6 h (limite inferior; 1/média = 2,4e-4)
    'CLUTCH': 2.77e-6,  # NSWC-11 (2011): solenoide, 2,77/1e6 operações; 1 demanda por hora de voo (ASSUMIDO)
}
RHO_RAW = 0.438 # fração BRUTA das falhas de FCC/ACE que é comando errôneo: FMD-2016, exemplo 'Actuator' genérico (fraco)
# --- Cobertura do monitor por canal: VARIÁVEL DE PROJETO (etapa 3, 03/11/2026) ---
# taxa errônea não detectada = lambda * RHO_RAW * (1 - c)
# mass: kg por canal; mon_rate: taxa do hardware de monitor (falso disparo/falha => passivação = perda do canal)
# dev_indep: o monitor é dissimilar e entra como item independente nos FFS de erro de desenvolvimento do runaway
COVERAGE = {
    'c90':  dict(c=0.90,  mass=0.00, mon_rate=0.0,   dev_indep=False),  # BIT/watchdog/razoabilidade no próprio FCC
    'c99':  dict(c=0.99,  mass=0.10, mon_rate=10e-6, dev_indep=False),  # ASSUMIDO: sensor de posição da superfície + monitor no ACE
    'c999': dict(c=0.999, mass=0.20, mon_rate=15e-6, dev_indep=True),   # ASSUMIDO: + monitor dissimilar com envelope de autoridade
}
RHO_JAM = 0.1   # PLACEHOLDER: fração das falhas do motor do EMA que é emperramento

# --- Massas (kg) ---
MASS = {
    'FCC_LANE': 0.4,    # PLACEHOLDER por pista (COM ou MON)
    'EMA': 2.23,        # etapa 3: canal que move a superfície toda, ~10 N·m no servo (extrapolado da escala Dynon SV52)
    'EMA_A1': 0.635,    # etapa 3: Garmin GSA 28 (60 in-lb, 0,635 kg) basta para 20% da superfície (~2 N·m)
    'BAT_DED': 0.27,    # etapa 3: ~15 Wh (10 W típ. x 1,5 h) a 90 Wh/kg + 0,1 kg (premissas em etapa3/dimensionamento_ema.py)
    'DCDC': 0.3,        # PLACEHOLDER conversor por canal a partir da bateria de propulsão
    'HARNESS': 0.4,     # PLACEHOLDER chicote por canal
    'MECH': 6.7,        # comandos mecânicos a substituir (build-up do CH 701, projeto paralelo)
    'CLUTCH': 0.5,      # PLACEHOLDER
}
MIN_PER_KG = -0.5   # retrofit CH 701: ~0,5 min de autonomia perdidos por kg (dual, 250 Wh/kg)

# --- Custos de garantia (Baron e Louis, 2021, como em Delmas et al. 2023) ---
COST_HW = {'E': 100, 'D': 105, 'C': 137, 'B': 157, 'A': 165}
COST_SW = {k: 5 * v - (0 if k == 'E' else 0) for k, v in COST_HW.items()}
COST_SW = {'E': 500, 'D': 525, 'C': 683, 'B': 785, 'A': 824}   # mesmos valores dos itens CCF_SW do WBS

# --- Regimes ---
# fdal: DAL de partida por severidade; reduce: aplica a Tabela 3 da ARP4754A; target: objetivo por hora
REGIMES = {
    'ClassI':   dict(fdal={'CAT': 'C', 'HAZ': 'C', 'MAJ': 'C', 'MIN': 'D'}, reduce=False,
                     target={'CAT': 1e-6, 'HAZ': 1e-5, 'MAJ': 1e-4, 'MIN': 1e-3}, nsev={'CAT': 2}),
    'Basic':    dict(fdal={'CAT': 'C', 'HAZ': 'C', 'MAJ': 'C', 'MIN': 'D'}, reduce=False,
                     target={'CAT': 1e-7, 'HAZ': 1e-6, 'MAJ': 1e-5, 'MIN': 1e-3}, nsev={'CAT': 2}),
    'Enhanced': dict(fdal={'CAT': 'A', 'HAZ': 'B', 'MAJ': 'C', 'MIN': 'D'}, reduce=True,
                     target={'CAT': 1e-9, 'HAZ': 1e-7, 'MAJ': 1e-5, 'MIN': 1e-3}, nsev={'CAT': 2}),
}
SPLIT_FRACTION = 0.2   # A1: fração da superfície movida pelo FBW (TUM ~20%); runaway vira MAJ
