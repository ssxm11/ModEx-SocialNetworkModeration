import unittest

from estrats import modexPD
from estrats.entrada_modex import ModexInputData


class ModexDynamicProgrammingTests(unittest.TestCase):
    def test_selects_global_optimum_instead_of_highest_individual_ratio(self) -> None:
        data = ModexInputData.from_text(
            "3\n10,0.4,1\n9,0.55,1\n9,0.55,1\n10\n"
        )

        strategy, effort, extremism = modexPD.modexPD(data)

        self.assertEqual(strategy, (0, 1, 1))
        self.assertAlmostEqual(effort, 8.1)
        self.assertAlmostEqual(extremism, 10 / 3)

    def test_selects_agents_with_zero_effort(self) -> None:
        data = ModexInputData.from_text("2\n-30,1,1\n20,1,2\n0\n")

        strategy, effort, extremism = modexPD.modexPD(data)

        self.assertEqual(strategy, (1, 1))
        self.assertEqual(effort, 0)
        self.assertEqual(extremism, 0)

    def test_uses_exact_effort_without_rounding_each_agent(self) -> None:
        data = ModexInputData.from_text(
            "2\n1.02,0.5,1\n0.98,0.5,1\n1\n"
        )

        strategy, effort, extremism = modexPD.modexPD(data)

        self.assertEqual(strategy, (1, 1))
        self.assertAlmostEqual(effort, 1.0)
        self.assertEqual(extremism, 0.0)

    def test_empty_agent_list_returns_zero_extremism(self) -> None:
        data = ModexInputData.from_text("0\n0\n")

        self.assertEqual(modexPD.modexPD(data), ((), 0, 0.0))


if __name__ == "__main__":
    unittest.main()
