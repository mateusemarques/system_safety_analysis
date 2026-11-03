# WBS DAL allocation: reproduction of Delmas et al. (DASC 2023), Table VI

Independent re-implementation, in Python with OR-Tools CP-SAT, of the cost-optimal DAL allocation for the ARP4761 Wheel Brake System. The rules are those of ARP4754A Table 3 (Option 1, Option 2 and both combined), with full independence between members and the user constraints of the original study.

```bash
./fetch_data.sh            # cut sets and costs from onera/dalculator (LGPL-2.1, not redistributed here)
python3 wbs_dal.py data 3  # order <= 3; use 4 for order <= 4
python3 check_paper.py     # checks the allocation printed in Table VI against the model
```

## Results
| Rule | Published total cost | This model (order 3 and 4) |
|---|---|---|
| Option 1 | 12356 | 12356 |
| Option 2 | 13055 | 13055 |
| Combined | 12260 | 12260 |

- Item-level differences from Table VI are alternative optima of equal cost: Command and Monitor items have zero cost, and CCF_SW_COM and CCF_SW_MON have identical costs.
- In Option 1 as printed, IsolationValve1/2 at C violates three order-3 cut sets of Loss of Braking (HAZ, DAL B). With B, the allocation is feasible and its cost is 12356, the published total. This is probably a typo in the table; not confirmed with the authors.

## References
- K. Delmas, L. Chambert, C. Frazza, C. Seguin. Optimization of Development Assurance Level Allocation. IEEE/AIAA DASC 2023. HAL hal-04313961.
- P. Bieber, R. Delmas, C. Seguin. DALculus: theory and tool for development assurance level allocation. SAFECOMP 2011.
- ONERA DALculator: https://github.com/onera/dalculator
