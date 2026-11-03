"""Protótipo da etapa 2: coalocação arquitetura x independência x DAL x massa (CH 701, arfagem).
Espaço de projeto: arquitetura (A1 simplex+reversão mecânica TUM, A2 duplex COM/MON, A3 triplex votado),
energia (bateria de propulsão comum via DC/DC ou bateria dedicada por canal) e software (comum ou dissimilar).
Para cada projeto: cortes mínimos de hardware (probabilidade e ordem mínima) e de erro de desenvolvimento
(alocação de DAL por CP-SAT com as regras do regime). A0 (mecânico) é referência de massa.
O espaço é pequeno e é enumerado exatamente; a codificação conjunta num único CP-SAT fica para bibliotecas maiores."""
import itertools, math, csv, sys
from ortools.sat.python import cp_model
import params as P

# ---------- álgebra de cortes mínimos ----------
def ev(name): return {frozenset([name])}
def OR(*xs): return minimize(set().union(*xs))
def AND(*xs):
    out = {frozenset()}
    for x in xs: out = {a | b for a in out for b in x}
    return minimize(out)
def KofN(k, xs): return OR(*[AND(*c) for c in itertools.combinations(xs, k)])
def minimize(s):
    s = sorted(set(s), key=len); keep = []
    for c in s:
        if not any(k <= c for k in keep): keep.append(c)
    return set(keep)

# ---------- geração de cortes por projeto ----------
def design_space(covs=None):
    covs = covs or list(P.COVERAGE)
    for cov in covs:
        yield dict(arch='A1', n=1, energy='common', sw='common', cov=cov)
        yield dict(arch='A1', n=1, energy='dedicated', sw='common', cov=cov)
        for arch, n in (('A2', 2), ('A3', 3)):
            for energy in ('common', 'dedicated'):
                for sw in ('common', 'dissimilar'):
                    yield dict(arch=arch, n=n, energy=energy, sw=sw, cov=cov)

_COV = {'c': 0.9}

def build(d):
    """Retorna {FC: (severidade, cortes_hw, cortes_dev)}, massa, itens (com tipo HW/SW) e grupos 'similares'."""
    n, a = d['n'], d['arch']
    cv = P.COVERAGE[d.get('cov', 'c90')]
    lanes = ['COM', 'MON'] if a == 'A2' else ['COM']
    # potência
    if d['energy'] == 'common':
        pwr_hw = lambda c: OR(ev('BAT_PROP'), ev(f'DCDC_{c}'))
    else:
        pwr_hw = lambda c: ev(f'BAT_{c}')
    # software: evento de erro de desenvolvimento
    def sw(c, lane):
        return ev(f'SW_{lane}') if d['sw'] == 'common' else ev(f'SW_{lane}_{c}')
    ch = range(1, n + 1)
    mon_hw = (lambda c: [ev(f'MONHW_{c}')]) if cv['mon_rate'] > 0 else (lambda c: [])
    loss_hw = lambda c: OR(*[ev(f'FCC_{l}_{c}') for l in lanes], ev(f'ACE_{c}'), ev(f'MOT_{c}'), pwr_hw(c), *mon_hw(c))
    loss_dev = lambda c: OR(*[sw(c, l) for l in lanes], *[ev(f'FCCHW_{l}_{c}') for l in lanes], ev(f'ACEHW_{c}'))
    err_hw_src = lambda c: OR(ev(f'FCCe_COM_{c}'), ev(f'ACEe_{c}'))
    _src = lambda c: OR(sw(c, 'COM'), ev(f'FCCHW_COM_{c}'), ev(f'ACEHW_{c}'))
    err_dev_src = (lambda c: AND(_src(c), ev(f'MONHW_{c}'))) if cv['dev_indep'] else _src
    fc = {}
    if a == 'A1':
        fc['Loss'] = ('CAT',
                      OR(AND(loss_hw(1), ev('MECH')), AND(ev('MOTjam_1'), ev('CLUTCH'))),
                      set())   # erro de desenvolvimento do FBW sozinho não tira o comando (reversão)
        fc['Runaway'] = ('MAJ', err_hw_src(1), err_dev_src(1))   # 20% da superfície, piloto sobrepõe
    elif a == 'A2':
        fc['Loss'] = ('CAT', AND(*[loss_hw(c) for c in ch]), AND(*[loss_dev(c) for c in ch]))
        fc['Runaway'] = ('CAT', OR(*[AND(err_hw_src(c), ev(f'FCCe_MON_{c}')) for c in ch]),
                         OR(*[AND(err_dev_src(c), OR(sw(c, 'MON'), ev(f'FCCHW_MON_{c}'))) for c in ch]))
    else:
        fc['Loss'] = ('CAT', AND(*[loss_hw(c) for c in ch]), AND(*[loss_dev(c) for c in ch]))
        fc['Runaway'] = ('CAT', KofN(2, [err_hw_src(c) for c in ch]), KofN(2, [err_dev_src(c) for c in ch]))
    # massa
    ema = P.MASS.get('EMA_' + a, P.MASS['EMA'])
    m = n * (len(lanes) * P.MASS['FCC_LANE'] + ema + P.MASS['HARNESS'])
    m += n * (P.MASS['DCDC'] if d['energy'] == 'common' else P.MASS['BAT_DED'])
    m += n * cv['mass']
    m += (P.MASS['MECH'] + P.MASS['CLUTCH']) if a == 'A1' else 0.0
    dm = m - P.MASS['MECH']
    return fc, dm

