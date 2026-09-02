from chatbot.graph.state import SupervisorOutput, DataAgentOutput, AgentState

from chatbot.config import model_llm

from chatbot.prompt.supervisor import SUPERVISOR_PROMPT
from chatbot.prompt.agent_prompt import RAG_prompt, omdb_prompt, Data_prompt, agregasi_prompt, Basic_prompt, SQL_PROMPT, SQL_SCHEMA

from chatbot.tools.tool import RAG_tool, OMDB_tool, sql_tool

from chatbot.graph.routing import apply_guardrails
from chatbot.utils.sql_missing import detect_missing_sql

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_core.runnables import RunnableConfig


from langfuse import get_client, propagate_attributes
from langfuse.langchain import CallbackHandler
from dotenv import load_dotenv

load_dotenv()
langfuse = get_client()

def supervisor_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    llm = model_llm(temperature=0.1)
    llm_supervisor = llm.with_structured_output(SupervisorOutput)
    
    session_id = config.get("configurable", {}).get("session_id", "default")
    with langfuse.start_as_current_observation(
        name="Supervisor",
        as_type="span",
    ):
        handler = CallbackHandler()
        
        last_message = state["messages"][-1].content
        
        decision = llm_supervisor.invoke(
            [
                SystemMessage(SUPERVISOR_PROMPT),
                HumanMessage(f"last_message: {last_message}"),
            ],
            config = {
                "callbacks": [handler]
            },
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
            "OMDB_result": ""
        }       

def Data_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    llm = model_llm(temperature=0.1)
    llm_data = llm.with_structured_output(DataAgentOutput)
    session_id = config.get("configurable", {}).get("session_id", "default")
    
    with langfuse.start_as_current_observation(
        name="Data_agent",
        as_type="span",
    ):
        handler = CallbackHandler()
        """
        This agnet is used to sort what agent used for the data search
        """
        sql_results = state.get("SQL_result", "")
        omdb_results = state.get("OMDB_result", "")
        rag_results = state.get("RAG_result", "")
        question = state["messages"][-1].content
        history  = state["history"]
        
        prompt = Data_prompt.format(
            RAG_result=rag_results,
            SQL_result=sql_results,
            OMDB_result=omdb_results
        )
        
        result = llm_data.invoke(
            [
                SystemMessage(prompt),
                HumanMessage(f"Query: {question} \n\n History Chat: {history}")
            ],
            config={
                "callbacks": [handler],
            },
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

        return {
            "data_worker": data_route
        }
        
def RAG_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    llm = model_llm()
    session_id = config.get("configurable", {}).get("session_id", "default")
    with langfuse.start_as_current_observation(
        name="RAG_agnet",
        as_type="span"
    ):
        handler = CallbackHandler()
        """
        This node used to retrive data from vectore databse based on user query
        """
        hasil_sql = state.get("SQL_result", "")
        question = state["messages"][-1].content
        history = state["history"]
        
        prompt = RAG_prompt.format(
            SQL_result=hasil_sql

        )
        
        response = llm.invoke(
            [
                SystemMessage(prompt),
                HumanMessage(f"Query: {question} \n\n History: {history}"),
            ],
            config={
                "callbacks": [handler],
            },
        )
        
        if "N/A" in response.content:
            result = "Tidak pake RAG"
        else:
            result = RAG_tool.invoke({"query": response.content})
            
        return {
            "RAG_result": result
        }
        
def SQL_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    llm = model_llm(temperature=0.1)
    session_id = config.get("configurable", {}).get("session_id", "default")

    with langfuse.start_as_current_observation(name="SQL_agent", as_type="span"):
        handler = CallbackHandler()

        question = state["messages"][-1].content
        history = state["history"]
        
        responses = llm.invoke(
            [
                SystemMessage(content=f"{SQL_PROMPT} \n History: {history} \n SQL Schema; {SQL_SCHEMA}"),
                HumanMessage(content=question)
            ],
            config={
                    "callbacks": [handler],
                    },
        )
        
        if "N/A" in responses.content:
            result = "Tidak pake SQL"
            sql_missing = ""
        else:
            result = sql_tool.invoke({"query": responses.content})
            sql_missing = detect_missing_sql(result)
            
        return {
            "SQL_result": result,
            "SQL_missing": sql_missing
        }

        
        
def OMDB_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    llm = model_llm()
    session_id = config.get("configurable",{}).get("session_id", "default")
    with langfuse.start_as_current_observation(
        name="OMDB_agent",
        as_type="span"
    ):
        handler = CallbackHandler()
        """
        This node used to get data from OMDB server
        """
        hasil_sql = state.get("SQL_result", "")
        question = state["messages"][-1].content
        history = state["history"]
        
        prompt = omdb_prompt
        
        response = llm.invoke(
            [
                SystemMessage(prompt),
                HumanMessage(f"Query: {question} \n\n SQL history: {hasil_sql} \n\n Chat History: {history}"),
            ],
            config={
                "callbacks": [handler],
            },
        )
        
        if "N/A" in response.content:
            result = "Tidak pake OMDB"
        else:
            clean_title = response.content.strip().strip('"').strip("'")
            result = OMDB_tool.invoke({"film_title": clean_title})
            
        return {
            "OMDB_result": result
        }
        
        
def Agregasi_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    llm = model_llm()
    session_id = config.get("configurable",{}).get("session_id", "default")
    with langfuse.start_as_current_observation(
        name="Agregasi_agent",
        as_type="span"
    ):
        handler=CallbackHandler()
        """
        This node is for agregation of all the data agent output
        """
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
        
        result = llm.invoke(
            [
                SystemMessage(agregasi_prompt),
                HumanMessage(f"Query: {original_query}\n\n History: {history}\n\n data: {combined}")
            ],
            config={
                "callbacks": [handler],
            },
        )
        
        final = result.content
        history_chat = f"User: {original_query} | AI: {final}"
        return {
            **state,
            "messages": [AIMessage(content=final)],
            "history": [history_chat],
            "final_result": final,
        }
        
def basic_agent(state: AgentState, config: RunnableConfig)-> AgentState:
    llm=model_llm()
    session_id = config.get("configurable", {}).get("session_id", "default")
    with langfuse.start_as_current_observation(
        name="Basic_agent",
        as_type="span"
    ):

        handler = CallbackHandler()
        """
        Node ini menjawab pertanyaan umum yang tidak masuk kategori
        produk atau promo.
        """
        question = state["messages"][-1].content

        prompt = Basic_prompt
        result = llm.invoke(
            [
                SystemMessage(prompt),
                HumanMessage(f"Query: {question}"),
            ],
            config={
                "callbacks": [handler],
            },
        )
        basic_results = result.content
        return {
            **state,
            "messages": [AIMessage(content=basic_results)],
            "final_result": basic_results,
        }