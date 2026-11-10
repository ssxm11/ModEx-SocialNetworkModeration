# Estrategia de fuerza bruta
# algoritmo que genera todas las soluciones posibles y las evalúa para encontrar la mejor


from itertools import product
from math import ceil, sqrt

from .entrada_modex import AgentData, ModexInputData


def modexFB(agents, R_max):
    """
    Algoritmo de fuerza bruta para resolver ModEx.

    Entrada:
        agents: secuencia de agentes.
        R_max: esfuerzo máximo disponible.

    Salida:
        (E, esfuerzo, extremismo)
    """

    if R_max < 0:
        raise ValueError("R_max no puede ser negativo.")

    n = len(agents)

    # Caso especial: red sin agentes.
    if n == 0:
        return (), 0, 0.0

    # Calcular el esfuerzo individual de moderar cada agente.
    costs = [
        ceil(
            abs(agent.opinion)
            * (1 - agent.receptivity)
            * agent.influence
        )
        for agent in agents
    ]

    # Calcular la contribución individual al extremismo.
    contributions = [
        (agent.opinion ** 2) * agent.influence
        for agent in agents
    ]

    best_strategy = None
    best_effort = 0
    best_extremism = float("inf")
    best_remaining_extremism = float("inf")

    # Generar exhaustivamente todas las estrategias binarias.
    for strategy in product((0, 1), repeat=n):

        effort = 0
        remaining_extremism = 0

        # Evaluar cada agente de la estrategia.
        for i in range(n):

            if strategy[i] == 1:
                effort += costs[i]
            else:
                remaining_extremism += contributions[i]

        # Descartar estrategias que exceden R_max.
        if effort > R_max:
            continue

        # Calcular el extremismo de la red resultante.
        extremism = sqrt(remaining_extremism / n)

        # Conservar la mejor estrategia encontrada.
        if (
            extremism < best_extremism
            or (
                extremism == best_extremism
                and effort < best_effort
            )
        ):
            best_strategy = strategy
            best_effort = effort
            best_extremism = extremism
            best_remaining_extremism = remaining_extremism

    # Siempre existe al menos una solución:
    # no moderar ningún agente (E = 0...0).
    return (
        best_strategy,
        best_effort,
        best_extremism
    )


def brute_force_algorithm(agents, R_max):
    """
    Interfaz alternativa para ejecutar fuerza bruta.
    Devuelve la tripleta (E, esfuerzo, extremismo).
    """
    return modexFB(agents, R_max)


def process(data: ModexInputData, original_content: str) -> str:
    """
    Integra el algoritmo con la aplicación principal ModEx.

    Devuelve el archivo de salida con:
        Línea 1: extremismo final.
        Línea 2: esfuerzo utilizado.
        Líneas siguientes: estrategia binaria.
    """

    if not isinstance(data, ModexInputData):
        raise TypeError(
            "data debe ser una instancia de ModexInputData."
        )

    strategy, effort, extremism = modexFB(
        data.agents,
        data.max_moderation
    )

    output = [
        f"{extremism:.6f}",
        str(effort)
    ]

    output.extend(str(value) for value in strategy)

    return "\n".join(output)
