#!/usr/bin/env bash
# Baixa os cortes mínimos, custos e restrições do WBS do repositório da ONERA (LGPL-2.1).
set -e; mkdir -p data; B=https://raw.githubusercontent.com/onera/dalculator/main/src/test/resources/arpModel
for f in sequences/ARP_Loss_3.seq sequences/ARP_Loss_4.seq sequences/ARP_Untimely_3.seq sequences/ARP_Untimely_4.seq userConstraints/constraints.udef userConstraints/costs.udef; do curl -sfL -o data/$(basename $f) $B/$f; done
