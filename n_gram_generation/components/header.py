import reflex as rx

from ..state import State


def model_status() -> rx.Component:
    loading_status = rx.hstack(
        rx.spinner(size="1"),
        rx.text(
            "Загружаю подсказки",
            size="2",
            weight="medium",
        ),
        padding_x="12px",
        padding_y="6px",
        border_radius="999px",
        background=rx.color("amber", 3),
        color=rx.color("amber", 11),
        align="center",
    )

    error_status = rx.hstack(
        rx.box(
            width="8px",
            height="8px",
            border_radius="50%",
            background=rx.color("red", 9),
        ),
        rx.text(
            "Не загрузилось",
            size="2",
            weight="medium",
        ),
        padding_x="12px",
        padding_y="6px",
        border_radius="999px",
        background=rx.color("red", 3),
        color=rx.color("red", 11),
        align="center",
    )

    ready_status = rx.hstack(
        rx.box(
            width="8px",
            height="8px",
            border_radius="50%",
            background=rx.color("green", 9),
        ),
        rx.text(
            "Подсказки готовы",
            size="2",
            weight="medium",
        ),
        padding_x="12px",
        padding_y="6px",
        border_radius="999px",
        background=rx.color("green", 3),
        color=rx.color("green", 11),
        align="center",
    )

    idle_status = rx.hstack(
        rx.box(
            width="8px",
            height="8px",
            border_radius="50%",
            background=rx.color("gray", 8),
        ),
        rx.text(
            "Жду текст",
            size="2",
            weight="medium",
        ),
        padding_x="12px",
        padding_y="6px",
        border_radius="999px",
        background=rx.color("gray", 3),
        color=rx.color("gray", 11),
        align="center",
    )

    status = rx.cond(
        State.model_loaded,
        ready_status,
        idle_status,
    )

    status = rx.cond(
        State.load_error != "",
        error_status,
        status,
    )

    status = rx.cond(
        State.loading_model,
        loading_status,
        status,
    )

    return status

def header() -> rx.Component:
    title = rx.vstack(
        rx.heading(
            "Подскажу продолжение",
            size="7",
            weight="bold",
        ),
        align="start",
        spacing="1",
    )

    theme_button = rx.button(
        rx.color_mode_cond("☀️", "🌙"),
        on_click=rx.toggle_color_mode,
        title="Сменить тему",
        variant="soft",
        color_scheme="gray",
        radius="full",
    )

    right_part = rx.hstack(
        model_status(),
        theme_button,
        align="center",
        spacing="3",
    )

    top_part = rx.hstack(
        title,
        rx.spacer(),
        right_part,
        width="100%",
        align="center",
    )

    description = rx.text(
        "Напиши фразу на английском — я предложу, как её продолжить.",
        color=rx.color("gray", 10),
        size="3",
    )

    return rx.vstack(
        top_part,
        description,
        width="100%",
        align="start",
        spacing="3",
    )