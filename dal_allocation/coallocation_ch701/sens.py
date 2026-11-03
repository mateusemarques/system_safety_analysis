import params as P, coalloc as C, itertools
base = dict(P.RATE); rho = P.RHO_RAW
def run(tag):
    out=[]
    for reg in P.REGIMES:
        rr=[C.evaluate(d,reg) for d in C.design_space()]
        out.append(f"{reg}: {[r['design'] for r in C.pareto(rr)] or 'nenhum viável'}")
    print(tag, ' | '.join(out))
for mech in (1e-7,1e-6,3e-6,1e-5):
    P.RATE.update(base); P.RATE['MECH']=mech; run(f'MECH={mech:.0e}')
P.RATE.update(base)
for f in (0.5,2.0):
    P.RATE['FCC']=base['FCC']*f; run(f'FCCx{f}')
P.RATE.update(base)
for r in (0.1,0.2,1.0):
    P.RHO_RAW=r; run(f'rho_err={r}')
P.RHO_RAW=rho
for b in (30e-6, 300e-6):
    P.RATE['BAT']=b; run(f'BAT={b:.0e}')
