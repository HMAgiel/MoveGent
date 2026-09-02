import os
import subprocess
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from sentence_transformers import CrossEncoder
from sqlalchemy import create_engine

load_dotenv()

# Path relatif ke package — menunjuk lokasi yang sama dengan path hardcoded lama
PACKAGE_DIR = Path(__file__).resolve().parent          # .../chatbot/
PROCESS_DIR = PACKAGE_DIR / "data" / "process"
DATABASE_PATH = PROCESS_DIR / "IMDB_FILM_capston3.db"
QDRANT_PATH = PROCESS_DIR / "qdrant"
MODEL_DIR = PACKAGE_DIR / "model"

# String model PERSIS sama dengan sebelumnya
LLM_MODEL = "gpt-5.6-luna"

# Env string murah, tidak perlu lazy
api_omdb = os.getenv("OMDB_api_key")
url_omdb = os.getenv("OMDB_url")


def check_gpu():
    try:
        subprocess.check_output('nvidia-smi')
        return "cuda"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "cpu"


@lru_cache(maxsize=1)
def get_embeddings():
    return OpenAIEmbeddings(model="text-embedding-3-small")


@lru_cache(maxsize=1)
def get_rerank():
    return CrossEncoder(
        "Qwen/Qwen3-Reranker-0.6B",
        device=check_gpu(),
        cache_folder=str(MODEL_DIR),
    )


@lru_cache(maxsize=1)
def get_retrive():
    return QdrantVectorStore.from_existing_collection(
        embedding=get_embeddings(),
        path=str(QDRANT_PATH),
        collection_name="Data_IMDB",
    )


@lru_cache(maxsize=1)
def get_db():
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    return engine.execution_options(read_only=True)


@lru_cache(maxsize=8)
def model_llm(temperature: float = 0.7):
    return ChatOpenAI(model=LLM_MODEL, temperature=temperature)


# Nama publik lama tetap bisa di-import, resource hanya dibuat saat pertama diakses
_LAZY = {"embedding": get_embeddings, "rerank": get_rerank, "retrive": get_retrive, "db": get_db}


def __getattr__(name: str):
    if name in _LAZY:
        return _LAZY[name]()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
