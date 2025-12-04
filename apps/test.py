import logging

from modules.audio.infrastructure.ai.embeddings import RemoteHTTPEmbeddings

logging.basicConfig(level=logging.INFO)

embeddings = RemoteHTTPEmbeddings(
    base_url="https://andr17p-hf-embeddings-api.hf.space"
)

text = "Hello world"

print(embeddings.embed_query(text))
