from math import sqrt

import pytest

from estrats.entrada_modex import AgentData, ModexInputData
from estrats.modexV import modexV, process


class TestModexV:
    def test_ejemplo_1_profesor(self):
        data = ModexInputData(
            (
                AgentData(100, 0.5, 1),
                AgentData(100, 0.1, 1),
                AgentData(-10, 0.1, 1),
            ),
            55,
        )

        strategy, effort, extremism = modexV(data)

        assert strategy == (1, 0, 0)
        assert effort == pytest.approx(50)
        assert extremism == pytest.approx(33.4995854)

    def test_ejemplo_2_profesor(self):
        data = ModexInputData(
            (
                AgentData(-30, 0.9, 1),
                AgentData(20, 0.1, 2),
                AgentData(50, 0.5, 1),
            ),
            35,
        )

        strategy, effort, extremism = modexV(data)

        assert strategy == (1, 0, 1)
        assert effort == pytest.approx(28)
        assert extremism == pytest.approx(9.4280904)

    def test_red_sin_agentes(self):
        assert modexV(ModexInputData((), 10)) == ((), 0.0, 0.0)

    def test_presupuesto_cero_no_modera_agentes_con_costo_positivo(self):
        data = ModexInputData(
            (AgentData(20, 0.5, 1), AgentData(-10, 0.5, 2)),
            0,
        )

        strategy, effort, extremism = modexV(data)

        assert strategy == (0, 0)
        assert effort == 0
        assert extremism == pytest.approx(sqrt(600) / 2)

    def test_modera_agentes_con_esfuerzo_cero(self):
        data = ModexInputData(
            (AgentData(-30, 1, 1), AgentData(20, 1, 2)),
            0,
        )

        strategy, effort, extremism = modexV(data)

        assert strategy == (1, 1)
        assert effort == 0
        assert extremism == 0

    def test_esfuerzo_fraccionario_no_se_redondea_por_agente(self):
        data = ModexInputData(
            (AgentData(1.02, 0.5, 1), AgentData(0.98, 0.5, 1)),
            1,
        )

        strategy, effort, extremism = modexV(data)

        assert strategy == (1, 1)
        assert effort == pytest.approx(1.0)
        assert extremism == 0

    def test_no_modera_agentes_con_opinion_cero(self):
        data = ModexInputData(
            (AgentData(0, 0.5, 1), AgentData(0, 0.8, 2)),
            10,
        )

        strategy, effort, extremism = modexV(data)

        assert strategy == (0, 0)
        assert effort == 0
        assert extremism == 0

    def test_selecciona_por_razon_beneficio_esfuerzo_y_respeta_el_limite(self):
        data = ModexInputData(
            (
                AgentData(10, 0.9, 1),
                AgentData(20, 0.75, 1),
                AgentData(20, 0.75, 1),
            ),
            10,
        )

        strategy, effort, extremism = modexV(data)

        assert strategy == (1, 1, 0)
        assert effort == pytest.approx(6)
        assert effort <= data.max_moderation
        assert extremism == pytest.approx(20 / 3)

    def test_retorna_error_para_datos_de_tipo_incorrecto(self):
        with pytest.raises(TypeError):
            modexV((), 10)

    def test_formato_salida(self):
        content = """3
-30 0.9 1
20 0.1 2
50 0.5 1
35
"""
        data = ModexInputData.from_text(content)

        output = process(data, content).splitlines()
        assert len(output) == len(data.agents) + 2
        assert float(output[0]) == pytest.approx(9.428090)
        assert float(output[1]) == pytest.approx(28)
        assert output[2:] == ["1", "0", "1"]
