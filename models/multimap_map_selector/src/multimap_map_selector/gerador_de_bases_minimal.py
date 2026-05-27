"""Minimal pure-Python generator for synthetic map datasets.

This script mirrors the behavior of the pandas-based generator but uses only
stdlib modules so it can run without installing additional packages.

It writes the following CSV files to the current working directory:
- 1_mapa_coropletico.csv
- 2_mapa_simbolos_proporcionais.csv
- 3_mapa_densidade_pontos.csv
- 4_mapa_calor_hexbin.csv
- 5_mapa_small_multiples.csv

Run from the repository root:

    python3 models/multimap_map_selector/src/multimap_map_selector/gerador_de_bases_minimal.py

"""

from __future__ import annotations

import csv
import random
from math import floor
from pathlib import Path

random.seed(42)

anos = list(range(2010, 2027))
sexos = ["Homens", "Mulheres"]
idades = [
    "00 a 04",
    "05 a 09",
    "10 a 14",
    "15 a 19",
    "20 a 24",
    "25 a 29",
    "30 a 34",
    "35 a 39",
    "40 a 44",
    "45 a 49",
    "50 a 54",
    "55 a 59",
    "60 a 64",
    "65 a 69",
    "70 a 74",
    "75 a 79",
    "80 e mais",
]

n_distritos = 96
codigos_distr = list(range(80001, 80001 + n_distritos))
nomes_distr = [f"Distrito Sintético {i}" for i in range(1, n_distritos + 1)]

lat_base, lon_base = -23.55, -46.63
lats_distr = [lat_base + random.gauss(0, 0.05) for _ in range(n_distritos)]
lons_distr = [lon_base + random.gauss(0, 0.05) for _ in range(n_distritos)]

cwd = Path.cwd()

# 1. Raw-like table (not written to disk explicitly, but used to compute others)
rows_raw = []
for ano in anos:
    for i in range(n_distritos):
        for sexo in sexos:
            for idade in idades:
                pop = random.randint(500, 5000)
                if any(x in idade for x in ("60", "65", "70", "75", "80")):
                    pop = int(pop * random.uniform(0.3, 0.8))
                rows_raw.append((codigos_distr[i], nomes_distr[i], ano, sexo, idade, pop))

# 2. Coropleth: aggregate totals and elderly counts per (cod_distr, nome_distr, ano)
pop_total = {}
pop_idosa = {}
for cod, nome, ano, sexo, idade, pop in rows_raw:
    key = (cod, nome, ano)
    pop_total[key] = pop_total.get(key, 0) + pop
    if idade in ("60 a 64", "65 a 69", "70 a 74", "75 a 79", "80 e mais"):
        pop_idosa[key] = pop_idosa.get(key, 0) + pop

coropletico_rows = []
for key, total in pop_total.items():
    idd = key[0]
    nome = key[1]
    ano = key[2]
    idosos = pop_idosa.get(key, 0)
    taxa = round((idosos / total) * 100, 2) if total > 0 else 0.0
    leitos = round(random.uniform(0.5, 5.0), 2)
    coropletico_rows.append((idd, nome, ano, total, idosos, taxa, leitos))

with open(cwd / '1_mapa_coropletico.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['cod_distr', 'nome_distr', 'ano', 'populacao_total', 'populacao_idosa', 'taxa_envelhecimento_perc', 'leitos_por_mil_hab'])
    for row in coropletico_rows:
        writer.writerow(row)

# 3. Proportional symbols
with open(cwd / '2_mapa_simbolos_proporcionais.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['cod_distr', 'nome_distr', 'latitude', 'longitude', 'total_centros_saude_idosos', 'atendimentos_totais_ano'])
    for i, cod in enumerate(codigos_distr):
        writer.writerow([
            cod,
            nomes_distr[i],
            f'{lats_distr[i]:.6f}',
            f'{lons_distr[i]:.6f}',
            random.randint(1, 11),
            random.randint(5000, 50000),
        ])

# 4. Density points (using latest year)
with open(cwd / '3_mapa_densidade_pontos.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['cod_distr', 'nome_distr', 'populacao_idosa'])
    for key, idosos in pop_idosa.items():
        cod, nome, ano = key
        if ano == anos[-1]:
            writer.writerow([cod, nome, idosos])

# 5. Heatmap / hexbin synthetic microdata
n_ocorrencias = 50000
with open(cwd / '4_mapa_calor_hexbin.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['id_atendimento', 'latitude_ocorrencia', 'longitude_ocorrencia', 'idade_paciente', 'tempo_deslocamento_min'])
    for i in range(1, n_ocorrencias + 1):
        lat = lat_base + random.gauss(0, 0.08)
        lon = lon_base + random.gauss(0, 0.08)
        idade_paciente = random.randint(60, 94)
        tempo = round(random.gammavariate(2.0, 15.0), 1)
        writer.writerow([i, f'{lat:.6f}', f'{lon:.6f}', idade_paciente, tempo])

# 6. Small multiples
with open(cwd / '5_mapa_small_multiples.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['cod_distr', 'nome_distr', 'ano', 'taxa_envelhecimento_perc', 'leitos_por_mil_hab', 'cobertura_esf_perc', 'indice_vulnerabilidade'])
    for idd, nome, ano, total, idosos, taxa, leitos in coropletico_rows:
        cobertura = round(random.uniform(30, 95), 2)
        indice = round(random.uniform(0.1, 0.9), 3)
        writer.writerow([idd, nome, ano, taxa, leitos, cobertura, indice])

print('Feito! Os 5 arquivos CSV foram gerados com sucesso na pasta atual:', cwd)
