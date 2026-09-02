from langchain_core.tools import tool
from sqlalchemy import text
from chatbot.config import retrive, rerank, api_omdb, url_omdb, db
from chatbot.tools.markdown import format_rows_to_markdown
import requests


@tool
def RAG_tool(query: str) -> str:
    """This tools is used to call data from Qdrant based on user query"""
    retrive_rag = retrive
    rerank_model = rerank
    results = retrive_rag.similarity_search(query=query)
    hasil_rag = [result.page_content for result in results]
    reranking = rerank_model.rank(
    query, 
    hasil_rag,
    return_documents=True, 
    top_k=3
    )
    context_list = [item['text'] for item in reranking]
    return context_list
    
tool_rag = [RAG_tool]

@tool
def sql_tool(query: str) -> str:
    """This tools is used to execute sql query"""
    with db.connect() as conn:
        
        result = conn.execute(text(query))

        if not result.returns_rows:
            return f"Query executed successfully. Rows affected: {result.rowcount}"

        columns = list(result.keys())
        rows = result.fetchall()

    if not columns:
        return "No results returned."

    return format_rows_to_markdown(columns, rows)

tool_sql = [sql_tool]
    

@tool
def OMDB_tool(film_title: str) -> str:
    """"This tool for calling OMDB data when data from other source is null, none or NaN.
    Input FILM_title in specific """
    

    if not url_omdb or not api_omdb:
        return "OMDb tidak dikonfigurasi. Lewati pencarian OMDB."

    params = {
        "apikey": api_omdb,
        "t": film_title
    }

    response = requests.get(url_omdb, params=params)
    
    # Jangan langsung response.json()! Lakukan pengecekan:
    if response.status_code != 200:
        return f"Error: OMDb API mengembalikan status {response.status_code}."
        
    try:
        data = response.json()
        
        # Cek apakah OMDb merespon dengan 'Response': 'False' (Film tidak ditemukan)
        if data.get("Response") == "False":
            return f"OMDb tidak dapat menemukan film tersebut. Error: {data.get('Error')}"
            
        return data
        
    except ValueError: # Menangkap JSONDecodeError jika bukan JSON
        return f"Error: OMDb merespon dengan format yang salah (bukan JSON). Response text: {response.text[:100]}"
tool_omdb = [OMDB_tool]