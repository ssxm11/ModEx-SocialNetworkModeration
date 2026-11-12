import math
from .entrada_modex import ModexInputData

def greedy_algorithm(agents, R_max):
    n = len(agents)
    items = []
    
    # Analisis de cada agente y calcula su peso (esfuerzo) y su valor (impacto)
    for i, agent in enumerate(agents):
        if agent.opinion == 0:
            # Si la opinión ya es 0, no vale la pena gastar presupuesto en moderarlo
            ratio = -1
            weight = 0
            value = 0
        else:
            # Esfuerzo que cuesta moderar a este agente según la fórmula del modelo
            weight = abs(agent.opinion) * (1 - agent.receptivity) * agent.influence
            
            # Estimado del valor o beneficio: que tanto reduce el extremismo al cuadrado con su influencia
            value = (agent.opinion ** 2) * agent.influence
            
            # ratio valor/peso para saber qué tan conveniente es
            ratio = (value / weight) if weight > 0 else float('inf')
            
        items.append({
            'index': i,
            'weight': weight,
            'value': value,
            'ratio': ratio
        })
    
    # organiza los agentes de mayor a menor según el ratio de conveniencia
    items.sort(key=lambda x: x['ratio'], reverse=True)
    
    strategy = [0] * n
    current_effort = 0
    
    # se usa para seleccionar de forma voraz los mejores agentes mientras alcance el R_max
    for item in items:
        if item['value'] > 0 and current_effort + item['weight'] <= R_max:
            strategy[item['index']] = 1
            current_effort += item['weight']
            
    return tuple(strategy)

def calcular_esfuerzo(agents, strategy):
    # Función auxiliar para sumar el esfuerzo total gastado con la estrategia elegida
    total_esfuerzo = 0.0
    for agent, e in zip(agents, strategy):
        if e == 1:
            total_esfuerzo += (
                abs(agent.opinion)
                * (1 - agent.receptivity)
                * agent.influence
            )
    return total_esfuerzo

def calcular_extremismo(agents, strategy):
    # Función auxiliar para calcular cómo queda el extremismo en la red tras aplicar la estrategia
    n = len(agents)
    suma_cuadrados = 0
    for agent, e in zip(agents, strategy):
        op_final = 0 if e == 1 else agent.opinion
        suma_cuadrados += (op_final ** 2) * agent.influence
    
    extremism = math.sqrt(suma_cuadrados) / n if n > 0 else 0.0
    return extremism

# Recibe los datos de la red y devuelve la tripleta exacta:
    # (Estrategia E, Esfuerzo total, Extremismo de la red moderada).
def modexV(data: ModexInputData, original_content: str = "") -> tuple:

    if not isinstance(data, ModexInputData):
        raise TypeError("Los datos de entrada deben ser una instancia válida de ModexInputData.")
    
    #para obtener la tupla de 0 y 1 con la decisión para cada agente
    estrategia = greedy_algorithm(data.agents, data.max_moderation)
  
    esfuerzo_total = calcular_esfuerzo(data.agents, estrategia)
    extremismo_red = calcular_extremismo(data.agents, estrategia)
    
    return (estrategia, esfuerzo_total, extremismo_red)

def process(data: ModexInputData, original_content: str) -> str:
    estrategia, esfuerzo, extremismo = modexV(data, original_content)

    output_lines = [f"{extremismo:.6f}", str(esfuerzo)]
    output_lines.extend(str(selected) for selected in estrategia)
    return "\n".join(output_lines)