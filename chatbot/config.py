import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from sqlalchemy import create_engine
from langchain_community.utilities.sql_database import SQLDatabase

from qdrant_client import QdrantClient

from sentence_transformers import CrossEncoder

from dotenv import load_dotenv

import subprocess

import os

load_dotenv()

url = os.getenv("QDRANT_URL")
qdrant_api = os.getenv("QDRANT_API")
url_omdb = os.getenv("OMDB_url")
api_omdb = os.getenv("OMDB_api_key")

data_base = create_engine(f"sqlite:////home/hasyim/movegent/chatbot/data/process/IMDB_FILM_capston3.db")
db = SQLDatabase(data_base)

def check_gpu():
    try:
        subprocess.check_output('nvidia-smi')
        return "cuda"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "cpu"
    
embedding = OpenAIEmbeddings(
    model='text-embedding-3-small',
)

def model_llm(temperature=0.7):
    llm = ChatOpenAI(model="gpt-5.6-luna", temperature=temperature)
    return llm

device_used=check_gpu()
rerank = CrossEncoder(
    "Qwen/Qwen3-Reranker-0.6B", 
    device=device_used, 
    cache_folder="chatbot/model",
)

retrive = QdrantVectorStore.from_existing_collection(
    embedding=embedding,
    path="/home/hasyim/movegent/chatbot/data/process/qdrant",
    collection_name="Data_IMDB"
)

