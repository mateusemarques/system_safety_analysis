# Architecture x independence x DAL x mass co-allocation, v0 prototype

**v0, 2026-11-03.** First prototype, with declared placeholders. It is research code, not a safety assessment.

Light electric aircraft (Zenith CH 701, electric conversion), pitch control. The design space is enumerated exactly:

| Architecture | Description |
|---|---|
| A1 | Hybrid FBW in the manner of TUM (about 20% of the surface on an EMA, mechanical reversion, clutch) |
| A2 | Duplex FBW, each channel COM/MON |
| A3 | Triplex FBW with voting |

Each architecture is combined with an energy option (propulsion battery shared through DC/DC, or a dedicated battery per channel) and a software option (common or dissimilar), for 10 designs in total.

For each design and regulatory regime (AC 23.1309-1E Class I, SC-VTOL Basic, SC-VTOL Enhanced) the code:
- builds hardware and development-error minimal cut sets from the architecture pattern;
- computes the rare-event probability per flight hour (T = 1 h) and the minimum cut order (no single failure catastrophic);
- allocates DAL with CP-SAT: fixed DAL with no architectural reduction in Class I and Basic, and ARP4754A Table 3 Options 1/2 in Enhanced, with Baron and Louis (2021) cost weights as in Delmas et al. (2023);
- reports the mass increment versus the mechanical controls, the endurance change (-0.5 min per kg, from the CH 701 retrofit model) and the cost x mass Pareto set.

```bash
pip install -r ../../requirements.txt
python3 coalloc.py   # base case
python3 sens.py      # sensitivity on mechanical, FCC, erroneous-fraction and battery rates
```

## Parameters
Rates for the battery, DC/DC, motor controller and motor come from NASA/CR-2019-220217 (Darmstadt et al., 2019). Every value marked PLACEHOLDER in `params.py` is a working assumption: the FCC rate, the mechanical and clutch rates, the erroneous and jam fractions, and every mass except the 6.7 kg of mechanical controls.

## Preliminary findings (v0)
1. Robust: in full FBW (A2/A3) with the shared propulsion battery, the battery is an order-1 cut (about 9e-5/h). These designs are infeasible in every regime and every sensitivity case, and no DAL allocation or software dissimilarity removes the cut.
2. Robust: dissimilar software is never Pareto-optimal, even in Enhanced.
3. Robust: in Class I, the Pareto set is always {A1 with shared battery, A2 with dedicated batteries and common software}.
4. Placeholder-dependent: in Basic and Enhanced, the choice depends on the mechanical-reversion rate, the FCC rate and the erroneous fraction.

## Known limitations
- Development errors of the clutch command (the critical function in the TUM concept) are not modelled.
- Class I primary/secondary levels (S = D) are not used.
- EMA power draw and zonal effects are not modelled yet.
- The architecture choice is enumerated rather than encoded inside the solver.
