#!/usr/bin/env python
import argparse
import numpy as np
import pandas as pd
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Convertir CSV 1-row por SNP a formato STRUCTURE (.str), filtrando loci todo-missing."
    )
    parser.add_argument(
        "--input",
        default="../data/Input_Naturales_1row.csv",
        help="Ruta al CSV de entrada (1 fila por SNP). Por defecto: ../data/Input_Naturales_1row.csv",
    )
    parser.add_argument(
        "--output-prefix",
        default="nat_filtrado",
        help="Prefijo de salida para el archivo .str (sin extensión). Por defecto: nat_filtrado",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_prefix = args.output_prefix
    output_path = Path(f"{output_prefix}.str")

    print(f"Usando archivo de entrada: {input_path}")
    print(f"Archivo .str de salida:   {output_path}")

    df = pd.read_csv(input_path)

    # Columnas de individuos (todas excepto 'Mark')
    sample_cols = [c for c in df.columns if c != "Mark"]

    # Genotipos como numpy
    geno = df[sample_cols].replace("-", np.nan).astype(float).to_numpy()

    n_loci, n_samples = geno.shape
    print(f"SNPs totales (loci): {n_loci}")
    print(f"Individuos: {n_samples}")

    # Eliminar loci donde TODOS los individuos son missing
    mask_valid = ~np.isnan(geno).all(axis=1)
    geno = geno[mask_valid, :]
    n_loci_valid = geno.shape[0]

    print(f"SNPs después de filtrar todo-missing: {n_loci_valid}")

    # Construir archivo .str: 2 filas por individuo
    str_rows = []
    POP_ID = "1"

    for j, sample in enumerate(sample_cols):
        g = geno[:, j]

        row1_alleles = []
        row2_alleles = []

        for val in g:
            if np.isnan(val):
                # ambos alelos missing
                row1_alleles.append("-9")
                row2_alleles.append("-9")
            else:
                # asumiendo codificación 0,1,2 (0=homoz ref, 1=hetero, 2=homoz alt)
                val_int = int(val)
                if val_int == 0:
                    a1, a2 = "0", "0"
                elif val_int == 1:
                    a1, a2 = "0", "1"
                elif val_int == 2:
                    a1, a2 = "1", "1"
                else:
                    a1, a2 = "-9", "-9"

                row1_alleles.append(a1)
                row2_alleles.append(a2)

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
