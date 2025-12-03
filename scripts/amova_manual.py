#!/usr/bin/env python
import argparse
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from pathlib import Path
import re

def main():
    parser = argparse.ArgumentParser(
        description="AMOVA simple basada en distancias euclidianas entre individuos."
    )
    parser.add_argument(
        "--input",
        default="../data/Input_Naturales_1row.csv",
        help="CSV de genotipos (1 fila por SNP). Por defecto: ../data/Input_Naturales_1row.csv",
    )
    args = parser.parse_args()

    csv_path = Path(args.input)
    print(f"Usando archivo de entrada para AMOVA: {csv_path}")

    df = pd.read_csv(csv_path)
    samples = list(df.columns[1:])

    geno_df = df[samples].replace("-", np.nan)
    mask_valid = ~geno_df.isna().all(axis=1)
    geno_df = geno_df[mask_valid].copy()
    geno = geno_df.astype(float).to_numpy()

    print(f"SNPs totales en archivo: {df.shape[0]}")
    print(f"SNPs después de eliminar filas todo-missing: {geno.shape[0]}")

    snp_means = np.nanmean(geno, axis=1)
    for i in range(geno.shape[0]):
        mask_row = np.isnan(geno[i])
        geno[i, mask_row] = snp_means[i]

    dist_vec = pdist(geno.T, metric="euclidean")
    dist_mat = squareform(dist_vec)

    groups = {}
    for s in samples:
        m = re.search(r"(\d+)", s)
        if not m:
            raise ValueError(f"No pude extraer número de la etiqueta de individuo: {s}")
        n = int(m.group(1))

        if 101 <= n <= 114:
            groups[s] = "Grupo1"
        elif 115 <= n <= 129:
            groups[s] = "Grupo2"
        else:
            raise ValueError(f"Individuo {s} tiene número {n} fuera de rango 101–129 (ajusta la lógica en amova_manual.py).")

    group_labels = np.array([groups[s] for s in samples])
    unique_groups = np.unique(group_labels)

    print("\nIndividuos y grupos asignados:")
    for s in samples:
        print(f"{s}: {groups[s]}")

    grand_mean = np.mean(dist_mat)
    SS_total = np.sum((dist_mat - grand_mean) ** 2)

    SS_within = 0.0
    for g in unique_groups:
        idx = np.where(group_labels == g)[0]
        submat = dist_mat[np.ix_(idx, idx)]
        mean_g = np.mean(submat)
        SS_within += np.sum((submat - mean_g) ** 2)

    SS_between = SS_total - SS_within
    phi_ST = SS_between / SS_total

    n_perm = 999
    perm_stats = []
    rng = np.random.default_rng(seed=123)

    for _ in range(n_perm):
        permuted = rng.permutation(group_labels)
        SS_within_perm = 0.0

        for g in unique_groups:
            idx = np.where(permuted == g)[0]
            submat = dist_mat[np.ix_(idx, idx)]
            mean_g = np.mean(submat)
            SS_within_perm += np.sum((submat - mean_g) ** 2)

        SS_between_perm = SS_total - SS_within_perm
        perm_phi = SS_between_perm / SS_total
        perm_stats.append(perm_phi)

    perm_stats = np.array(perm_stats)
    p_value = np.mean(perm_stats >= phi_ST)

    print("\n===== RESULTADOS AMOVA MANUAL =====")
    print(f"ΦST (Phi_ST): {phi_ST:.6f}")
    print(f"P-value (perm {n_perm}): {p_value:.6f}")
    print(f"SS_total: {SS_total:.3f}")
    print(f"SS_within: {SS_within:.3f}")
    print(f"SS_between: {SS_between:.3f}")

if __name__ == "__main__":
    main()
