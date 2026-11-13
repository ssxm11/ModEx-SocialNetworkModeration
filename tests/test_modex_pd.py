import unittest
from itertools import product
from math import sqrt

from estrats import modexPD
from estrats.entrada_modex import AgentData, ModexInputData


def exhaustive_reference(agents: tuple[AgentData, ...], budget: int):
    n = len(agents)
    feasible = []

    for strategy in product((0, 1), repeat=n):
        effort = sum(
            abs(agent.opinion)
            * (1 - agent.receptivity)
            * agent.influence
            for agent, selected in zip(agents, strategy)
            if selected == 1
        )
        if effort > budget:
            continue

        remaining = sum(
            agent.opinion**2 * agent.influence
            for agent, selected in zip(agents, strategy)
            if selected == 0
        )
        feasible.append((remaining, effort))

    best_remaining, best_effort = min(feasible)
    extremism = sqrt(best_remaining) / n if n else 0.0
    return best_effort, extremism


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

    def test_matches_exhaustive_optimum_for_representative_networks(self) -> None:
        cases = (
            (
                (
                    AgentData(30, 0.5, 1),
                    AgentData(-20, 0.2, 2),
                    AgentData(15, 0.8, 3),
                    AgentData(40, 0.4, 1),
                ),
                (0, 10, 25, 50, 100),
            ),
            (
                (AgentData(1.02, 0.5, 1), AgentData(0.98, 0.5, 1)),
                (0, 1, 2),
            ),
            (
                (AgentData(-100, 1, 3), AgentData(0, 0.4, 2)),
                (0, 1),
            ),
        )

        for agents, budgets in cases:
            for budget in budgets:
                with self.subTest(agents=agents, budget=budget):
                    data = ModexInputData(agents, budget)
                    strategy, effort, extremism = modexPD.modexPD(data)
                    expected_effort, expected_extremism = exhaustive_reference(
                        agents,
                        budget,
                    )

                    self.assertLessEqual(effort, budget)
                    self.assertEqual(len(strategy), len(agents))
                    self.assertTrue(all(value in (0, 1) for value in strategy))
                    self.assertAlmostEqual(effort, expected_effort)
                    self.assertAlmostEqual(extremism, expected_extremism)

    def test_negative_budget_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            modexPD.dynamic_programming_algorithm((AgentData(20, 0.5, 1),), -1)


if __name__ == "__main__":
    unittest.main()
