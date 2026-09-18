import re
import reflex as rx

from .models import get_suggester, tokenize


def get_suggestion(result: list[str]) -> str:
    if not result:
        return ""

    return re.sub(r" ([.,!?;:])", r"\1", " ".join(result))


class State(rx.State):
    user_text: str = ""
    suggestions: list[str] = []
    selected_index: int = -1
    loading_model: bool = False
    load_error: str = ""
    model_loaded: bool = False
    show_no_suggestions: bool = False

    @rx.event
    def update_text(self, value: str):
        self.user_text = value

        self.suggestions = []
        self.selected_index = -1
        self.load_error = ""
        self.show_no_suggestions = False

        if value.strip() == "":
            return

        words = tokenize(value)

        if not self.model_loaded:
            self.loading_model = True
            yield

        last_word_complete = False

        if value[-1].isspace():
            last_word_complete = True

        if value[-1] in ".,!?;:":
            last_word_complete = True

        try:
            results = get_suggester().suggest_text(
                words,
                n_words=3,
                n_texts=3,
                last_word_complete=last_word_complete,
            )
        except Exception:
            self.loading_model = False
            self.load_error = "Не удалось загрузить модель"
            return

        self.loading_model = False
        self.model_loaded = True

        for result in results:
            suggestion = get_suggestion(result)

            if suggestion != "":
                if suggestion not in self.suggestions:
                    self.suggestions.append(suggestion)

        if len(self.suggestions) > 0:
            self.selected_index = 0
        else:
            self.show_no_suggestions = True

    @rx.event
    def handle_key_down(self, key: str):
        if len(self.suggestions) == 0:
            return

        if key == "Escape":
            self.suggestions = []
            self.selected_index = -1
            self.show_no_suggestions = False
            return

        if key == "ArrowDown":
            self.selected_index = self.selected_index + 1

            if self.selected_index >= len(self.suggestions):
                self.selected_index = 0

            return

        if key == "ArrowUp":
            self.selected_index = self.selected_index - 1

            if self.selected_index < 0:
                self.selected_index = len(self.suggestions) - 1

            return

        if key == "Enter":
            if self.selected_index >= 0:
                suggestion = self.suggestions[self.selected_index]
                self.apply_suggestion(suggestion)

    @rx.event
    def apply_suggestion(self, suggestion: str):
        last_symbol = self.user_text[-1]

        if last_symbol.isspace():
            self.user_text = self.user_text + suggestion

        elif last_symbol in ".,!?;:":
            self.user_text = self.user_text + " " + suggestion

        else:
            words = tokenize(self.user_text)
            last_word = words[-1]

            part_to_add = suggestion[len(last_word):]
            self.user_text = self.user_text + part_to_add

        self.suggestions = []
        self.selected_index = -1
        self.show_no_suggestions = False

        return rx.set_focus("text_input")