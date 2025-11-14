from typing import Final, Literal

from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Стратегия для суммаризации
Strategy = Literal["simple", "extractive", "abstractive"]

llm: Final[BaseChatModel] = ...


class Summarizer(ABC):
    @abstractmethod
    async def summarize(self, text: str, **kwargs) -> str: ...


class SimpleSummarizer(Summarizer):
    async def summarize(self, text: str, **kwargs) -> str: ...


class ExtractiveSummarizer(Summarizer):
    async def summarize(self, text: str, **kwargs) -> str: ...


class AbstractiveSummarizer(Summarizer):
    async def summarize(self, text: str, **kwargs) -> str: ...


def choose_strategy(text: str) -> Strategy: ...


async def summarize(text: str, strategy: Strategy = "simple") -> str:
    ...
