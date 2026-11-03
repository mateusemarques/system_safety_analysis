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
    'MECH':  1e-6,      # PLACEHOLDER: falha (emperramento/desconexão) do comando mecânico remanescente
    'CLUTCH': 10e-6,    # PLACEHOLDER: embreagem não abre quando comandada (conceito TUM)
}
RHO_ERR = 0.1   # PLACEHOLDER: fração das falhas de FCC/ACE que é comando errôneo (não detectado na fonte)
RHO_JAM = 0.1   # PLACEHOLDER: fração das falhas do motor do EMA que é emperramento

# --- Massas (kg) ---
MASS = {
    'FCC_LANE': 0.4,    # PLACEHOLDER por pista (COM ou MON)
    'EMA': 1.5,         # PLACEHOLDER motor + redutor + ACE
    'BAT_DED': 1.0,     # PLACEHOLDER bateria dedicada por canal
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
