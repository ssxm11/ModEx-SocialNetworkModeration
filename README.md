# ModEx: moderación del extremismo de opiniones

## Integrantes del equipo

Helkin Gabriel JimenezMedina - 2179462
Esteban Samuel Córdoba Narváez - 2370976
Brigitte Vanesa Chavez Riascos - 2510107


## Descripción

Aplicación de escritorio para el problema ModEx: dada una red social con `n`
agentes y un presupuesto máximo `R_max`, seleccionar qué opiniones moderar para
minimizar el extremismo de la red sin exceder el esfuerzo disponible.

Cada agente tiene una opinión, receptividad e influencia. Una estrategia es una
secuencia binaria `E = (e0, ..., e(n-1))`: `ei = 1` significa que se modera al
agente `i` (su opinión final se establece en cero), y `ei = 0` que permanece
sin cambios.

La aplicación ofrece tres métodos para resolver el problema:

- **Fuerza bruta (`modexFB`)**: evalúa todas las estrategias posibles y devuelve
  una solución óptima. Su tiempo de ejecución es exponencial, del orden de
  `O(n * 2^n)`.
- **Voraz (`modexV`)**: ordena a los agentes por una razón de beneficio/esfuerzo
  y selecciona mientras el presupuesto lo permita. Es una heurística y no
  garantiza encontrar el óptimo. Su tiempo es `O(n log n)`.
- **Programación dinámica (`modexPD`)**: resuelve la selección como una mochila
  0/1 y reconstruye una estrategia óptima para el modelo implementado.

El esfuerzo de moderar al agente `i` es
`|opinión_i - opinión_final_i| * (1 - receptividad_i) * influencia_i`.
El esfuerzo puede ser decimal y no se redondea por agente.
El extremismo reportado es
`sqrt(sum(influencia_i * opinión_final_i²)) / n`, donde la opinión final es cero
para los agentes moderados. Las estrategias voraz y de programación dinámica
usan `opinión_i² * influencia_i` como beneficio estimado de moderar al agente.
La programación dinámica conserva los estados no dominados de esfuerzo y
beneficio, por lo que su peor caso puede ser exponencial.

## Formato de entrada

El archivo de texto contiene `n + 2` líneas: el número de agentes, una línea
por agente y el presupuesto máximo.

```text
3
-30, 0.9, 1
20, 0.1, 2
50, 0.5, 1
35
```

Cada fila de agente contiene opinión, receptividad e influencia. Se aceptan
comas o espacios como separadores, incluidos espacios alrededor de las comas.
Las líneas vacías se ignoran. El parser valida que la opinión esté entre `-100`
y `100`, la receptividad entre `0` y `1`, la influencia sea un entero entre
`1` y `3`, y `R_max` sea un entero no negativo. Las opiniones decimales también
son aceptadas por la implementación.

**Diferencia respecto al dominio del enunciado:** este especifica opiniones
enteras e influencias reales entre `1` y `3`; el parser actual acepta opiniones
numéricas decimales, pero exige que la influencia sea un entero (`1`, `2` o
`3`).

## Formato de salida

Cada estrategia escribe un archivo de texto con `n + 2` líneas, sin etiquetas:

1. Extremismo de la red moderada.
2. Esfuerzo total utilizado.
3. Una decisión `0` o `1` por agente, en el orden de entrada.

Por ejemplo, para dos agentes:

```text
12.345678
20
1
0
```

Los archivos se guardan en `output/` con un nombre que identifica el archivo
de origen y el método (`_modexFB_salida.txt`, `_modexV_salida.txt` o
`_modexPD_salida.txt`). Si el nombre ya existe, se añade un sufijo numérico.

## Uso de la aplicación

La interfaz permite añadir archivos `.txt`, revisar su contenido, generar una
salida con fuerza bruta, voraz o programación dinámica, y consultar entradas y
resultados en pestañas separadas. Las salidas generadas se muestran en la
interfaz y se guardan en `output/`. También es posible abrir archivos con la
aplicación asociada o retirarlos de la lista sin borrarlos del disco.

El botón **Generar salida** copia el contenido de entrada a un archivo de
salida, precedido por una línea `salida`; no ejecuta una estrategia. Para
resolver ModEx, usa uno de los botones de estrategia.

## Instalación y ejecución en Windows

Desde la carpeta del proyecto, ejecuta en PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Para ejecutar las pruebas:

```powershell
py -m unittest discover -s tests
```

## Estructura del proyecto

- `main.py`: interfaz gráfica, selección y visualización de archivos, y
  generación de salidas.
- `estrats/entrada_modex.py`: lectura y validación de entradas.
- `estrats/modexFB.py`: estrategia de fuerza bruta.
- `estrats/modexV.py`: estrategia voraz.
- `estrats/modexPD.py`: estrategia de programación dinámica.
- `tests/`: pruebas automatizadas.
- `assets/modex.ico`: icono de la aplicación.
- `output/`: archivos de salida generados.
- `enunciado_proyecto.md`: enunciado del proyecto del curso.
