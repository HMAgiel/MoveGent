from chatbot.graph.state import SupervisorOutput, DataAgentOutput, AgentState
from chatbot.config import model_llm
from chatbot.prompt.supervisor import SUPERVISOR_PROMPT
from chatbot.prompt.agent_prompt import RAG_prompt, omdb_prompt, Data_prompt, agregasi_prompt, Basic_prompt, SQL_PROMPT, SQL_SCHEMA
from chatbot.tools.tool import RAG_tool, OMDB_tool, sql_tool
from chatbot.graph.routing import apply_guardrails
from chatbot.utils.sql_missing import detect_missing_sql
from chatbot.graph.tracing import llm_call

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig

NO_DATA_MARKER = "N/A"
NOT_USED_RAG = "Tidak pake RAG"
NOT_USED_SQL = "Tidak pake SQL"
NOT_USED_OMDB = "Tidak pake OMDB"


def supervisor_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    """Supervisor memutuskan worker mana yang menangani pesan user."""
    llm = model_llm(temperature=0.1)
    llm_supervisor = llm.with_structured_output(SupervisorOutput)
    last_message = state["messages"][-1].content
    decision = llm_call(
        llm_supervisor,
        [
            SystemMessage(SUPERVISOR_PROMPT),
            HumanMessage(f"last_message: {last_message}"),
        ],
        "Supervisor",
    )
    if decision and "next_worker" in decision:
        main_route = decision["next_worker"]
    else:
        main_route = "basic_agent"
    if isinstance(main_route, list):
        main_route = main_route[0]
    return {
        "next_worker": main_route,
        "SQL_result": "",
        "SQL_missing": "",
        "RAG_result": "",
        "OMDB_result": "",
    }


def Data_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    """Mengarahkan worker mana yang dipakai untuk pencarian data (SQL/RAG/OMDB)."""
    llm = model_llm(temperature=0.1)
    llm_data = llm.with_structured_output(DataAgentOutput)
    sql_results = state.get("SQL_result", "")
    omdb_results = state.get("OMDB_result", "")
    rag_results = state.get("RAG_result", "")
    question = state["messages"][-1].content
    history = state["history"]
    prompt = Data_prompt.format(
        RAG_result=rag_results,
        SQL_result=sql_results,
        OMDB_result=omdb_results,
    )
    result = llm_call(
        llm_data,
        [
            SystemMessage(prompt),
            HumanMessage(f"Query: {question} \n\n History Chat: {history}"),
        ],
        "Data_agent",
    )
    data_route = result.get("data_worker", "Agregasi_agent")
    butuh_rag = result.get("needs_overview", False)
    sql_missing = state.get("SQL_missing", "")
    data_route = apply_guardrails(
        data_route,
        sql_results=sql_results,
        omdb_results=omdb_results,
        rag_results=rag_results,
        butuh_rag=butuh_rag,
        sql_missing=sql_missing,
    )
    return {"data_worker": data_route}


def RAG_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    """Mengambil data dari vector database berdasarkan query user."""
    llm = model_llm()
    hasil_sql = state.get("SQL_result", "")
    question = state["messages"][-1].content
    history = state["history"]
    prompt = RAG_prompt.format(SQL_result=hasil_sql)
    response = llm_call(
        llm,
        [
            SystemMessage(prompt),
            HumanMessage(f"Query: {question} \n\n History: {history}"),
        ],
        "RAG_agnet",
    )
    if NO_DATA_MARKER in response.content:
        result = NOT_USED_RAG
    else:
        result = RAG_tool.invoke({"query": response.content})
    return {"RAG_result": result}


def SQL_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    """Mengambil data SQL sesuai query user."""
    llm = model_llm(temperature=0.1)
    question = state["messages"][-1].content
    history = state["history"]
    responses = llm_call(
        llm,
        [
            SystemMessage(content=f"{SQL_PROMPT} \n History: {history} \n SQL Schema; {SQL_SCHEMA}"),
            HumanMessage(content=question),
        ],
        "SQL_agent",
    )
    if NO_DATA_MARKER in responses.content:
        result = NOT_USED_SQL
        sql_missing = ""
    else:
        result = sql_tool.invoke({"query": responses.content})
        sql_missing = detect_missing_sql(result)
    return {"SQL_result": result, "SQL_missing": sql_missing}


def OMDB_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    """Mengambil data film dari OMDB server."""
    llm = model_llm()
    hasil_sql = state.get("SQL_result", "")
    question = state["messages"][-1].content
    history = state["history"]
    prompt = omdb_prompt
    response = llm_call(
        llm,
        [
            SystemMessage(prompt),
            HumanMessage(f"Query: {question} \n\n SQL history: {hasil_sql} \n\n Chat History: {history}"),
        ],
        "OMDB_agent",
    )
    if NO_DATA_MARKER in response.content:
        result = NOT_USED_OMDB
    else:
        clean_title = response.content.strip().strip('"').strip("'")
        result = OMDB_tool.invoke({"film_title": clean_title})
    return {"OMDB_result": result}


def Agregasi_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    """Menggabungkan output semua data agent menjadi jawaban final."""
    llm = model_llm()
    results = []
    if state.get("RAG_result"):
        results.append(f"RAG Result: {state["RAG_result"]}")
    if state.get("SQL_result"):
        results.append(f"SQL Result: {state["SQL_result"]}")
    if state.get("OMDB_result"):
        results.append(f"OMDB result: {state["OMDB_result"]}")
    combined = "\n\n".join(results) if results else "Tidak ada hasil dari worker"
    history = state["history"]
    original_query = state["messages"][-1].content
    result = llm_call(
        llm,
        [
            SystemMessage(agregasi_prompt),
            HumanMessage(f"Query: {original_query}\n\n History: {history}\n\n data: {combined}"),
        ],
        "Agregasi_agent",
    )
    final = result.content
    history_chat = f"User: {original_query} | AI: {final}"
    return {
        **state,
        "messages": [AIMessage(content=final)],
        "history": [history_chat],
        "final_result": final,
    }


def basic_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    """Node ini menjawab pertanyaan umum yang tidak masuk kategori produk atau promo."""
    llm = model_llm()
    question = state["messages"][-1].content
    prompt = Basic_prompt
    result = llm_call(
        llm,
        [
            SystemMessage(prompt),
            HumanMessage(f"Query: {question}"),
        ],
        "Basic_agent",
    )
    basic_results = result.content
    return {
        **state,
        "messages": [AIMessage(content=basic_results)],
        "final_result": basic_results,
    }
