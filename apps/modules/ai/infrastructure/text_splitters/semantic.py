import logging

import numpy as np
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

from ...utils.nlp import preprocess_text

logger = logging.getLogger(__name__)


class SemanticTextSplitter:
    """Разбиение текста на чанки по семантическим (смысловым) кластерам.

    Основные этапы:
        1. Разделение текста на предложения/сегменты
        2. Генерация эмбеддингов для каждого сегмента
        3. Кластеризация сегментов по смыслу (K-means)
        4. Определение оптимального числа кластеров (метод локтя)
    """

    N_INIT = 10
    MIN_ELBOW_POINTS = 6  # Минимальное количество точек для реализации метода локтя

    def __init__(
            self,
            embeddings: Embeddings,
            sentence_separator: str = "\n\n",
            batch_size: int = 32,
            min_chunk_sentences: int = 1,
            random_state: int = 42,
    ) -> None:
        self._embeddings = embeddings
        self._sentence_separator = sentence_separator
        self._batch_size = batch_size
        self._min_chunk_sentences = min_chunk_sentences
        self._random_state = random_state

    def _determine_k(self, embeddings: np.ndarray, k_min: int = 2, k_max: int = 20) -> int:
        """Определение оптимального количество кластеров методом локтя.

        :param embeddings: Массив ембедингов размером (n_samples, n_features).
        :param k_min: Минимальное количество кластеров.
        :param k_max: Максимальное количество кластеров.
        :returns: Оптимальное количество кластеров.
        """

        logger.debug("Start determining optimal clusters")
        k_max = min(k_max, len(embeddings) - 1)
        clusters = list(range(k_min, k_max + 1))
        metrics: list[float] = [
            (KMeans(n_clusters=cluster, random_state=self._random_state, n_init=self.N_INIT)
             .fit(embeddings))
            .inertia_
            for cluster in clusters
        ]
        return self._elbow(k_min, clusters, metrics)

    @classmethod
    def _elbow(cls, k_min: int, clusters: list[int], metrics: list[float]) -> int:
        """Алгоритм поиска точки 'лома' на графике инерции"""

        if len(clusters) < cls.MIN_ELBOW_POINTS:
            logger.warning("Clusters to small for elbow calculation")
            return k_min

        score: list[float] = []
        logger.debug("Start elbow calculation for %s clusters", len(clusters))
        for i in range(1, clusters[-3]):  # -3, так как нудно минимум 2 точки для регрессии
            idx = i + k_min - 1
            x1 = np.array(clusters[: idx + 1]).reshape(-1, 1)
            y1 = np.array(metrics[: idx + 1])
            x2 = np.array(clusters[idx:]).reshape(-1, 1)
            y2 = np.array(metrics[idx:])
            reg1 = LinearRegression().fit(x1, y1)
            reg2 = LinearRegression().fit(x2, y2)
            y1_pred = reg1.predict(x1)
            y2_pred = reg2.predict(x2)
            score.append(mean_squared_error(y1, y1_pred) + mean_squared_error(y2, y2_pred))
        return int(np.argmin(score) + k_min)

    def _embed_sentences(self, sentences: list[str]) -> list[list[float]]:
        """Векторизация текста по предложениям"""

        if len(sentences) <= self._batch_size:
            embeddings = self._embeddings.embed_documents(sentences)
        else:
            embeddings: list[list[float]] = []
            for i in range(0, len(sentences), self._batch_size):
                batch_embeddings = self._embeddings.embed_documents(
                    sentences[i:i + self._batch_size]
                )
                embeddings.extend(batch_embeddings)
        return embeddings

    def split_text(self, text: str) -> list[Document]:
        if not text.strip():
            return []
        preprocessed_text = preprocess_text(text)
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
        sentences: list[str] = [
            sentence.strip()
            for sentence in splitter.split_text(preprocessed_text)
            if sentence.strip()
        ]
        embeddings = self._embed_sentences(sentences)
        embeddings = np.array(embeddings)
        k_optimal = self._determine_k(embeddings)
        logger.debug("%s optimal clusters calculated", k_optimal)
        kmeans = KMeans(n_clusters=k_optimal, random_state=self._random_state, n_init=self.N_INIT)
        labels = kmeans.fit_predict(embeddings)
        cluster_to_sentences_map: dict[int, list[str]] = {}
        for sentence, label in zip(sentences, labels, strict=False):
            cluster_to_sentences_map.setdefault(int(label), []).append(sentence)
        clusters = len(cluster_to_sentences_map)
        return [
            Document(
                page_content="\n\n".join(sentences),
                metadata={
                    "cluster": cluster,
                    "total_clusters": clusters,
                    "sentences_count": len(sentences),
                }
            )
            for cluster, sentences in cluster_to_sentences_map.items()
        ]
