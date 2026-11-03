import wbs_dal as w
from ortools.sat.python import cp_model
P={1:dict(Accumulator='D',Alt_EmerMeterValve_L='A',Alt_EmerMeterValve_R='A',CCF_HW_COM_MON_Incorrect='A',CCF_HW_COM_MON_Loss='A',CCF_SW_COM_Incorrect='C',CCF_SW_COM_Loss='C',CCF_SW_MON_Incorrect='A',CCF_SW_MON_Loss='A',Command1='C',Command2='C',ElectricalBrakeUnit='A',HYD1='B',HYD2='B',InternalPower1='C',InternalPower2='C',IsolationValve1='C',IsolationValve2='C',Monitor1='A',Monitor2='A',PWR1='C',PWR2='C',PowerMonitor1='A',PowerMonitor2='A',Selection_Mgt='A',SelectorValve='B',ShutOff_Valve='B')}
P[2]={k:v for k,v in zip(P[1],'C B B A A B B B B B B A B B B B C C B B B B B B B C D'.split())}
P[3]={k:v for k,v in zip(P[1],'C B B A A C C A A C C A B B C C C C A A C C A A A C D'.split())}
LV=w.LV
def cost(a): return sum(w.costs.get(i,{}).get(LV[a[i]],0) for i in a)
def viol(a,rule):
    bad=[]
    for f,L in w.ffs:
        S=sorted(f); d=[LV[a[i]] for i in S]
        if len(S)==1: ok=d[0]>=L
        else:
            fl=all(x>=L-2 for x in d); o1=any(x>=L for x in d); o2=sum(x>=L-1 for x in d)>=2
            ok=fl and (o1 if rule==1 else o2 if rule==2 else (o1 or o2))
        if not ok: bad.append((S,L))
    for x,op,y,it in w.cons:
        r=LV[a[y]] if it else LV[y]; l=LV[a[x]]
        if not {'Eq':l==r,'Ge':l>=r,'Lt':l<r}[op]: bad.append((x,op,y))
    return bad
for r in (1,2,3):
    b=viol(P[r],r); print(r,'custo',cost(P[r]),'violações',len(b),b[:4])
