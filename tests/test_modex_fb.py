
import itertools
from math import sqrt

import pytest

from estrats.entrada_modex import AgentData, ModexInputData
from estrats.modexFB import modexFB, brute_force_algorithm, process


def evaluador_independiente(agents, R_max):
    """
    Evaluador de referencia para redes pequeñas.
    Se utiliza exclusivamente para verificar los resultados
    de modexFB mediante una segunda enumeracion.
    """

    n = len(agents)

    if n == 0:
        return (), 0, 0.0

    mejor = None

    for strategy in itertools.product((0, 1), repeat=n):

        effort = sum(
            abs(agent.opinion)
            * (1 - agent.receptivity)
            * agent.influence
            for i, agent in enumerate(agents)
            if strategy[i] == 1
        )

        if effort > R_max:
            continue

        remaining = sum(
            agent.opinion ** 2 * agent.influence
            for i, agent in enumerate(agents)
            if strategy[i] == 0
        )

        extremism = sqrt(remaining) / n

        candidate = (remaining, effort, strategy, extremism)

        if (
            mejor is None
            or candidate[0] < mejor[0]
            or (
                candidate[0] == mejor[0]
                and candidate[1] < mejor[1]
            )
        ):
            mejor = candidate

    return mejor[2], mejor[1], mejor[3]


class TestModexFB:

    def test_ejemplo_1_profesor(self):

        agents = (
            AgentData(100, 0.5, 1),
            AgentData(100, 0.1, 1),
            AgentData(-10, 0.1, 1)
        )

        strategy, effort, extremism = modexFB(agents, 55)

        assert strategy == (1, 0, 0)
        assert effort == 50
        assert extremism == pytest.approx(33.4995854)

    def test_ejemplo_2_profesor(self):

        agents = (
            AgentData(-30, 0.9, 1),
            AgentData(20, 0.1, 2),
            AgentData(50, 0.5, 1)
        )

        strategy, effort, extremism = modexFB(agents, 35)

        assert strategy == (1, 0, 1)
        assert effort == 28
        assert extremism == pytest.approx(9.4280904)

    def test_red_sin_agentes(self):

        assert modexFB((), 10) == ((), 0, 0.0)

    def test_presupuesto_negativo(self):

        agents = (AgentData(20, 0.5, 1),)

        with pytest.raises(ValueError):
            modexFB(agents, -1)

    def test_presupuesto_debe_ser_entero(self):

        agents = (AgentData(20, 0.5, 1),)

        with pytest.raises(ValueError):
            modexFB(agents, 10.5)

    def test_presupuesto_cero(self):

        agents = (
            AgentData(20, 0.5, 1),
            AgentData(-10, 0.5, 2)
        )

        strategy, effort, extremism = modexFB(agents, 0)

        assert strategy == (0, 0)
        assert effort == 0
        assert extremism == pytest.approx(sqrt(600) / 2)

    def test_esfuerzo_usa_valores_exactos_sin_redondear_por_agente(self):
        agents = (
            AgentData(1.02, 0.5, 1),
            AgentData(0.98, 0.5, 1),
        )

        strategy, effort, extremism = modexFB(agents, 1)

        assert strategy == (1, 1)
        assert effort == pytest.approx(1.0)
        assert extremism == 0.0

    def test_opinion_fuera_de_rango(self):

        agents = (AgentData(120, 0.5, 1),)

        with pytest.raises(ValueError):
            modexFB(agents, 100)

    def test_receptividad_fuera_de_rango(self):

        agents = (AgentData(20, 1.5, 1),)

        with pytest.raises(ValueError):
            modexFB(agents, 100)

    def test_influencia_fuera_de_rango(self):

        agents = (AgentData(20, 0.5, 4),)

        with pytest.raises(ValueError):
            modexFB(agents, 100)

    def test_agente_con_opinion_cero(self):

        agents = (
            AgentData(0, 0.5, 1),
            AgentData(0, 0.8, 2)
        )

        strategy, effort, extremism = modexFB(agents, 10)

        assert strategy == (0, 0)
        assert effort == 0
        assert extremism == 0.0

    def test_estrategia_no_supera_presupuesto(self):

        agents = (
            AgentData(100, 0.5, 1),
            AgentData(100, 0.1, 1),
            AgentData(-10, 0.1, 1)
        )

        strategy, effort, extremism = modexFB(agents, 55)

        assert effort <= 55
        assert len(strategy) == len(agents)
        assert all(value in (0, 1) for value in strategy)

    def test_comparacion_con_evaluador_independiente(self):

        agents = (
            AgentData(30, 0.5, 1),
            AgentData(-20, 0.2, 2),
            AgentData(15, 0.8, 3),
            AgentData(40, 0.4, 1)
        )

        resultado_fb = modexFB(agents, 50)
        resultado_referencia = evaluador_independiente(agents, 50)

        assert resultado_fb[0] == resultado_referencia[0]
        assert resultado_fb[1] == resultado_referencia[1]
        assert resultado_fb[2] == pytest.approx(
            resultado_referencia[2]
        )

    def test_interfaz_brute_force(self):

        agents = (
            AgentData(20, 0.5, 1),
            AgentData(10, 0.5, 1)
        )

        assert modexFB(agents, 20) == brute_force_algorithm(
            agents, 20
        )

    def test_formato_salida(self):

        content = """3
-30 0.9 1
20 0.1 2
50 0.5 1
35
"""

        data = ModexInputData.from_text(content)

        result = process(data, content)
        lines = result.splitlines()

        assert len(lines) == 5
        assert float(lines[0]) == pytest.approx(9.428090)
        assert float(lines[1]) == pytest.approx(28)
        assert lines[2:] == ["1", "0", "1"]
