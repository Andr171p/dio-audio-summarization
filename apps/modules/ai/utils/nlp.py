import re

import nltk
from mawo_pymorphy3 import create_analyzer
from nltk.tokenize import word_tokenize

nltk.download("punkt")

nltk.download("stopwords")
stopwords = nltk.corpus.stopwords.words("russian")

analyzer = create_analyzer()


def remove_extra_chars(text: str) -> str:
    """Удаление лишних символов в тексте, а именно пунктуации + лишние пробелы"""

    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)  # Удаление пунктуации
    text = re.sub(r"\s+", " ", text)  # Удаление лишних пробелов
    return text.strip()


def remove_stopwords(text: str) -> str:
    """Удаление стоп-слов"""

    return " ".join([word for word in text.split() if word not in stopwords])


def remove_emoji(text: str) -> str:
    """Удаление эмодзи из текста"""

    pattern = re.compile(
        r"["
        r"\U0001f600-\U0001f64f"  # эмоции
        r"\U0001f300-\U0001f5ff"  # символы и пиктограммы
        "\U0001f680-\U0001f6ff"  # транспорт и карты  # noqa: RUF039
        r"\U0001f1e0-\U0001f1ff"  # флаги
        r"\U00002702-\U000027b0"
        r"\U000024c2-\U0001f251"
        r"]+",
        flags=re.UNICODE,
    )
    return pattern.sub(r"", text)


def tokenize_text(text: str) -> list[str]:
    """Токенизация текста"""

    return word_tokenize(text, language="russian")


def lemmatize(words: list[str]) -> list[str]:
    """Лемматизация русских слов"""

    return [analyzer.parse(word)[0].normal_form for word in words]


def preprocess_text(text: str) -> str:
    """Предварительная обработка русского текста:
     - Удаление лишних слов и символов (стоп-слова, пунктуация, эмодзи)
     - Токенизация текста
     - Лемматизация
    """

    cleaned_text = remove_emoji(remove_stopwords(remove_extra_chars(text)))
    tokens = tokenize_text(cleaned_text)
    lemmas = lemmatize(tokens)
    return " ".join(lemmas)
