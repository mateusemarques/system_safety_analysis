"""Cobertura como variável de projeto: frente por regime em cenários de rho_raw e taxa do FCC/ACE."""
import params as P, coalloc as C
base = dict(P.RATE); rho0 = P.RHO_RAW
def run(tag):
    out = []
    for reg in P.REGIMES:
        rr = [C.evaluate(d, reg) for d in C.design_space()]
        par = C.pareto(rr)
        out.append(f"{reg}: " + (', '.join(f"{r['design']}({r['dal_cost']}; {r['dmass_kg']:+.1f} kg)" for r in par) if par else 'nenhum viável'))
    print(f'{tag:24s}', ' | '.join(out))
for rho in (0.438, 1.0):
    for f in (1, 3, 10):
        P.RATE.update(base); P.RATE['FCC'] = base['FCC']*f; P.RATE['ACE'] = base['ACE']*f; P.RHO_RAW = rho
        run(f'rho={rho} FCC,ACEx{f}')
P.RATE.update(base); P.RHO_RAW = rho0
