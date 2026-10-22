import unittest
from unittest.mock import patch

import main
from estrats import modexFB, modexPD, modexV
from estrats.entrada_modex import ModexInputData


class ModexStrategyInputTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
