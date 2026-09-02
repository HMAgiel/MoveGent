from uuid import uuid4

from langchain_qdrant import QdrantVectorStore

from chatbot.config import QDRANT_PATH, get_embeddings
from chatbot.utils.data_cleaning import build_movies_documents, prepare_movies_dataframe


def make_vectore(path: str):
    """Membangun koleksi Qdrant 'Data_IMDB' dari CSV film."""
    df = prepare_movies_dataframe(path)
    documents = build_movies_documents(df)
    uuids = [str(uuid4()) for _ in range(len(documents))]

    qdrant = QdrantVectorStore.from_documents(
        documents,
        embedding=get_embeddings(),
        path=str(QDRANT_PATH),
        collection_name="Data_IMDB",
    )

    print("Create qdrant data sucesses ✅")
    return qdrant
