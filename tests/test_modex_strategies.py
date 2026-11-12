import math
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import main
from estrats import modexFB, modexPD, modexV
from estrats.entrada_modex import ModexInputData


class ModexStrategyInputTests(unittest.TestCase):
    def test_strategies_use_exact_effort_and_shared_extremism_formula(self) -> None:
        cases = (
            (
                "2\n1.02,0.5,1\n0.98,0.5,1\n1\n",
                (1, 1),
                1.0,
                0.0,
            ),
            (
                "2\n10,0.5,1\n-20,0.5,2\n0\n",
                (0, 0),
                0.0,
                15.0,
            ),
        )
        for content, expected_strategy, expected_effort, expected_extremism in cases:
            data = ModexInputData.from_text(content)
            results = (
                ("fuerza bruta", modexFB.modexFB(data.agents, data.max_moderation)),
                ("programación dinámica", modexPD.modexPD(data)),
                ("voraz", modexV.modexV(data)),
            )
            for name, result in results:
                with self.subTest(case=content, strategy=name):
                    self.assertEqual(result[0], expected_strategy)
                    self.assertAlmostEqual(result[1], expected_effort)
                    self.assertAlmostEqual(result[2], expected_extremism)

    def test_each_strategy_receives_parsed_input(self) -> None:
        content = "1\n0.25 0.8 2\n3\n"
        expected_data = ModexInputData.from_text(content)
        strategies = (
            (main.process_modex_fb, modexFB),
            (main.process_modex_pd, modexPD),
            (main.process_modex_v, modexV),
        )

        for processor, strategy in strategies:
            with self.subTest(strategy=strategy.__name__):
                with patch.object(strategy, "process", return_value="resultado") as process:
                    self.assertEqual(processor(content), "resultado")

                process.assert_called_once_with(expected_data, content)

    def test_v_and_pd_outputs_contain_only_numeric_values(self) -> None:
        content = "2\n10,0.5,1\n-20,0.5,2\n100\n"
        data = ModexInputData.from_text(content)

        for strategy in (modexPD, modexV):
            with self.subTest(strategy=strategy.__name__):
                lines = strategy.process(data, content).splitlines()

                self.assertEqual(len(lines), len(data.agents) + 2)
                self.assertTrue(math.isfinite(float(lines[0])))
                self.assertTrue(math.isfinite(float(lines[1])))
                self.assertTrue(all(line in ("0", "1") for line in lines[2:]))

    def test_saved_v_and_pd_outputs_have_no_header(self) -> None:
        content = "1\n10,0.5,1\n10\n"

        with TemporaryDirectory() as temporary_directory:
            project_dir = Path(temporary_directory)
            source = project_dir / "input.txt"
            source.write_text(content, encoding="utf-8")

            for strategy in ("modexV", "modexPD"):
                with self.subTest(strategy=strategy):
                    output_path = main.create_output_file(
                        source,
                        project_dir,
                        strategy,
                    )

                    output_lines = output_path.read_text(encoding="utf-8").splitlines()
                    self.assertEqual(len(output_lines), 3)
                    self.assertTrue(math.isfinite(float(output_lines[0])))
                    self.assertTrue(math.isfinite(float(output_lines[1])))
                    self.assertIn(output_lines[2], ("0", "1"))


if __name__ == "__main__":
    unittest.main()
