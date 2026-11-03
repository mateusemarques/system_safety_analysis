# system_safety_analysis

Open scripts for aircraft system safety assessment (ARP4754A/B, ARP4761/A): development assurance level (DAL) allocation, fault tree and cut-set analysis, and related studies for light electric aircraft.

| Folder | Content |
|---|---|
| `dal_allocation/coallocation_ch701` | v0 prototype: architecture, independence, DAL and mass co-allocation for a light electric aircraft FBW |
| `dal_allocation/wbs_delmas2023` | Reproduction of the cost-optimal DAL allocation of the Wheel Brake System (Delmas et al., DASC 2023) |

Requirements: Python 3.10+, `pip install -r requirements.txt`.

Third-party data (e.g. ONERA's DALculator test cases, LGPL-2.1) are downloaded by scripts and are not redistributed. SAE standards are not included.

Author: Mateus Enrique Marques.
