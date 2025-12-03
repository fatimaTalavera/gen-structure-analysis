#!/usr/bin/env python
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Generar gráfico STRUCTURE (barplot apilado) a partir de un archivo .meanQ."
    )
    parser.add_argument(
        "--meanq",
        required=True,
        help="Ruta al archivo .meanQ generado por ezstructure/fastStructure.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Ruta del archivo PNG de salida.",
    )
    parser.add_argument(
        "--csv",
        default="../data/Input_Naturales_1row.csv",
        help="CSV original para obtener nombres de individuos (por defecto: Input_Naturales_1row.csv).",
    )
    args = parser.parse_args()

    meanq_path = Path(args.meanq)
    output_path = Path(args.output)
    csv_path = Path(args.csv)

    print(f"Usando .meanQ: {meanq_path}")
    print(f"Usando CSV:    {csv_path}")
    print(f"Salida PNG:    {output_path}")

    df_csv = pd.read_csv(csv_path)
    samples = [c for c in df_csv.columns if c != "Mark"]

    Q = np.loadtxt(meanq_path)
    print("Forma de Q:", Q.shape)
    print("Número de individuos:", len(samples))

    if Q.shape[0] != len(samples):
        raise ValueError("El número de filas de Q no coincide con el número de individuos del CSV.")

    K = Q.shape[1]
    df_Q = pd.DataFrame(Q, columns=[f"Cluster_{i+1}" for i in range(K)])
    df_Q["individuo"] = samples
    df_Q.set_index("individuo", inplace=True)

    plt.figure(figsize=(12, 4))
    df_Q.plot(kind="bar", stacked=True, legend=True)

    plt.ylabel("Proporción de ancestría")
    plt.xlabel("Individuos")
    plt.ylim(0, 1)
    plt.xticks(rotation=90, fontsize=6)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)
    print(f"Gráfico guardado en {output_path}")

if __name__ == "__main__":
    main()
