# ModEx

Aplicación de escritorio hecha con Pygame. Permite añadir archivos `.txt`, seleccionar uno de la lista para ver su contenido, abrirlo con la aplicación asociada o quitarlo de la lista sin eliminarlo del disco.

La ventana usa el icono `assets/modex.ico` y una paleta blanca con verde y verde lima.

Los botones **modexFB**, **modexV** y **modexPD** generan archivos como `nombre_modexFB_salida.txt`, `nombre_modexV_salida.txt` y `nombre_modexPD_salida.txt`. modexV aplica una estrategia voraz; modexPD usa programación dinámica para la mochila 0/1, con el mismo esfuerzo y beneficio por agente, caracterizando el subproblema, aplicando la recurrencia, llenando la tabla y reconstruyendo la estrategia óptima; modexFB sigue pendiente de implementación. Si ya existe un archivo con ese nombre, se agrega un sufijo numérico.

Antes de generar una salida con un modo ModEx, el archivo de entrada se interpreta y valida con `ModexInputData`, definido en [estrats/entrada_modex.py](./estrats/entrada_modex.py). El formato es:

```text
3
-0.5 0.8 1
0.2, 0.3, 2
0.9 0.1 3
5
```

La primera línea indica el número de agentes; cada una de las siguientes filas contiene la opinión, receptividad e influencia de un agente, separadas por espacios o comas (se permiten espacios antes o después de las comas); la última línea indica `R_max`. La opinión debe estar entre `-100` y `100`, la receptividad entre `0` y `1`, ambas deben ser números finitos, la influencia un entero entre 1 y 3, y `R_max` un entero no negativo. Se ignoran las líneas vacías. Los errores de formato se muestran en la aplicación y no generan una salida. El botón **Generar salida** conserva su comportamiento anterior.

Para obtener los datos desde un archivo o desde texto en el código:

```python
from estrats.entrada_modex import ModexInputData

datos = ModexInputData.from_file("entrada.txt")
# datos.agents: tupla de AgentData; datos.max_moderation: R_max
```

Los tres módulos de estrategia (`estrats/modexFB.py`, `estrats/modexPD.py` y `estrats/modexV.py`) reciben un `ModexInputData` mediante su función `process(data, original_content)`. El resultado de modexV y modexPD incluye la estrategia, el esfuerzo utilizado y el extremismo resultante; modexFB sigue pendiente de implementación.

## Ejecutar en Windows

Desde la carpeta del proyecto, abre PowerShell y ejecuta:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Al pulsar **Añadir archivo**, puedes seleccionar archivos de texto para agregarlos a la lista. Las pestañas **Entradas** y **Salidas** permiten consultar por separado los archivos de origen y los resultados generados; también se muestran las salidas `.txt` que ya existen en `output`. Al generar una salida, se muestra automáticamente en la vista previa. Selecciona un archivo para leerlo y usa **Abrir para editar** o **Quitar de lista** según necesites. Para procesar una entrada, elige **Generar salida** o uno de los tres modos.
