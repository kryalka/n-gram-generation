import reflex as rx

from ..state import State

def suggestion_button(
    suggestion,
    index,
) -> rx.Component:

    number = rx.center(
        rx.text(
            index + 1,
            size="2",
            weight="bold",
        ),
        width="30px",
        height="30px",
        min_width="30px",
        border_radius="9px",
        background=rx.cond(
            index == State.selected_index,
            "rgba(255,255,255,0.18)",
            rx.color("gray", 4),
        ),
    )

    text = rx.text(
        suggestion,
        size="3",
        text_align="left",
    )

    enter_hint = rx.cond(
        index == State.selected_index,
        rx.text(
            "Enter",
            size="1",
            weight="bold",
            opacity="0.7",
        ),
    )

    content = rx.hstack(
        number,
        text,
        rx.spacer(),
        enter_hint,
        width="100%",
        align="center",
        spacing="3",
    )

    return rx.button(
        content,

        on_click=lambda: State.apply_suggestion(
            suggestion
        ),

        variant=rx.cond(
            index == State.selected_index,
            "solid",
            "soft",
        ),

        color_scheme="indigo",

        width="100%",
        height="auto",
        min_height="62px",

        padding_x="16px",
        padding_y="12px",

        border_radius="14px",

        justify_content="flex-start",
        white_space="normal",

        cursor="pointer",

        transition=(
            "transform 0.15s ease, "
            "box-shadow 0.15s ease"
        ),

        _hover={
            "transform": "translateY(-1px)",
            "box_shadow": (
                "0 6px 20px "
                "rgba(0, 0, 0, 0.08)"
            ),
        },
    )

def suggestions_block() -> rx.Component:
    title = rx.hstack(
        rx.text(
            "Варианты продолжения",
            size="1",
            weight="bold",
            color=rx.color("gray", 9),
            letter_spacing="0.12em",
        ),

        rx.spacer(),

        rx.text(
            "Выбери, что дописать",
            size="2",
            color=rx.color("gray", 9),
        ),

        width="100%",
    )

    buttons = rx.foreach(
        State.suggestions,
        suggestion_button,
    )

    content = rx.vstack(
        title,
        buttons,
        id="suggestions_box",
        width="100%",
        align="stretch",
        spacing="2",
    )

    return rx.cond(
        State.suggestions.length() > 0,
        content,
    )
