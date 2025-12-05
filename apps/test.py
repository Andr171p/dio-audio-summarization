import logging

from modules.ai.infrastructure.embeddings import RemoteHTTPEmbeddings
from modules.ai.infrastructure.text_splitters import SemanticTextSplitter

logging.basicConfig(level=logging.DEBUG)

embeddings = RemoteHTTPEmbeddings(
    base_url="https://andr17p-hf-embeddings-api.hf.space"
)

splitter = SemanticTextSplitter(
    embeddings=embeddings, sentence_separator="\n\n", batch_size=32
)

with open("result.txt", encoding="utf-8") as file:
    text = file.read()

print(len(text))

docs = splitter.split_text(text)

print(len(docs))
for doc in docs:
    print("=" * 75)
    print(doc)
