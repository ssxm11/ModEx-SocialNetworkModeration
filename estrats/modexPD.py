import math
from collections.abc import Sequence

from .entrada_modex import AgentData, ModexInputData


def dynamic_programming_algorithm(
    agents: Sequence[AgentData],
    R_max: int,
) -> tuple[int, ...]:
    if R_max < 0:
        raise ValueError("R_max no puede ser negativo.")

    n = len(agents)
    weights = [
        math.ceil(abs(agent.opinion) * (1 - agent.receptivity) * agent.influence)
        for agent in agents
    ]
    benefits = [
        (agent.opinion ** 2) * agent.influence
        for agent in agents
    ]
    budget_limit = min(R_max, sum(weights))

    # 0. Subestructura óptima: una solución para los primeros i agentes
    # incluye al agente i o lo deja fuera; en ambos casos, el subproblema
    # con los primeros i-1 agentes también debe tener beneficio máximo.
    # 1. dp[i][r] guarda el beneficio máximo usando los primeros i agentes
    # con presupuesto r. Caso base: dp[0][r] = 0 para cualquier r.
    dp = [[0.0] * (budget_limit + 1) for _ in range(n + 1)]

    # 2. Recurrencia 0/1:
    # dp[i][r] = max(dp[i-1][r], dp[i-1][r-w_i] + v_i), si w_i <= r;
    # si no, dp[i][r] = dp[i-1][r].
    # Aquí w_i es el esfuerzo y v_i la reducción estimada del extremismo
    # al cuadrado, con las mismas definiciones usadas por modexV.

    # 3. Calcula la tabla en orden creciente de agentes y presupuestos.
    for i in range(1, n + 1):
        weight = weights[i - 1]
        benefit = benefits[i - 1]
        for budget in range(budget_limit + 1):
            without_agent = dp[i - 1][budget]
            with_agent = (
                dp[i - 1][budget - weight] + benefit
                if weight <= budget
                else float("-inf")
            )
            dp[i][budget] = max(without_agent, with_agent)

    # 4. Reconstruye la solución desde dp[n][budget_limit]:
    # si incluir al agente mejora el estado, lo marca y descuenta su esfuerzo.
    strategy = [0] * n
    remaining_budget = budget_limit
    for i in range(n, 0, -1):
        if dp[i][remaining_budget] > dp[i - 1][remaining_budget]:
            strategy[i - 1] = 1
            remaining_budget -= weights[i - 1]

    return tuple(strategy)


def calcular_esfuerzo(
    agents: Sequence[AgentData],
    strategy: Sequence[int],
) -> int:
    return sum(
        math.ceil(abs(agent.opinion) * (1 - agent.receptivity) * agent.influence)
        for agent, selected in zip(agents, strategy)
        if selected == 1
    )


def calcular_extremismo(
    agents: Sequence[AgentData],
    strategy: Sequence[int],
) -> float:
    if not agents:
        return 0.0

    suma_cuadrados = sum(
        (0 if selected == 1 else agent.opinion) ** 2 * agent.influence
        for agent, selected in zip(agents, strategy)
    )
    return math.sqrt(suma_cuadrados / len(agents))


def modexPD(
    data: ModexInputData,
    original_content: str = "",
) -> tuple[tuple[int, ...], int, float]:
    if not isinstance(data, ModexInputData):
        raise TypeError("Los datos de entrada deben ser una instancia válida de ModexInputData.")

    strategy = dynamic_programming_algorithm(data.agents, data.max_moderation)
    effort = calcular_esfuerzo(data.agents, strategy)
    extremism = calcular_extremismo(data.agents, strategy)
    return strategy, effort, extremism


def process(data: ModexInputData, original_content: str) -> str:
    strategy, effort, extremism = modexPD(data, original_content)
    output_lines = [f"{extremism:.6f}", str(effort)]
    output_lines.extend(str(selected) for selected in strategy)
    return "\n".join(output_lines)
