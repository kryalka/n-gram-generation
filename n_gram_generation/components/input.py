import reflex as rx

from ..state import State

def key_hint(key: str, text: str) -> rx.Component:
    key_box = rx.text(
        key,
        size="1",
        weight="bold",
        padding_x="7px",
        padding_y="3px",
        border_radius="6px",
        border="1px solid",
        border_color=rx.color("gray", 6),
        background=rx.color("gray", 3),
        color=rx.color("gray", 11),
        font_family="monospace",
    )

    hint_text = rx.text(
        text,
        size="2",
        color=rx.color("gray", 10),
    )

    return rx.hstack(
        key_box,
        hint_text,
        spacing="2",
        align="center",
    )

def keyboard_guard() -> rx.Component:
    script = r"""
    (() => {
        const handler = (event) => {
            const target = event.target;

            if (target == null) {
                return;
            }

            if (target.closest == undefined) {
                return;
            }

            const text_area = target.closest("#text_input");

            if (text_area == null) {
                return;
            }

            const suggestions = document.getElementById("suggestions_box");

            if (suggestions == null) {
                return;
            }

            let block_key = false;

            if (event.key === "ArrowUp") {
                block_key = true;
            }

            if (event.key === "ArrowDown") {
                block_key = true;
            }

            if (event.key === "Escape") {
                block_key = true;
            }

            if (event.key === "Enter") {
                if (event.shiftKey === false) {
                    block_key = true;
                }
            }

            if (block_key === true) {
                event.preventDefault();
            }
        };

        if (window.__ngramKeyboardGuard != null) {
            document.removeEventListener(
                "keydown",
                window.__ngramKeyboardGuard,
                true
            );
        }

        window.__ngramKeyboardGuard = handler;

        document.addEventListener(
            "keydown",
            handler,
            true
        );
    })();
    """

    return rx.script(script)

def text_input_block() -> rx.Component:
    title = rx.text(
        "Твой текст",
        size="1",
        weight="bold",
        color=rx.color("gray", 9),
        letter_spacing="0.12em",
    )

    text_area = rx.text_area(
        id="text_input",
        placeholder="Например: Thank you",
        value=State.user_text,
        on_change=State.update_text,
        on_key_down=State.handle_key_down,

        rows="5",
        resize="vertical",
        size="3",
        variant="surface",

        width="100%",
        min_height="150px",
        max_height="320px",

        padding="18px",
        font_size="16px",
        line_height="1.6",

        border_radius="16px",
        border="1px solid",
        border_color=rx.color("gray", 6),
        background=rx.color("gray", 2),

        transition="all 0.2s ease",

        _focus={
            "border_color": rx.color("indigo", 8),
            "box_shadow": "0 0 0 3px rgba(99, 102, 241, 0.12)",
        },
    )

    hints = rx.flex(
        key_hint("↑ ↓", "выбрать"),
        key_hint("Enter", "вставить"),
        key_hint("Esc", "скрыть"),
        gap="12px",
        wrap="wrap",
    )

    return rx.vstack(
        title,
        text_area,
        hints,
        width="100%",
        align="stretch",
        spacing="3",
    )