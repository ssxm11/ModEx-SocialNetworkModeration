import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

import pygame

from estrats import modexFB, modexPD, modexV
from estrats.entrada_modex import ModexInputData


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 735
BACKGROUND = (246, 250, 245)
PANEL = (255, 255, 255)
BUTTON = (34, 139, 74)
BUTTON_HOVER = (48, 163, 83)
WHITE = (255, 255, 255)
TEXT = (30, 58, 38)
MUTED = (96, 119, 101)
SELECTED = (224, 245, 177)
LIME = (191, 225, 70)
BORDER = (214, 229, 215)
DISABLED = (216, 226, 216)
ERROR = (190, 57, 57)
SUCCESS = (34, 125, 67)


def choose_text_file() -> str:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        return filedialog.askopenfilename(
            title="Selecciona un archivo de texto",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
        )
    finally:
        root.destroy()


def process_modex_fb(content: str) -> str:
    data = ModexInputData.from_text(content)
    return modexFB.process(data, content)


def process_modex_v(content: str) -> str:
    data = ModexInputData.from_text(content)
    return modexV.process(data, content)


def process_modex_pd(content: str) -> str:
    data = ModexInputData.from_text(content)
    return modexPD.process(data, content)


def create_output_file(
    source: Path,
    project_dir: Path,
    strategy: str | None = None,
) -> Path:
    content = source.read_text(encoding="utf-8-sig")
    if strategy is None:
        output_stem = f"{source.stem}_salida"
        output_content = f"salida\n{content}"
    else:
        processors = {
            "modexFB": process_modex_fb,
            "modexV": process_modex_v,
            "modexPD": process_modex_pd,
        }
        processor = processors[strategy]
        output_stem = f"{source.stem}_{strategy}_salida"
        output_content = f"salida - {strategy}\n{processor(content)}"

    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{output_stem}.txt"
    suffix = 2
    while output_path.exists():
        output_path = output_dir / f"{output_stem}_{suffix}.txt"
        suffix += 1

    output_path.write_text(output_content, encoding="utf-8")
    return output_path


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    wrapped_lines: list[str] = []
    for source_line in text.splitlines() or [""]:
        words = source_line.split()
        if not words:
            wrapped_lines.append("")
            continue

        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if font.size(candidate)[0] <= max_width:
                line = candidate
            else:
                if line:
                    wrapped_lines.append(line)
                    line = ""
                while font.size(word)[0] > max_width:
                    split_at = len(word)
                    while split_at > 1 and font.size(word[:split_at])[0] > max_width:
                        split_at -= 1
                    wrapped_lines.append(word[:split_at])
                    word = word[split_at:]
                line = word
        wrapped_lines.append(line)
    return wrapped_lines


def open_file_for_editing(path: Path) -> None:
    start_file = getattr(os, "startfile", None)
    if not callable(start_file):
        raise OSError("La apertura con la aplicación asociada solo está disponible en Windows.")
    start_file(str(path))


