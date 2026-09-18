import reflex as rx

from .header import header
from .input import text_input_block
from .messages import (
    loading_block,
    error_block,
    no_suggestions_block,
)
from .suggestions import suggestions_block


def main_card() -> rx.Component:
    return rx.vstack(
        header(),
        text_input_block(),
        loading_block(),
        error_block(),
        no_suggestions_block(),
        suggestions_block(),

        spacing="5",
        align="stretch",

        width="100%",
        max_width="780px",

        padding=rx.breakpoints(
            initial="18px",
            sm="26px",
            md="36px",
        ),

        background=rx.color("gray", 1),

        border="1px solid",
        border_color=rx.color("gray", 5),
        border_radius="24px",

        box_shadow=rx.color_mode_cond(
            "0 24px 70px rgba(44, 66, 112, 0.12)",
            "0 24px 70px rgba(0, 0, 0, 0.35)",
        ),
    )
