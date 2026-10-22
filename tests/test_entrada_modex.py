import unittest

from estrats.entrada_modex import AgentData, ModexInputData, ModexInputError


class ModexInputDataTests(unittest.TestCase):
    def test_builds_agents_and_max_moderation(self) -> None:
        data = ModexInputData.from_text(
            "2\n-0.5 0.8 1\n0.25, 0.3, 3\n4\n"
        )

        self.assertEqual(
            data.agents,
            (
                AgentData(-0.5, 0.8, 1),
                AgentData(0.25, 0.3, 3),
            ),
        )
        self.assertEqual(data.max_moderation, 4)

    def test_allows_zero_agents(self) -> None:
        data = ModexInputData.from_text("0\n0\n")

        self.assertEqual(data.agents, ())
        self.assertEqual(data.max_moderation, 0)

    def test_rejects_wrong_number_of_agent_rows(self) -> None:
        with self.assertRaisesRegex(ModexInputError, "Se esperaban"):
            ModexInputData.from_text("2\n0.1 0.2 1\n5\n")

    def test_rejects_influence_outside_range(self) -> None:
        with self.assertRaisesRegex(ModexInputError, "entre 1 y 3"):
            ModexInputData.from_text("1\n0.1 0.2 4\n5\n")

    def test_rejects_negative_max_moderation(self) -> None:
        with self.assertRaisesRegex(ModexInputError, "no puede ser negativo"):
            ModexInputData.from_text("0\n-1\n")

    def test_rejects_non_finite_agent_values(self) -> None:
        with self.assertRaisesRegex(ModexInputError, "valores finitos"):
            ModexInputData.from_text("1\nnan 0.2 1\n0\n")


if __name__ == "__main__":
    unittest.main()
