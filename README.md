# Genotype Structure & AMOVA Pipeline

Este repositorio contiene el flujo de trabajo completo para:

1. Convertir archivos de genotipos (`.csv`) a formato **STRUCTURE (`.str`)**.
2. Ejecutar **ezstructure/fastStructure** para inferir clusters genéticos.
3. Generar gráficos de barras de ancestría (estilo STRUCTURE).
4. Realizar un análisis **AMOVA** sencillo en Python para evaluar estructura poblacional entre dos grupos.

La estructura está pensada para datos de individuos (`g101BR`–`g129BR`), pero los scripts permiten reutilizarse con otros archivos ubicados en la carpeta `data/`.

---

## 1. Estructura sugerida del repositorio

```text
gen-structure-analysis/
├─ data/
│  ├─ Input_Naturales_1row.csv
│  ├─ input_2row_fil.csv
├─ scripts/
│  ├─ crear_str_desde_1row_filtrado.py
│  ├─ crear_str_desde_2row.py
│  ├─ plot_structure.py
│  ├─ amova_manual.py
├─ env/
│  └─ (opcional: notas sobre pyenv / venv)
├─ requirements.txt
├─ README.md
```

---

## 2. Preparación del entorno

Los scripts están probados con **Python 3.11** en Linux/WSL.

### 2.1. Instalar pyenv (opcional pero recomendado)

```bash
# Dependencias para compilar Python
sudo apt update
sudo apt install -y   build-essential curl git libssl-dev zlib1g-dev libbz2-dev   libreadline-dev libsqlite3-dev wget llvm libncursesw5-dev   xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# Instalar pyenv
curl https://pyenv.run | bash
```

Agregar al final de `~/.bashrc`:

```bash
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Recargar el shell:

```bash
source ~/.bashrc
```

Instalar Python 3.11 (ejemplo 3.11.9) y usarlo en el proyecto:

```bash
cd gen-structure-analysis
pyenv install 3.11.9
pyenv local 3.11.9
```

### 2.2. Crear y activar un entorno virtual

```bash
cd gen-structure-analysis

# Crear entorno virtual
python -m venv venv311

# Activar entorno
source venv311/bin/activate    # Linux / WSL / macOS
# venv311\Scripts\activate   # Windows (PowerShell / CMD)
```

Cuando el entorno está activo, el prompt muestra algo como `(venv311)`.

### 2.3. Instalar dependencias

Crear un fichero `requirements.txt` con, por ejemplo:

```text
numpy<2
pandas
matplotlib
scipy
cython
ezstructure
```

Instalar todo:

```bash
pip install -r requirements.txt
```

> **Nota:** `ezstructure` es un wrapper moderno de `fastStructure`. Puede compilar extensiones en C, así que la instalación puede tardar un poco.

---

## 3. Archivos de entrada

Colocar los CSV originales en la carpeta `data/`:

- `data/Input_Naturales_1row.csv`  
  - Formato: **una fila por SNP**  
  - Columnas: `Mark`, `g101BR`, `g102BR`, ..., `g129BR`  
  - Genotipos codificados como `0`, `1`, `2` o `-` (missing).

- `data/input_2row_fil.csv`  
  - Formato: **dos filas por SNP** (alelo 1 y alelo 2).  
  - Columnas: `Mark`, `g101BR`, `g102BR`, ..., `g129BR`  
  - Valores: `0`, `1` o `NaN` / `-` para missing.

Los scripts permiten usar otros archivos siempre que respeten este esquema de columnas.

---

## 4. Scripts

Todos los scripts se ubican en la carpeta `scripts/`. A continuación se describe qué hace cada uno y sus parámetros.

### 4.1. `crear_str_desde_1row_filtrado.py`

Convierte un archivo **1-row por SNP** a formato STRUCTURE (`.str`), filtrando SNPs donde todos los individuos están en missing.

#### Uso básico (por defecto con el archivo original)

```bash
cd scripts
python crear_str_desde_1row_filtrado.py
```

- Entrada por defecto: `../data/Input_Naturales_1row.csv`
- Salida por defecto: `nat_filtrado.str` (en `scripts/`)

#### Uso con archivo alternativo

```bash
python crear_str_desde_1row_filtrado.py   --input ../data/otro_archivo_1row.csv   --output-prefix otro_prefix
```

Genera: `otro_prefix.str`

### 4.2. `crear_str_desde_2row.py`

Convierte un archivo **2-row por SNP** a `.str`, usando directamente las dos filas como alelo 1 y alelo 2.

#### Uso básico

```bash
cd scripts
python crear_str_desde_2row.py
```

- Entrada por defecto: `../data/input_2row_fil.csv`
- Salida por defecto: `2row.str`

#### Uso con archivo alternativo

```bash
python crear_str_desde_2row.py   --input ../data/otro_archivo_2row.csv   --output-prefix otro2row
```

Genera: `otro2row.str`

### 4.3. Ejecución de ezstructure/fastStructure

Una vez creado el `.str`, desde `scripts/` se puede ejecutar, por ejemplo:

```bash
# Para el archivo 1-row filtrado
ezstructure -K 2 --input nat_filtrado --output nat_k2 --format str
ezstructure -K 3 --input nat_filtrado --output nat_k3 --format str
ezstructure -K 4 --input nat_filtrado --output nat_k4 --format str

