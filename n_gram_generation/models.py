import re
from typing import List, Union
from collections import Counter
from functools import lru_cache
import os
import pickle

class PrefixTreeNode:
    def __init__(self):
        self.children: dict[str, PrefixTreeNode] = {}
        self.is_end_of_word = False

class PrefixTree:
    def __init__(self, vocabulary: List[str]):
        """
        vocabulary: список всех уникальных токенов в корпусе
        """
        self.root = PrefixTreeNode()

        for word in vocabulary:
            node = self.root

            for letter in word:
                if letter not in node.children:
                    node.children[letter] = PrefixTreeNode()

                node = node.children[letter]

            node.is_end_of_word = True

    def search_prefix(self, prefix) -> List[str]:
        """
        Возвращает все слова, начинающиеся на prefix
        prefix: str – префикс слова
        """

        node = self.root

        for letter in prefix:
            if letter not in node.children:
                return []

            node = node.children[letter]

        result = []

        nodes = [node]
        words = [prefix]

        while nodes:
            node = nodes.pop()
            word = words.pop()

            if node.is_end_of_word:
                result.append(word)

            for letter in node.children:
                nodes.append(node.children[letter])
                words.append(word + letter)

        return result


class WordCompletor:
    def __init__(self, corpus, min_count=2):
        """
        corpus: list – корпус текстов
        """
        self.counts = Counter()

        for text in corpus:
            self.counts.update(text)

        for word in list(self.counts):
            if self.counts[word] < min_count:
                del self.counts[word]
                
        self.total_words = sum(self.counts.values())
        vocabulary = list(self.counts)
        self.prefix_tree = PrefixTree(vocabulary)

    def get_words_and_probs(self, prefix: str) -> tuple[list[str], list[float]]:
        """
        Возвращает список слов, начинающихся на prefix,
        с их вероятностями (нормировать ничего не нужно)
        """
        words, probs = [], []

        words = self.prefix_tree.search_prefix(prefix)
        words.sort(key=lambda word: self.counts[word], reverse=True)

        for word in words:
            prob = self.counts[word] / self.total_words
            probs.append(prob)

        return words, probs


class NGramLanguageModel:
    def __init__(self, corpus, n):
        self.n = n
        self.counts = {}

        for text in corpus:
            for i in range(n, len(text)):
                prefix = tuple(text[i - n:i])
                next_word = text[i]

                if prefix not in self.counts:
                    self.counts[prefix] = Counter({next_word: 1})
                else:
                    self.counts[prefix][next_word] += 1

    def get_next_words_and_probs(self, prefix: list) -> tuple[list[str], list[float]]:
        """
        Возвращает список слов, которые могут идти после prefix,
        а так же список вероятностей этих слов
        """

        if len(prefix) == 1 and self.n == 2:
            if not hasattr(self, "one_word_counts"):
                self.one_word_counts = {}
            word = prefix[-1]
            if word not in self.one_word_counts:
                counts = Counter()
                for context, following in self.counts.items():
                    if context[-1] == word:
                        counts.update(following)
                self.one_word_counts[word] = counts
            counts = self.one_word_counts[word]
        else:
            counts = self.counts.get(tuple(prefix[-self.n:]))

        if not counts:
            return [], []

        total = sum(counts.values())
        words = list(counts)
        probs = [counts[word] / total for word in words]
        return words, probs


class TextSuggestion:
    def __init__(self, word_completor, n_gram_model):
        self.word_completor = word_completor
        self.n_gram_model = n_gram_model

    def suggest_text(self, text: Union[str, list], n_words=3, n_texts=1, last_word_complete=False) -> list[list[str]]:
        """
        Возвращает возможные варианты продолжения текста (по умолчанию только один)
        
        text: строка или список слов – написанный пользователем текст
        n_words: число слов, которые дописывает n-граммная модель
        n_texts: число возвращаемых продолжений (пока что только одно)
        
        return: list[list[srt]] – список из n_texts списков слов, по 1 + n_words слов в каждом
        last_word_complete: последнее слово уже закончено пробелом
        """

        suggestions = []

        if last_word_complete:
            words, probs = self.n_gram_model.get_next_words_and_probs(text)
            words = [
                word for word, prob in sorted(zip(words, probs), key=lambda pair: pair[1], reverse=True)
                if any(letter.isalpha() for letter in word)
            ]
            original_prefix = text
            remaining_words = n_words - 1
        else:
            words, probs = self.word_completor.get_words_and_probs(text[-1])
            original_prefix = text[:-1]
            remaining_words = n_words

        if len(words) == 0:
            return [[]]

        for word in words[:n_texts]:
            # word = words[0]
            suggestion = [word]
            text = original_prefix + [word]

            for _ in range(remaining_words):
                words, probs = self.n_gram_model.get_next_words_and_probs(text)

                if len(words) == 0:
                    break

                best_word, best_prob = words[0], probs[0]

                for i in range(len(words)):
                    if probs[i] > best_prob:
                        best_prob, best_word = probs[i], words[i]

                suggestion.append(best_word)
                text.append(best_word)

            suggestions.append(suggestion)

        return suggestions


