# Architecture x independence x monitor coverage x DAL x mass co-allocation

**v0.1, 2026-11-03.** Research prototype with declared assumptions. It is not a safety assessment. (v0 = tag `coallocation-v0`.)

Light electric aircraft (Zenith CH 701, electric conversion), pitch control. The design space is enumerated exactly:

| Variable | Options |
|---|---|
| Architecture | A1 hybrid FBW in the manner of TUM (about 20% of the surface on an EMA, mechanical reversion, clutch); A2 duplex COM/MON; A3 triplex with voting |
| Energy | propulsion battery shared through DC/DC, or a dedicated battery per channel |
| Software | common or dissimilar (A2/A3) |
| Monitor coverage (new in v0.1) | c90 (BIT/watchdog), c99 (+ surface position sensor and ACE monitor), c999 (+ dissimilar authority-envelope monitor, counted as an independent item in the DAL allocation) |

That gives 30 designs. Undetected erroneous rate = lambda x rho_raw x (1 - c). Higher coverage adds mass and monitor failure rate, and a monitor failure passivates the channel.

For each design and regime (AC 23.1309-1E Class I, SC-VTOL Basic, SC-VTOL Enhanced) the code builds the hardware and development-error minimal cut sets, computes probability per flight hour (T = 1 h) and the minimum cut order, allocates DAL with CP-SAT (fixed DAL in Class I and Basic, ARP4754A Table 3 in Enhanced, with the Baron and Louis 2021 weights), and reports the mass increment, the endurance change and the cost x mass Pareto set.

```bash
pip install -r ../../requirements.txt
python3 coalloc.py      # base case
python3 sens.py         # one-at-a-time sensitivity
python3 sens_fontes.py  # scenarios with public-source rates
python3 sens_cov.py     # coverage as a design variable under rho_raw and FCC/ACE rate scenarios
python3 ema_sizing.py   # first-order pitch EMA sizing (hinge moment, servo, dedicated battery)
```

## Parameters and sources
- Battery, DC/DC, motor controller, motor: NASA/CR-2019-220217 (Darmstadt et al., 2019).
- Mechanical pitch control (A1 reversion): 7.44e-6/h, the hazard rate at t = 6 h for the longitudinal control system of complex GA aircraft in NASA/CR-2001-210647 (Pettit and Turnbull, 2001; Weibull beta 1.57, alpha 4718 h). The mean of 4188 h (about 2.4e-4/h) is used as the upper bound. Both are maintenance-record failures, not in-flight loss.
- Clutch: NSWC-11 (2011) solenoid base rate, 2.77 per 10^6 operations, with one demand per flight hour assumed.
- rho_raw = 0.438: the "spurious position change" share in the generic "Actuator" example of the FMD-2016 free sample. This is a weak source.
- EMA mass: Garmin GSA 28 (0.635 kg) for A1. For A2/A3, 2.23 kg is extrapolated from the Dynon SV52 scale, because a single channel needs about 10 N·m at the servo.
- Dedicated battery: about 15 Wh, LiFePO4 at 90 Wh/kg + 0.1 kg (assumed).
- Coverage masses and monitor rates, the FCC rate, the jam fraction and the harness/DC-DC/FCC masses are assumptions (see `params.py`).

## Preliminary findings (v0.1)
1. Shared propulsion battery in full FBW (A2/A3) is an order-1 cut (about 9e-5/h) and is infeasible in every regime.
2. A dedicated channel battery (about 0.27 kg) is lighter than the DC/DC it replaces, so energy segregation costs no mass here.
3. Class I Pareto set: {A1 dedicated battery, A2 dedicated battery with common SW}, unchanged by every public-rate scenario.
4. Enhanced: with the NASA mechanical rate, A1 is infeasible (loss about 7e-8 to 1e-7/h) and triplex with dedicated batteries is selected.
5. Coverage: c90 suffices at current rates. c99 is needed only when FCC/ACE rates triple (A1 in Basic; A3 in Enhanced with rho_raw = 1), at about 0.1 kg per channel.
6. Dissimilar software and the dissimilar monitor (c999) are never optimal: common software is a single-member cut of total loss, so it stays at DAL A in Enhanced anyway.
7. A2 fails Basic and Enhanced on loss (about 1e-7/h), not on runaway, and coverage does not change that.

## Known limitations
- Clutch command development errors, latent monitor failures and exposure times are not modelled.
- Class I primary/secondary levels (S = D) are not used.
- EMA power in the endurance model and zonal/thermal-runaway effects are not modelled yet.
- The architecture choice is enumerated rather than encoded inside the solver.
