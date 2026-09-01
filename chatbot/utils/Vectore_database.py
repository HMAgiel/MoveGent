import pandas as pd
from uuid import uuid4
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from chatbot.config import embedding
import os

def make_vectore(path):
    try:
        
        df = pd.read_csv(path)

        df=df.replace({'Released_Year': 'PG'}, None)

        df['Gross'] = df['Gross'].str.replace(',', '', regex=True)

        df[['Released_Year','Gross']] = df[['Released_Year','Gross']].apply(pd.to_numeric)

        df['film_id'] = [str(uuid4()) for _ in range(len(df['Series_Title']))]
        
        documents = []

        for i in range(len(df)):
            judul_film = df['Series_Title'][i]
            overview_film = df['Overview'][i]
            id_film = df['film_id'][i]
            input_rag = f"Series_Title: {judul_film}, Overview: {overview_film}"
            doc = Document(
                page_content=input_rag,
                metadata={
                    "film_id": id_film,
                    "Series_Title": judul_film
                },
            )
            documents.append(doc)

        uuids = [str(uuid4()) for _ in range(len(documents))]

        qdrant = QdrantVectorStore.from_documents(
            documents,
            embedding=embedding,
            path="/home/hasyim/movegent/chatbot/data/process/qdrant",
            collection_name="Data_IMDB",
        )
        
        return print("Create qdrant data sucesses ✅")
    
    except Exception as e:
        print(e)