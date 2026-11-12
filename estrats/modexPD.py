import math
from collections.abc import Sequence

from .entrada_modex import AgentData, ModexInputData


def dynamic_programming_algorithm(
    agents: Sequence[AgentData],
    R_max: int,
) -> tuple[int, ...]:
    if R_max < 0:
        raise ValueError("R_max no puede ser negativo.")

    states = [(0.0, 0.0, ())]
    for agent in agents:
        effort = (
            abs(agent.opinion)
            * (1 - agent.receptivity)
            * agent.influence
        )
        benefit = (agent.opinion ** 2) * agent.influence
        candidates = []

        for used_effort, total_benefit, strategy in states:
            candidates.append(
                (used_effort, total_benefit, strategy + (0,))
            )
            moderated_effort = used_effort + effort
            if moderated_effort <= R_max:
                candidates.append(
                    (
                        moderated_effort,
                        total_benefit + benefit,
                        strategy + (1,),
                    )
                )

        candidates.sort(key=lambda state: (state[0], -state[1]))
        states = []
        best_benefit = float("-inf")
        for state in candidates:
            if state[1] > best_benefit:
                states.append(state)
                best_benefit = state[1]

    return max(states, key=lambda state: (state[1], -state[0]))[2]


def calcular_esfuerzo(
    agents: Sequence[AgentData],
    strategy: Sequence[int],
) -> float:
    return sum(
        (
            abs(agent.opinion) * (1 - agent.receptivity) * agent.influence
            for agent, selected in zip(agents, strategy)
            if selected == 1
        ),
        0.0,
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
    return math.sqrt(suma_cuadrados) / len(agents)


def modexPD(
    data: ModexInputData,
    original_content: str = "",
) -> tuple[tuple[int, ...], float, float]:
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
