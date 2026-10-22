from dataclasses import dataclass
import math
from pathlib import Path
import re


class ModexInputError(ValueError):
    """Raised when a ModEx input file does not follow its expected format."""


@dataclass(frozen=True, slots=True)
class AgentData:
    opinion: float
    receptivity: float
    influence: int


@dataclass(frozen=True, slots=True)
class ModexInputData:
    agents: tuple[AgentData, ...]
    max_moderation: int

    @classmethod
    def from_file(cls, path: str | Path) -> "ModexInputData":
        content = Path(path).read_text(encoding="utf-8-sig")
        return cls.from_text(content)

    @classmethod
    def from_text(cls, content: str) -> "ModexInputData":
        lines = [
            (line_number, line.strip())
            for line_number, line in enumerate(content.splitlines(), start=1)
            if line.strip()
        ]
        if not lines:
            raise ModexInputError("El archivo de entrada está vacío.")

        count_line, count_text = lines[0]
        try:
            agent_count = int(count_text)
        except ValueError as error:
            raise ModexInputError(
                f"La línea {count_line} debe indicar el número entero de agentes."
            ) from error
        if agent_count < 0:
            raise ModexInputError(
                f"El número de agentes en la línea {count_line} no puede ser negativo."
            )

        expected_line_count = agent_count + 2
        if len(lines) != expected_line_count:
            raise ModexInputError(
                "Se esperaban "
                f"{agent_count} filas de agentes y una fila para R_max "
                f"(total: {expected_line_count} líneas no vacías); "
                f"se encontraron {len(lines)}."
            )

        agents: list[AgentData] = []
        for agent_index, (line_number, line) in enumerate(lines[1:-1]):
            values = re.split(r"[\s,]+", line)
            if len(values) != 3:
                raise ModexInputError(
                    f"La línea {line_number} del agente {agent_index} "
                    "debe contener exactamente tres valores."
                )

            try:
                opinion = float(values[0])
                receptivity = float(values[1])
            except ValueError as error:
                raise ModexInputError(
                    f"La opinión y receptividad del agente {agent_index} "
                    f"en la línea {line_number} deben ser números."
                ) from error
            if not math.isfinite(opinion) or not math.isfinite(receptivity):
                raise ModexInputError(
                    f"La opinión y receptividad del agente {agent_index} "
                    f"en la línea {line_number} deben ser valores finitos."
                )

            try:
                influence = int(values[2])
            except ValueError as error:
                raise ModexInputError(
                    f"La influencia del agente {agent_index} "
                    f"en la línea {line_number} debe ser un entero entre 1 y 3."
                ) from error
            if influence not in (1, 2, 3):
                raise ModexInputError(
                    f"La influencia del agente {agent_index} "
                    f"en la línea {line_number} debe estar entre 1 y 3."
                )

            agents.append(AgentData(opinion, receptivity, influence))

        max_line, max_text = lines[-1]
        try:
            max_moderation = int(max_text)
        except ValueError as error:
            raise ModexInputError(
                f"La línea {max_line} debe indicar R_max como un entero."
            ) from error
        if max_moderation < 0:
            raise ModexInputError(
                f"R_max en la línea {max_line} no puede ser negativo."
            )

        return cls(tuple(agents), max_moderation)
