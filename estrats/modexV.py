# Estrategia voraz
# elegir primero un algoritmo voraz que permita encontrar la solución optima siempre o la mayoría de veces.

from .entrada_modex import ModexInputData


def process(data: ModexInputData, original_content: str) -> str:
    if not isinstance(data, ModexInputData):
        raise TypeError("data debe ser una instancia de ModexInputData.")
    return original_content

# entrada: <agente1, agente2, agente3, ... , agenteN , R_max>
# usaremos el algoritmo voraz que toma peso y valor de cada agente, y elige los agentes con la mejor relación valor/peso hasta que se alcance R_max. (inicialmente)

def greedy_algorithm(agents, R_max):
    # Implementación del algoritmo voraz
    # Ordenar los agentes por su relación valor/peso y seleccionar los mejores hasta alcanzar R_max.
    pass  # Aquí iría la lógica del algoritmo voraz