def main() -> None:
    project_dir = Path(__file__).resolve().parent
    pygame.init()
    pygame.display.set_caption("ModEx")
    icon = pygame.image.load(str(project_dir / "assets" / "modex.ico"))
    pygame.display.set_icon(icon)
    small_icon = pygame.transform.smoothscale(icon, (38, 38))
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    title_font = pygame.font.Font(None, 40)
    font = pygame.font.Font(None, 27)
    small_font = pygame.font.Font(None, 21)
    preview_font = pygame.font.Font(None, 22)

    added_files: list[Path] = []
    output_dir = project_dir / "output"
    output_files = sorted(output_dir.glob("*.txt"), key=lambda path: path.name.casefold())
    file_view = "input"
    selected_index: int | None = None
    preview_lines: list[str] = []
    preview_error: str | None = None
    status = "Añade archivos .txt y selecciona uno para ver su contenido."
    status_color = MUTED
    list_rect = pygame.Rect(30, 265, 310, 350)
    preview_rect = pygame.Rect(360, 265, 570, 350)
    add_button = pygame.Rect(30, 115, 170, 44)
    generate_button = pygame.Rect(210, 115, 170, 44)
    edit_button = pygame.Rect(390, 115, 210, 44)
    remove_button = pygame.Rect(610, 115, 170, 44)
    input_tab = pygame.Rect(30, 220, 150, 36)
    output_tab = pygame.Rect(190, 220, 150, 36)
    strategy_buttons = {
        "modexFB": pygame.Rect(30, 170, 285, 44),
        "modexV": pygame.Rect(337, 170, 285, 44),
        "modexPD": pygame.Rect(644, 170, 285, 44),
    }
    list_scroll = 0
    preview_scroll = 0
    row_height = 48
    visible_list = pygame.Rect(
        list_rect.x + 8,
        list_rect.y + 53,
        list_rect.width - 16,
        list_rect.height - 61,
    )
    visible_preview = pygame.Rect(
        preview_rect.x + 12,
        preview_rect.y + 52,
        preview_rect.width - 24,
        preview_rect.height - 64,
    )

    def active_files() -> list[Path]:
        return added_files if file_view == "input" else output_files

    running = True

    def select_file(index: int) -> None:
        nonlocal selected_index, preview_lines, preview_error, preview_scroll
        selected_index = index
        preview_scroll = 0
        try:
            content = active_files()[index].read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            preview_lines = []
            preview_error = f"No se pudo leer el archivo: {error}"
            return
        preview_error = None
        preview_lines = wrap_text(
            content or "El archivo está vacío.",
            preview_font,
            visible_preview.width - 8,
        )

    while running:
        mouse_position = pygame.mouse.get_pos()
        screen.fill(BACKGROUND)

        title = title_font.render(
            "Moderación del extremismo de opiniones en una red social",
            True,
            TEXT,
        )
        screen.blit(title, (30, 30))
        pygame.draw.circle(screen, LIME, (WINDOW_WIDTH - 50, 52), 25)
        screen.blit(small_icon, (WINDOW_WIDTH - 69, 33))
        subtitle = small_font.render(
            "Revisa entradas y salidas, o selecciona un modo para procesar el archivo.",
            True,
            MUTED,
        )
        screen.blit(subtitle, (30, 76))

        has_selection = selected_index is not None and bool(active_files())
        can_generate = has_selection and file_view == "input"
        buttons = [
            (add_button, "Añadir archivo", True),
            (generate_button, "Generar salida", can_generate),
            (edit_button, "Abrir para editar", has_selection),
            (remove_button, "Quitar de lista", has_selection),
        ]
        buttons.extend(
            (rect, strategy, can_generate)
            for strategy, rect in strategy_buttons.items()
        )
        for button_rect, label, enabled in buttons:
            color = BUTTON_HOVER if button_rect.collidepoint(mouse_position) else BUTTON
            if not enabled:
                color = DISABLED
            pygame.draw.rect(screen, color, button_rect, border_radius=8)
            button_text = font.render(label, True, WHITE if enabled else MUTED)
            screen.blit(button_text, button_text.get_rect(center=button_rect.center))

        for tab_rect, label, view_name in (
            (input_tab, f"Entradas ({len(added_files)})", "input"),
            (output_tab, f"Salidas ({len(output_files)})", "output"),
        ):
            color = SELECTED if file_view == view_name else PANEL
            if tab_rect.collidepoint(mouse_position):
                color = BUTTON_HOVER if file_view == view_name else SELECTED
            pygame.draw.rect(screen, color, tab_rect, border_radius=7)
            pygame.draw.rect(screen, BORDER, tab_rect, width=1, border_radius=7)
            tab_text = small_font.render(label, True, TEXT)
            screen.blit(tab_text, tab_text.get_rect(center=tab_rect.center))

        pygame.draw.rect(screen, PANEL, list_rect, border_radius=10)
        pygame.draw.rect(screen, BORDER, list_rect, width=1, border_radius=10)
        files = active_files()
        list_title = font.render(
            "Archivos de entrada" if file_view == "input" else "Archivos de salida",
            True,
            TEXT,
        )
        screen.blit(list_title, (list_rect.x + 14, list_rect.y + 12))
        pygame.draw.line(
            screen,
            (67, 77, 95),
            (list_rect.x + 14, list_rect.y + 45),
            (list_rect.right - 14, list_rect.y + 45),
            1,
        )
        screen.set_clip(visible_list)
        if not files:
            empty_label = "Todavía no hay archivos." if file_view == "input" else "Aún no hay salidas."
            empty_text = small_font.render(empty_label, True, MUTED)
            screen.blit(empty_text, (visible_list.x + 8, visible_list.y + 12))
        else:
            for index, file_path in enumerate(files):
                row_y = visible_list.y + index * row_height - list_scroll
                row_rect = pygame.Rect(
                    visible_list.x + 2,
                    row_y,
                    visible_list.width - 4,
                    row_height - 4,
                )
                if row_rect.bottom < visible_list.top or row_rect.top > visible_list.bottom:
                    continue
                if index == selected_index:
                    pygame.draw.rect(screen, SELECTED, row_rect, border_radius=6)
                name = small_font.render(file_path.name, True, TEXT)
                screen.blit(name, (row_rect.x + 8, row_rect.y + 3))
                path_text = small_font.render(str(file_path), True, MUTED)
                screen.blit(path_text, (row_rect.x + 8, row_rect.y + 23))
        screen.set_clip(None)

        pygame.draw.rect(screen, PANEL, preview_rect, border_radius=10)
        pygame.draw.rect(screen, BORDER, preview_rect, width=1, border_radius=10)
        preview_title = font.render(
            "Contenido de entrada" if file_view == "input" else "Contenido de salida",
            True,
            TEXT,
        )
        screen.blit(preview_title, (preview_rect.x + 14, preview_rect.y + 12))
        pygame.draw.line(
            screen,
            (67, 77, 95),
            (preview_rect.x + 14, preview_rect.y + 45),
            (preview_rect.right - 14, preview_rect.y + 45),
            1,
        )
        screen.set_clip(visible_preview)
        if preview_error:
            error_text = small_font.render(preview_error, True, ERROR)
            screen.blit(error_text, (visible_preview.x + 4, visible_preview.y + 4))
        elif selected_index is None:
            prompt = small_font.render(
                "Selecciona un archivo para leerlo.",
                True,
                MUTED,
            )
            screen.blit(prompt, (visible_preview.x + 4, visible_preview.y + 4))
        else:
            line_height = 24
            first_line = preview_scroll // line_height
            last_line = (preview_scroll + visible_preview.height) // line_height + 1
            for line_index, line in enumerate(preview_lines[first_line:last_line], start=first_line):
                line_surface = preview_font.render(line, True, TEXT)
                line_y = visible_preview.y + line_index * line_height - preview_scroll
                screen.blit(line_surface, (visible_preview.x + 4, line_y))
        screen.set_clip(None)

        status_text = small_font.render(status, True, status_color)
        screen.blit(status_text, (30, 638))
        output_hint = small_font.render(
            "Las salidas se guardan en output y también aparecen en la pestaña Salidas.",
            True,
            MUTED,
        )
        screen.blit(output_hint, (30, 678))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                if visible_list.collidepoint(mouse_position):
                    max_scroll = max(0, len(files) * row_height - visible_list.height)
                    list_scroll = max(0, min(max_scroll, list_scroll - event.y * row_height))
                elif visible_preview.collidepoint(mouse_position):
                    max_scroll = max(
                        0,
                        len(preview_lines) * 24 - visible_preview.height,
                    )
                    preview_scroll = max(
                        0,
                        min(max_scroll, preview_scroll - event.y * 24),
                    )
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if input_tab.collidepoint(event.pos) or output_tab.collidepoint(event.pos):
                    file_view = "input" if input_tab.collidepoint(event.pos) else "output"
                    list_scroll = 0
                    files = active_files()
                    if files:
                        select_file(0)
                    else:
                        selected_index = None
                        preview_lines = []
                        preview_error = None
                        preview_scroll = 0
                    status = (
                        f"Viendo las {'entradas' if file_view == 'input' else 'salidas'}."
                    )
                    status_color = MUTED
                elif add_button.collidepoint(event.pos):
                    try:
                        chosen_file = choose_text_file()
                    except tk.TclError as error:
                        status = f"No se pudo abrir el selector de archivos: {error}"
                        status_color = ERROR
                    else:
                        if chosen_file:
                            path = Path(chosen_file)
                            if path not in added_files:
                                added_files.append(path)
                                file_view = "input"
                                list_scroll = max(
                                    0,
                                    len(added_files) * row_height - visible_list.height,
                                )
                                select_file(len(added_files) - 1)
                                if preview_error:
                                    status = preview_error
                                    status_color = ERROR
                                else:
                                    status = f"Archivo añadido y leído: {path.name}"
                                    status_color = SUCCESS
                            else:
                                file_view = "input"
                                select_file(added_files.index(path))
                                if preview_error:
                                    status = preview_error
                                    status_color = ERROR
                                else:
                                    status = "Ese archivo ya está en la lista; se seleccionó."
                                    status_color = MUTED
                elif (
                    generate_button.collidepoint(event.pos)
                    and selected_index is not None
                    and file_view == "input"
                ):
                    try:
                        output_path = create_output_file(
                            added_files[selected_index],
                            project_dir,
                        )
                    except (OSError, UnicodeError) as error:
                        status = f"No se pudo generar el archivo: {error}"
                        status_color = ERROR
                    else:
                        output_files.append(output_path)
                        file_view = "output"
                        list_scroll = max(
                            0,
                            len(output_files) * row_height - visible_list.height,
                        )
                        select_file(len(output_files) - 1)
                        if preview_error:
                            status = preview_error
                            status_color = ERROR
                        else:
                            status = f"Archivo generado y visible: {output_path.name}"
                            status_color = SUCCESS
                elif (
                    edit_button.collidepoint(event.pos)
                    and selected_index is not None
                    and has_selection
                ):
                    try:
                        open_file_for_editing(active_files()[selected_index])
                    except OSError as error:
                        status = f"No se pudo abrir el archivo para editarlo: {error}"
                        status_color = ERROR
                    else:
                        status = f"Archivo abierto para editar: {active_files()[selected_index].name}"
                        status_color = SUCCESS
                elif (
                    remove_button.collidepoint(event.pos)
                    and selected_index is not None
                    and has_selection
                ):
                    removed_files = active_files()
                    removed_path = removed_files.pop(selected_index)
                    if removed_files:
                        select_file(min(selected_index, len(removed_files) - 1))
                    else:
                        selected_index = None
                        preview_lines = []
                        preview_error = None
                        preview_scroll = 0
                    list_scroll = min(
                        list_scroll,
                        max(0, len(removed_files) * row_height - visible_list.height),
                    )
                    status = f"Archivo retirado de la lista: {removed_path.name}"
                    status_color = SUCCESS
                elif visible_list.collidepoint(event.pos) and files:
                    clicked_index = (
                        (event.pos[1] - visible_list.y + list_scroll) // row_height
                    )
                    if 0 <= clicked_index < len(files):
                        select_file(clicked_index)
                        status = f"Seleccionado: {files[clicked_index].name}"
                        status_color = ERROR if preview_error else MUTED
                elif can_generate:
                    selected_strategy = next(
                        (
                            strategy
                            for strategy, rect in strategy_buttons.items()
                            if rect.collidepoint(event.pos)
                        ),
                        None,
                    )
                    if selected_strategy is not None:
                        try:
                            output_path = create_output_file(
                                added_files[selected_index],
                                project_dir,
                                selected_strategy,
                            )
                        except (OSError, UnicodeError, ValueError) as error:
                            status = f"No se pudo ejecutar {selected_strategy}: {error}"
                            status_color = ERROR
                        else:
                            status = f"Salida de {selected_strategy}: {output_path.name}"
                            status_color = SUCCESS
                            output_files.append(output_path)
                            file_view = "output"
                            list_scroll = max(
                                0,
                                len(output_files) * row_height - visible_list.height,
                            )
                            select_file(len(output_files) - 1)
                            if preview_error:
                                status = preview_error
                                status_color = ERROR
                            else:
                                status = (
                                    f"Salida de {selected_strategy} generada y visible: "
                                    f"{output_path.name}"
                                )
                                status_color = SUCCESS

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
