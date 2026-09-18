import reflex as rx

from ..state import State

def loading_block() -> rx.Component:
    content = rx.hstack(
        rx.spinner(size="1"),
        rx.text(
            "Загружаю подсказки, подожди немного…",
            size="2",
            color=rx.color("gray", 10),
        ),
        align="center",
        spacing="2",
    )

    return rx.cond(
        State.loading_model,
        content,
    )

def error_block() -> rx.Component:
    message = rx.text(
        State.load_error,
        size="2",
        color=rx.color("red", 11),
    )

    box = rx.box(
        message,
        width="100%",
        padding="14px",
        border_radius="12px",
        background=rx.color("red", 3),
        border="1px solid",
        border_color=rx.color("red", 6),
    )

    return rx.cond(
        State.load_error != "",
        box,
    )

def no_suggestions_block() -> rx.Component:
    message = rx.text(
        "Пока нет подходящих подсказок. Попробуй другие слова.",
        color=rx.color("gray", 10),
    )

    box = rx.box(
        message,
        width="100%",
        padding="20px",
        text_align="center",
        border_radius="14px",
        background=rx.color("gray", 2),
    )

    return rx.cond(
        State.show_no_suggestions,
        box,
    )