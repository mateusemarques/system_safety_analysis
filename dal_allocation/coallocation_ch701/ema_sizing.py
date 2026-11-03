"""Dimensionamento de 1ª ordem do EMA de profundor do CH 701 e da bateria dedicada (etapa 3, 03/11/2026).
Fontes: geometria e Ch do profundor do projeto paralelo (notes/manche_livre.md, plantas 7-H); velocidades do
POH do CH 701 (VA 71 mph, VNE 108 mph); servos GSA 28 (60 in-lb, 0,635 kg, 0,36 A típ./1,8 A máx. a 14 V) e
Dynon SV32/42/52 (36/55/72 in-lb; 0,9/1,4/1,8 kg). ASSUMIDOS: curso, alfa_t, razão da articulação, margem."""
import json, math
rho = 1.225; mph = 0.44704
VA, VNE = 71 * mph, 108 * mph
span, cf = 2.22, 0.30                     # m (plantas 7-H; cf atrás do eixo)
Se = span * cf
k3d = 3.38 / (2 * math.pi)                 # a_t / 2pi (Helmbold)
Chd = -0.63 * 0.75 * k3d                   # caso central (manche_livre)
Cha = -0.60 * 0.60 * k3d
def H(V, d_deg, at_deg):
    q = 0.5 * rho * V**2
    Ch = Chd * math.radians(d_deg) + Cha * math.radians(at_deg)
    return abs(q * Se * cf * Ch)
cases = {'VA, deflexão plena 20°, alfa_t 6° (ASSUMIDO)': H(VA, 20, 6),
         'VNE, 5°, alfa_t 3° (ASSUMIDO)': H(VNE, 5, 3)}
Hmax = max(cases.values())
k_link, margin = 2.0, 1.5                  # ASSUMIDOS: razão curso do braço/superfície e margem de torque
servo = [('Dynon SV32', 36, 0.9), ('Dynon SV42', 55, 1.4), ('Garmin GSA 28', 60, 0.635), ('Dynon SV52', 72, 1.8)]
inlb = 0.112985
def need(frac): return margin * Hmax * frac / k_link
def pick(T):
    ok = [s for s in servo if s[1] * inlb >= T]
    return min(ok, key=lambda s: s[2]) if ok else None
kg_per_Nm = 1.8 / (72 * inlb)              # escala do SV52 (extrapolação acima de 8,1 N·m)
out = {'H_casos_Nm': cases, 'H_max_Nm': Hmax}
for frac, tag in ((0.2, 'A1 (20% da superfície, TUM)'), (1.0, 'A2/A3 (canal sozinho move a superfície toda)')):
    T = need(frac); s = pick(T)
    out[tag] = dict(torque_servo_Nm=round(T, 2), servo=s[0] if s else None,
                    massa_kg=s[2] if s else round(T * kg_per_Nm, 2), extrapolado=s is None)
# bateria dedicada por canal: servo típico 0,36 A e máx. 1,8 A a 14 V; FCC 5 W (ASSUMIDO); 1 h + 30 min (ASSUMIDO)
P_typ, P_max = 0.36 * 14 + 5, 1.8 * 14 + 5
E = P_typ * 1.5; e_pack = 90                # Wh/kg do pack LiFePO4 (ASSUMIDO)
out['bateria_dedicada'] = dict(P_tip_W=P_typ, P_max_W=P_max, E_Wh=E, massa_kg=round(E / e_pack + 0.1, 2),
                               nota='+0,1 kg de caixa/BMS (ASSUMIDO); dimensionado pela potência típica')
json.dump(out, open('dimensionamento_ema.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
