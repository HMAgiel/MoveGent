"""Helper tracing langfuse untuk agent nodes."""
from langfuse import get_client
from langfuse.langchain import CallbackHandler

langfuse = get_client()


def llm_call(llm, messages: list, span_name: str):
    """Jalankan invoke LLM di dalam span langfuse + CallbackHandler."""
    handler = CallbackHandler()
    with langfuse.start_as_current_observation(name=span_name, as_type="span"):
        return llm.invoke(messages, config={"callbacks": [handler]})