# Para el archivo 2-row
ezstructure -K 2 --input 2row --output 2row_k2 --format str
ezstructure -K 3 --input 2row --output 2row_k3 --format str
ezstructure -K 4 --input 2row --output 2row_k4 --format str
```

Esto genera archivos `.meanQ` con las proporciones de ancestría por individuo y por cluster.

### 4.4. `plot_structure.py`

Genera gráficos de barras de ancestría (estilo STRUCTURE) a partir de un archivo `.meanQ` de ezstructure.

#### Uso básico

```bash
cd scripts
python plot_structure.py   --meanq ../results/nat_k2.2.meanQ   --output ../results/nat_k2_barplot.png   --csv ../data/Input_Naturales_1row.csv
```

Parámetros:

- `--meanq`: ruta al archivo `.meanQ`.
- `--output`: ruta del PNG de salida.
- `--csv`: archivo CSV original desde donde se obtienen los nombres de individuos.

Si no se pasan argumentos, se pueden configurar valores por defecto dentro del script (por ejemplo, apuntando a `nat_k2.2.meanQ` y `Input_Naturales_1row.csv`).

El script:

- Lee la matriz Q (`N_individuos x K`).
- Lee los nombres de individuos del CSV (todas las columnas excepto `Mark`).
- Crea un gráfico de barras apiladas donde:
  - eje X: individuos,
  - eje Y: proporción de ancestría,
  - cada color: un cluster (K).

### 4.5. `amova_manual.py`

Implementa un **AMOVA simple en Python**, sin `scikit-bio`, usando una matriz de distancias euclidianas entre individuos.

Suposición de grupos por defecto:

- **Grupo1:** individuos con IDs que contienen números 101–114 (por ejemplo `g101BR`–`g114BR`)
- **Grupo2:** individuos con IDs que contienen números 115–129 (por ejemplo `g115BR`–`g129BR`)

#### Uso básico

```bash
cd scripts
python amova_manual.py
```

- Entrada por defecto: `../data/Input_Naturales_1row.csv`

#### Uso con archivo alternativo

```bash
python amova_manual.py --input ../data/otro_archivo_1row.csv
```

> **Importante:** el script asume que los nombres de columnas de individuos contienen un número (ej. `g101BR`) y usa ese número para asignar individuos a Grupo1 o Grupo2. Si se usan otros IDs, será necesario adaptar la lógica de agrupación dentro del script.

El script:

1. Lee el CSV de genotipos.
2. Elimina SNPs completamente missing.
3. Imputa valores missing por la media del SNP.
4. Calcula una matriz de distancias euclidianas entre individuos.
5. Calcula:
   - `SS_total`
   - `SS_within`
   - `SS_between`
   - **ΦST = SS_between / SS_total**
6. Realiza 999 permutaciones de las etiquetas de grupo para estimar un **p-value**.

Ejemplo de salida:

```text
SNPs totales en archivo: 14193
SNPs después de eliminar filas todo-missing: 14110

Individuos y grupos asignados:
g101BR: Grupo1
...
g129BR: Grupo2

===== RESULTADOS AMOVA MANUAL =====
ΦST (Phi_ST): 0.134708
P-value (perm 999): 0.000000
SS_total: 44353.741
SS_within: 38378.941
SS_between: 5974.800
```

Interpretación típica:

- **ΦST ≈ 0.135** → estructura poblacional moderada entre Grupo1 y Grupo2.
- **p-value ≈ 0.000** → la diferenciación genética es altamente significativa.

---

## 5. Posibles extensiones

Algunas ideas para expandir este repositorio:

- Agregar un script de **PCA genético** a partir de la misma matriz de genotipos.
- Generar **heatmaps** y dendrogramas de la matriz de distancias.
- Permitir que el script `amova_manual.py` reciba un archivo externo de definición de poblaciones (por ejemplo, `poblaciones.csv`) en lugar de agrupar por rango de IDs.
- Añadir notebooks (`.ipynb`) con análisis exploratorio y visualización avanzada.

---

## 6. Créditos

Este pipeline combina:

- Preprocesamiento de genotipos en Python.
- ezstructure/fastStructure para inferencia de estructura poblacional.
- Un AMOVA manual basado en distancias euclidianas y permutaciones.

Puede servir como plantilla para analizar estructura genética en otros conjuntos de datos con formato similar.
