from .entrada_modex import ModexInputData


def process(data: ModexInputData, original_content: str) -> str:
    if not isinstance(data, ModexInputData):
        raise TypeError("data debe ser una instancia de ModexInputData.")
    return original_content