def clean_emails(emails):
    # добавим колонку, в которой будет текст письма + пока что ниже есть ненужная часть
    emails["body"] = emails["message"].apply(lambda text: text.split("\n\n", 1)[1].strip())

    # первым делом убираю мусор вида: =20, =\n и т.д.
    emails["body"] = emails["body"].str.replace(r"=\n", "", regex=True)
    emails["body"] = emails["body"].str.replace(r"=[0-9A-Fa-f]{2}", "", regex=True) 

    # убираем вложения (названия файлов)
    emails["body"] = emails["body"].str.replace(r"<<[^>]+>>", "", regex=True)
    emails["body"] = emails["body"].str.replace(r"^\s*-\s*\S+\.(xls|doc|pdf|ppt|gif|jpg)\s*$", "", regex=True, flags=re.MULTILINE | re.IGNORECASE)

    # убираем явные рассылки/спам:
    emails["body"] = emails["body"].str.replace(
    r"(?is)(?:this e-?mail (?:message|communication)|the information contained (?:in|herein)).*?(?:sole use|confidential|privileged|intended recipient).?", 
        "", regex=True)
    emails["body"] = emails["body"].str.replace(r"(?is)the information contained in this communication may be confidential.*?(delete the original message.*?\.|$)", 
                                                "", regex=True)

    # убираем пересылки и цитирования, чтобы оставить только оригинальный текст
    emails["body"] = emails["body"].str.split(r"(?i)(?:-{2,}\s*)?(?:Original Message|Forwarded by|Reply Message)\s*:?", n=1).str[0]

    # убираем цитаты, то есть строки где есть ">", чтобы опять же оставить только оригинальный текст
    emails["body"] = emails["body"].str.replace(r"^>.*$", "", regex=True, flags=re.MULTILINE)

    # убираем повторяющиеся заголовки, а именно From To Cc и тд
    emails["body"] = emails["body"].str.replace(r"^(?:From|To|Cc|Bcc|Subject|Sent|Date):.*$", "", regex=True, flags=re.MULTILINE | re.IGNORECASE)

    # поработаем с email, url, телефонами, html: просто уберем, чтобы не было "угадывания" телефофнов и тд, оно нам не надо...
    emails["body"] = (emails["body"]
        .str.replace(r"\S+@\S+", "", regex=True)
        .str.replace(r"https?://\S+", "", regex=True)
        .str.replace(r"\(?\+?\d{0,2}\)?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?:\s?(?:x|ext\.?)\s?\d+)?", "", regex=True)
    )
    emails["body"] = emails["body"].str.replace(r"<[^>]+>", "", regex=True)

    # мне кажется, что надо отрезать подписи (имена и тд)
    flag = (r"(?im)^[ \t]*(?:Regards|Best regards|Best|Thanks|Thank you|" r"Sincerely|Cheers|Phillip|Phillip Allen)[ \t]*[,.]?[ \t]*(?=\n|$)")
    emails["body"] = (emails["body"].str.split(flag, n=1).str[0].str.strip())

    # убираем разделители и мусор (======= -------) <= вот такое убираем 
    emails["body"] = emails["body"].str.replace(r"[-=_]{3,}", "", regex=True)
    emails["body"] = emails["body"].str.replace(r"[~]{3,}", "", regex=True)

    # приведем переносы к единому виду
    emails["body"] = (emails["body"].str.replace(r"\n{2,}", "\n", regex=True).str.replace(r"[ \t]{2,}", " ", regex=True))

    # возможно во время моей чистки появились пробелы в конце, поэтому убираем и их
    emails["body"] = emails["body"].str.strip()

    # и последнее: пытаемся и стараемся убрать письма-рассылки/спам/автоответы/системные уведомления целиком
    spam = re.compile(
        r"(?i)unsubscribe|mailing list|egroups|remove me from this|"
        r"click here|out of the office|<a href|<A HREF|"
        r"was delivered to the following recipient|delivery report|"
        r"newsletter|no longer wish to receive"
    )
    emails = emails[~emails["body"].str.contains(spam, regex=True, na=False)]

    # еще после чистки часть писем схлопнется в пустую строку 
    # (например, если письмо целиком состояло из пересылки или подписи) 
    # хочу выкинуть их. + выкинула дубли писем
    emails = emails[emails["body"].str.len() > 0]
    emails = emails.drop_duplicates(subset="body")

    return emails


def tokenize(text):
    return re.findall(r"\w+(?:'\w+)?|[.,!?;:]", text)


def load_corpus():
    import pandas as pd

    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "data", "emails.csv")
    emails = pd.read_csv(csv_path)
    emails = clean_emails(emails)
    emails["tokens"] = emails["body"].apply(tokenize)
    return emails["tokens"].tolist()


def load_or_build_models():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(base_dir, "data", "models_cache.pkl")

    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    corpus = load_corpus()
    wc = WordCompletor(corpus)
    ngram = NGramLanguageModel(corpus, n=2)

    with open(cache_path, "wb") as f:
        pickle.dump((wc, ngram), f)

    return wc, ngram


@lru_cache(maxsize=1)
def get_suggester():
    word_completor, n_gram_model = load_or_build_models()
    return TextSuggestion(word_completor, n_gram_model)
