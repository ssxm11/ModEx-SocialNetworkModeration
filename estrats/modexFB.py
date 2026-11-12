
# ==========================================================
# ESTRATEGIA DE FUERZA BRUTA - MODEX
# ==========================================================
# Genera y evalua exhaustivamente las 2^n estrategias
# posibles para encontrar la solucion factible con
# menor extremismo.
# ==========================================================

from itertools import product
from math import sqrt, isfinite

from .entrada_modex import ModexInputData


def validar_entrada(agents, R_max):
    """
    Verifica que los datos respeten los dominios del problema.
    """

    if not isinstance(R_max, int) or isinstance(R_max, bool):
        raise ValueError("R_max debe ser un numero entero.")

    if R_max < 0:
        raise ValueError("R_max no puede ser negativo.")

    for i, agent in enumerate(agents):

        opinion = agent.opinion
        receptivity = agent.receptivity
        influence = agent.influence

        if not isfinite(opinion):
            raise ValueError(
                f"La opinion del agente {i} debe ser finita."
            )

        if not -100 <= opinion <= 100:
            raise ValueError(
                f"La opinion del agente {i} debe estar entre -100 y 100."
            )

        if not isfinite(receptivity):
            raise ValueError(
                f"La receptividad del agente {i} debe ser finita."
            )

        if not 0 <= receptivity <= 1:
            raise ValueError(
                f"La receptividad del agente {i} debe estar entre 0 y 1."
            )

        if (
            not isinstance(influence, int)
            or isinstance(influence, bool)
            or influence not in (1, 2, 3)
        ):
            raise ValueError(
                f"La influencia del agente {i} debe ser 1, 2 o 3."
            )


def modexFB(agents, R_max):
    """
    Resuelve el problema ModEx mediante fuerza bruta.

    Parametros:
        agents: secuencia de agentes.
        R_max: presupuesto maximo de moderacion.

    Retorna:
        (E, esfuerzo, extremismo)

        E: tupla binaria que indica los agentes moderados.
        esfuerzo: esfuerzo total utilizado.
        extremismo: extremismo final de la red.
    """

    agents = tuple(agents)

    validar_entrada(agents, R_max)

    n = len(agents)

    # Caso especial: red sin agentes.
    if n == 0:
        return (), 0, 0.0

    # ------------------------------------------------------
    # 1. PRECALCULO DE COSTOS DE MODERACION
    # ------------------------------------------------------

    costs = [
        abs(agent.opinion)
        * (1 - agent.receptivity)
        * agent.influence
        for agent in agents
    ]

    # ------------------------------------------------------
    # 2. PRECALCULO DE CONTRIBUCIONES AL EXTREMISMO
    # ------------------------------------------------------

    contributions = [
        agent.opinion ** 2 * agent.influence
        for agent in agents
    ]

    # ------------------------------------------------------
    # 3. INICIALIZACION DE LA MEJOR SOLUCION
    # ------------------------------------------------------

    best_strategy = None
    best_effort = 0.0
    best_remaining = float("inf")

    # ------------------------------------------------------
    # 4. GENERACION EXHAUSTIVA DE ESTRATEGIAS
    # ------------------------------------------------------

    for strategy in product((0, 1), repeat=n):

        effort = 0.0
        remaining_extremism = 0

        # Evaluar todos los agentes de la estrategia.
        for i, decision in enumerate(strategy):

            if decision == 1:
                # Moderar al agente: opinion final igual a cero.
                effort += costs[i]

            else:
                # No moderar: conserva su contribucion.
                remaining_extremism += contributions[i]

        # --------------------------------------------------
        # 5. COMPROBACION DE FACTIBILIDAD
        # --------------------------------------------------

        if effort > R_max:
            continue

        # --------------------------------------------------
        # 6. SELECCION DE LA MEJOR ESTRATEGIA
        # --------------------------------------------------

        # Para n fijo, minimizar la suma restante equivale
        # a minimizar el extremismo final.
        #
        # En caso de empate, se prefiere menor esfuerzo.

        if (
            remaining_extremism < best_remaining
            or (
                remaining_extremism == best_remaining
                and (
                    best_strategy is None
                    or effort < best_effort
                )
            )
        ):
            best_strategy = strategy
            best_effort = effort
            best_remaining = remaining_extremism

    # La estrategia de no moderar ningun agente siempre
    # es factible cuando R_max >= 0.
    if best_strategy is None:
        raise RuntimeError(
            "No se encontro una estrategia factible."
        )

    # ------------------------------------------------------
    # 7. CALCULO DEL EXTREMISMO FINAL
    # ------------------------------------------------------

    extremism = sqrt(best_remaining) / n

    return best_strategy, best_effort, extremism


def brute_force_algorithm(agents, R_max):
    """
    Interfaz alternativa para ejecutar el algoritmo.
    """
    return modexFB(agents, R_max)


def process(data: ModexInputData, original_content: str) -> str:
    """
    Integra fuerza bruta con la aplicacion principal.

    Formato:
        Linea 1: extremismo.
        Linea 2: esfuerzo.
        Lineas 3 hasta n+2: decisiones binarias.
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