def rate(e):
    base = e.split('_')[0]
    if base == 'BAT': return P.RATE['BAT']
    if base == 'FCCe': return P.RATE['FCC'] * P.RHO_RAW * (1 - _COV['c'])
    if base == 'ACEe': return P.RATE['ACE'] * P.RHO_RAW * (1 - _COV['c'])
    if base == 'MONHW': return _COV['mon_rate']
    if base == 'MOTjam': return P.RATE['MOT'] * P.RHO_JAM
    return P.RATE[base]

def prob(cuts): return sum(math.prod(rate(e) for e in c) for c in cuts)

# ---------- alocação de DAL ----------
LV = {'E': 0, 'D': 1, 'C': 2, 'B': 3, 'A': 4}; NM = 'EDCBA'
def item_of(e):  # SW_COM_1 -> SW_COM_1 ; FCCHW_COM_2 -> FCCHW_COM_2
    return e
def similar_key(i):  # itens replicados (mesmo projeto) recebem o mesmo DAL, como no WBS
    p = i.split('_')
    return '_'.join(p[:-1]) if p[0] in ('FCCHW', 'ACEHW', 'MONHW') else i

def allocate(dev_ffs, regime):
    """dev_ffs: lista (ffs, sev). Retorna (custo, {item: DAL}) mínimo pelas regras do regime."""
    R = P.REGIMES[regime]
    items = sorted({i for f, _ in dev_ffs for i in f})
    if not items: return 0, {}
    m = cp_model.CpModel()
    x = {i: [m.NewBoolVar('') for _ in range(5)] for i in items}; dal = {}
    for i in items: m.AddExactlyOne(x[i]); dal[i] = sum(k * x[i][k] for k in range(5))
    for f, sev in dev_ffs:
        L = LV[R['fdal'][sev]]; S = sorted(f)
        if not R['reduce'] or len(S) == 1:
            for i in S: m.Add(dal[i] >= L)
            continue
        for i in S: m.Add(dal[i] >= max(L - 2, 0))
        top = [m.NewBoolVar('') for _ in S]; m1 = [m.NewBoolVar('') for _ in S]
        for b, i in zip(top, S): m.Add(dal[i] >= L).OnlyEnforceIf(b)
        for b, i in zip(m1, S): m.Add(dal[i] >= L - 1).OnlyEnforceIf(b)
        o1, o2 = m.NewBoolVar(''), m.NewBoolVar('')
        m.AddBoolOr(top).OnlyEnforceIf(o1); m.Add(sum(m1) >= 2).OnlyEnforceIf(o2); m.AddBoolOr([o1, o2])
    groups = {}
    for i in items: groups.setdefault(similar_key(i), []).append(i)
    for g in groups.values():
        for i in g[1:]: m.Add(dal[i] == dal[g[0]])
    cost = sum((P.COST_SW if i.startswith('SW') else P.COST_HW)[NM[k]] * x[i][k] for i in items for k in range(5))
    m.Minimize(cost); s = cp_model.CpSolver(); s.parameters.num_workers = 8
    assert s.Solve(m) == cp_model.OPTIMAL
    return int(s.ObjectiveValue()), {i: NM[s.Value(dal[i])] for i in items}

