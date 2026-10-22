# ModEx

Aplicación de escritorio hecha con Pygame. Permite añadir archivos `.txt`, seleccionar uno de la lista para ver su contenido, abrirlo con la aplicación asociada o quitarlo de la lista sin eliminarlo del disco.

La ventana usa el icono `assets/modex.ico` y una paleta blanca con verde y verde lima.

Los botones **modexFB**, **modexV** y **modexPD** son plantillas para conectar los algoritmos; por ahora conservan el texto de entrada y crean, respectivamente, archivos como `nombre_modexFB_salida.txt`, `nombre_modexV_salida.txt` y `nombre_modexPD_salida.txt`. Si ya existe un archivo con ese nombre, se agrega un sufijo numérico.

Antes de generar una salida con un modo ModEx, el archivo de entrada se interpreta y valida con `ModexInputData`, definido en [estrats/entrada_modex.py](./estrats/entrada_modex.py). El formato es:

```text
3
-0.5 0.8 1
0.2, 0.3, 2
0.9 0.1 3
5
```

La primera línea indica el número de agentes; cada una de las siguientes filas contiene la opinión, receptividad e influencia de un agente, separadas por espacios o comas; la última línea indica `R_max`. La opinión y la receptividad deben ser números finitos, la influencia un entero entre 1 y 3, y `R_max` un entero no negativo. Se ignoran las líneas vacías. Los errores de formato se muestran en la aplicación y no generan una salida. El botón **Generar salida** conserva su comportamiento anterior.

Para obtener los datos desde un archivo o desde texto en el código:

```python
from estrats.entrada_modex import ModexInputData

datos = ModexInputData.from_file("entrada.txt")
# datos.agents: tupla de AgentData; datos.max_moderation: R_max
```

Los tres módulos de estrategia (`estrats/modexFB.py`, `estrats/modexPD.py` y `estrats/modexV.py`) reciben un `ModexInputData` mediante su función `process(data, original_content)`. Al implementar cada algoritmo, usa ese primer argumento para consultar `data.agents` (cada elemento contiene `opinion`, `receptivity` e `influence`) y `data.max_moderation` (`R_max`). Por ahora `process` conserva el contenido original como salida.

## Ejecutar en Windows

Desde la carpeta del proyecto, abre PowerShell y ejecuta:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Al pulsar **Añadir archivo**, puedes seleccionar archivos de texto para agregarlos a la lista. Las pestañas **Entradas** y **Salidas** permiten consultar por separado los archivos de origen y los resultados generados; también se muestran las salidas `.txt` que ya existen en `output`. Al generar una salida, se muestra automáticamente en la vista previa. Selecciona un archivo para leerlo y usa **Abrir para editar** o **Quitar de lista** según necesites. Para procesar una entrada, elige **Generar salida** o uno de los tres modos.
