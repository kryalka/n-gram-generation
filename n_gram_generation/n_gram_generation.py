import reflex as rx

from .components import main_card, keyboard_guard


def index() -> rx.Component:
    page = rx.center(
        main_card(),

        width="100%",
        min_height="100vh",

        padding=rx.breakpoints(
            initial="12px",
            sm="24px",
            md="40px",
        ),

        background=rx.color_mode_cond(
            (
                "linear-gradient(135deg, "
                "#EEF2FF 0%, #F8FAFC 55%, #F1F5F9 100%)"
            ),
            (
                "linear-gradient(135deg, "
                "#0B0D14 0%, #11131C 55%, #151822 100%)"
            ),
        ),

        font_family=(
            "-apple-system, BlinkMacSystemFont, "
            "'Segoe UI', sans-serif"
        ),
    )

    return rx.fragment(
        keyboard_guard(),
        page,
    )


app = rx.App()
app.add_page(index, title="Подсказки для текста")
