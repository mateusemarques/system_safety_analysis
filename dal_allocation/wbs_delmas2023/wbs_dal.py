"""Reprodução da alocação de DAL do WBS (Delmas et al., DASC 2023, Tab. VI)
com os cortes mínimos e custos públicos do DALCULATOR (github.com/onera/dalculator,
src/test/resources/arpModel, LGPL-2.1). Regras: ARP4754A Tabela 3 (Opção 1, 2, combinada).
DAL codificado E=0, D=1, C=2, B=3, A=4. Independência total por padrão (hipótese do DALCULATOR)."""
import re, sys, itertools
from ortools.sat.python import cp_model

LV = {'E':0,'D':1,'C':2,'B':3,'A':4}; NM = 'EDCBA'
D = sys.argv[1] if len(sys.argv) > 1 and __name__ == "__main__" else "data"
ORDER = sys.argv[2] if len(sys.argv) > 2 and __name__ == "__main__" else "3"

def item(ev):  # 'Command1.Loss' -> 'Command1'; eventos CCF são itens próprios
    return ev.split('.')[0]

def read_seq(path):
    ffs = []
    for line in open(path):
        line = line.strip()
        if line.startswith('{'):
            evs = re.findall(r"'([^']+)'", line)
            ffs.append(frozenset(item(e) for e in evs))
    return ffs

def read_costs(path):
    c = {}
    for m in re.finditer(r"Cost\('([^']+)',\s*([EDCBA])\)\s*=\s*(\d+)", open(path).read()):
        c.setdefault(m.group(1), {})[LV[m.group(2)]] = int(m.group(3))
    return c

def read_cons(path):
    out = []
    for line in open(path):
        m = re.match(r"Dal\('([^']+)'\s+(Eq|Ge|Lt)\s+('?)([^')]+)'?\)", line.strip())
        if m: out.append((m.group(1), m.group(2), m.group(4), m.group(3) == "'"))
    return out

FC = {'Loss': ('ARP_Loss_%s.seq' % ORDER, LV['B']), 'Untimely': ('ARP_Untimely_%s.seq' % ORDER, LV['A'])}
ffs = [(f, L) for k, (p, L) in FC.items() for f in read_seq(f'{D}/{p}')]
costs = read_costs(f'{D}/costs.udef'); cons = read_cons(f'{D}/constraints.udef')
items = sorted(set().union(*[f for f, _ in ffs]) | set(costs))

def solve(rule):
    m = cp_model.CpModel()
    x = {i: [m.NewBoolVar(f'{i}_{d}') for d in range(5)] for i in items}
    dal = {}
    for i in items:
        m.AddExactlyOne(x[i]); dal[i] = sum(d * x[i][d] for d in range(5))
    for f, L in ffs:
        S = sorted(f)
        if len(S) == 1:
            m.Add(dal[S[0]] >= L); continue
        for i in S: m.Add(dal[i] >= max(L - 2, 0))
        # o1: algum membro no nível de topo; o2: dois membros em L-1
        ge_top = [m.NewBoolVar('') for _ in S]; ge_m1 = [m.NewBoolVar('') for _ in S]
        for b, i in zip(ge_top, S): m.Add(dal[i] >= L).OnlyEnforceIf(b)
        for b, i in zip(ge_m1, S): m.Add(dal[i] >= L - 1).OnlyEnforceIf(b)
        o1 = m.NewBoolVar(''); o2 = m.NewBoolVar('')
        m.AddBoolOr(ge_top).OnlyEnforceIf(o1)
        m.Add(sum(ge_m1) >= 2).OnlyEnforceIf(o2)
        if rule == 1: m.Add(o1 == 1)
        elif rule == 2: m.Add(o2 == 1)
        else: m.AddBoolOr([o1, o2])
    for a, op, b, is_item in cons:
        rhs = dal[b] if is_item else LV[b]
        if op == 'Eq': m.Add(dal[a] == rhs)
        elif op == 'Ge': m.Add(dal[a] >= rhs)
        else: m.Add(dal[a] < rhs)
    cost = sum(costs.get(i, {}).get(d, 0) * x[i][d] for i in items for d in range(5))
    m.Minimize(cost)
    s = cp_model.CpSolver(); s.parameters.num_workers = 8
    st = s.Solve(m)
    return s.StatusName(st), int(s.ObjectiveValue()), {i: NM[s.Value(dal[i])] for i in items}

if __name__ == '__main__':
    print(f'FFS: {len(ffs)} (ordem <= {ORDER}); itens: {len(items)}')
    res = {r: solve(r) for r in (1, 2, 3)}
    for r, (st, c, _) in res.items(): print(f'regra {r}: {st}, custo {c}')
    print('item'.ljust(28), 'Op1 Op2 Comb')
    for i in items: print(i.ljust(28), '  '.join(res[r][2][i] for r in (1, 2, 3)))