# ---------- avaliação ----------
def evaluate(d, regime):
    R = P.REGIMES[regime]; cov = d.get('cov', 'c90'); _COV.update(P.COVERAGE[cov]); fc, dm = build(d)
    nm = f"{d['arch']}-{d['energy']}-{d['sw']}" if d['arch'] != 'A1' else f"A1-{d['energy']}"
    out = dict(design=f"{nm}-{cov}",
               regime=regime, dmass_kg=round(dm, 2), dendur_min=round(P.MIN_PER_KG * dm, 1))
    ok = True; dev = []
    for name, (sev, hw, dv) in fc.items():
        p = prob(hw); order = min(len(c) for c in hw)
        out[f'P_{name}'] = p; out[f'ord_{name}'] = order
        single = [sorted(c)[0] for c in hw if len(c) == 1]
        out[f'single_{name}'] = ';'.join(single)
        if p > R['target'][sev]: ok = False
        if order < R['nsev'].get(sev, 1): ok = False
        dev += [(f, sev) for f in dv]
    c, alloc = allocate(dev, regime)
    out['dal_cost'] = c
    out['dal'] = ' '.join(f'{k}={v}' for k, v in sorted(alloc.items()) if not k[-1].isdigit() or k.endswith('_1'))
    out['feasible'] = ok
    return out

def pareto(rows):
    f = [r for r in rows if r['feasible']]
    return [r for r in f if not any((o['dal_cost'] <= r['dal_cost'] and o['dmass_kg'] <= r['dmass_kg'])
                                    and (o['dal_cost'] < r['dal_cost'] or o['dmass_kg'] < r['dmass_kg']) for o in f)]

if __name__ == '__main__':
    rows = [evaluate(d, reg) for reg in P.REGIMES for d in design_space()]
    keys = ['regime', 'design', 'feasible', 'dal_cost', 'dmass_kg', 'dendur_min', 'P_Loss', 'ord_Loss',
            'single_Loss', 'P_Runaway', 'ord_Runaway', 'dal']
    w = csv.DictWriter(open('resultados.csv', 'w'), fieldnames=keys, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
    for reg in P.REGIMES:
        print(f'\n=== {reg} ===')
        rr = [r for r in rows if r['regime'] == reg]
        for r in rr:
            print(f"{r['design']:28s} {'OK ' if r['feasible'] else '-- '} cost={r['dal_cost']:5d} dm={r['dmass_kg']:+5.1f}kg "
                  f"dt={r['dendur_min']:+5.1f}min Ploss={r['P_Loss']:.1e}(o{r['ord_Loss']}{' 1:'+r['single_Loss'] if r['single_Loss'] else ''}) "
                  f"Prun={r['P_Runaway']:.1e}(o{r['ord_Runaway']})")
        print('Pareto (custo DAL x massa):', [r['design'] for r in pareto(rr)])
        for r in rr:
            if r['design'] in [p['design'] for p in pareto(rr)]: print('   ', r['design'], r['dal'])
