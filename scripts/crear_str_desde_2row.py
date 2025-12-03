#!/usr/bin/env python
import argparse
import numpy as np
import pandas as pd
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Convertir CSV 2-row por SNP a formato STRUCTURE (.str)."
    )
    parser.add_argument(
        "--input",
        default="../data/input_2row_fil.csv",
        help="Ruta al CSV 2-row por SNP. Por defecto: ../data/input_2row_fil.csv",
    )
    parser.add_argument(
        "--output-prefix",
        default="2row",
        help="Prefijo de salida para el archivo .str (sin extensión). Por defecto: 2row",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_prefix = args.output_prefix
    output_path = Path(f"{output_prefix}.str")

    print(f"Usando archivo de entrada: {input_path}")
    print(f"Archivo .str de salida:   {output_path}")

    df = pd.read_csv(input_path)
    sample_cols = [c for c in df.columns if c != "Mark"]

    geno = df[sample_cols].replace("-", np.nan).astype(float).to_numpy()
    n_rows, n_samples = geno.shape

    if n_rows % 2 != 0:
        raise ValueError("El número de filas no es par: el formato 2-row por SNP requiere pares exactos.")

    n_loci = n_rows // 2
    print(f"Filas totales: {n_rows}")
    print(f"SNPs (loci) brutos: {n_loci}")
    print(f"Individuos: {n_samples}")

    allele1 = geno[0::2, :]
    allele2 = geno[1::2, :]

    # loci con al menos un genotipo no missing
    valid_mask = (~np.isnan(allele1)) | (~np.isnan(allele2))
    loci_keep = valid_mask.any(axis=1)

    allele1 = allele1[loci_keep, :]
    allele2 = allele2[loci_keep, :]

    n_loci_valid = allele1.shape[0]
    print(f"Loci después de filtrar todo-missing: {n_loci_valid}")

    str_rows = []
    POP_ID = "1"

    for j, sample in enumerate(sample_cols):
        a1_vec = allele1[:, j]
        a2_vec = allele2[:, j]

        row1_alleles = []
        row2_alleles = []

        for v1, v2 in zip(a1_vec, a2_vec):
            if np.isnan(v1):
                row1_alleles.append("-9")
            else:
                row1_alleles.append(str(int(v1)))

            if np.isnan(v2):
                row2_alleles.append("-9")
            else:
                row2_alleles.append(str(int(v2)))

        meta = [sample, "0", "0", "0", "0", POP_ID]
        row1 = meta + row1_alleles
        row2 = meta + row2_alleles

        str_rows.append(row1)
        str_rows.append(row2)

    with open(output_path, "w") as f:
        for row in str_rows:
            f.write("\t".join(row) + "\n")

    print("Listo.")
    print(f"Loci en .str: {n_loci_valid}")
    print(f"Filas en .str (2 por individuo): {len(str_rows)}")

if __name__ == "__main__":
    main()
