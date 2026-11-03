"""Etapa 3: cenários com taxas de fontes públicas (03/11/2026).
MECH: NASA/CR-2001-210647 (Pettit e Turnbull), sistema longitudinal de GA a cabo: Weibull beta 1,57, alfa 4718 h;
      taxa de risco 7,44e-6/h (Tab. 19, t = 6 h) e média de 4188 h entre falhas (Tab. 3), ~2,4e-4/h com todas as falhas registradas.
CLUTCH: NSWC-11 (2011), solenoide 2,77 falhas/1e6 operações (eq. de base); 1 demanda por hora de voo (ASSUMIDO).
RHO_ERR: FMD-2016, exemplo 'Actuator' genérico (Fig. 1-1): 'Spurious Position Change' 43,8% da distribuição normalizada (fraco: exemplo genérico)."""
import params as P, coalloc as C
base = dict(P.RATE); rho0 = P.RHO_RAW
def run(tag):
    out = []
    for reg in P.REGIMES:
        rr = [C.evaluate(d, reg) for d in C.design_space()]
        par = C.pareto(rr)
        out.append(f"{reg}: " + (', '.join(f"{r['design']}({r['dal_cost']})" for r in par) if par else 'nenhum viável'))
    print(f'{tag:40s}', ' | '.join(out))
for mech, mt in ((7.44e-6, 'MECH 7,4e-6 (NASA, t=6 h)'), (2.4e-4, 'MECH 2,4e-4 (NASA, 1/média)')):
    for rho, rt in ((0.1, 'rho 0,1'), (0.438, 'rho 0,44 (FMD ex.)')):
        P.RATE.update(base); P.RATE['MECH'] = mech; P.RATE['CLUTCH'] = 2.77e-6; P.RHO_RAW = rho
        run(f'{mt}, {rt}')
P.RATE.update(base); P.RHO_RAW = rho0
