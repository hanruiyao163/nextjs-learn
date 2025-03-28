import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()
model = os.getenv("MODEL")
api_key = os.getenv("ARK_API_KEY")
base_url = os.getenv("BASE_URL")


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

llm = ChatDeepSeek(model=model, api_key=api_key, api_base=base_url, stream_usage=True)


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# graph2 = (
#     graph_builder
#         .add_node('c1',chatbot)
#         .add_node('c2',chatbot)
#         .add_edge(START, "c1")
#         .add_edge('c1', "c2")
#         .add_edge("c2", END)
#         .compile()
# )


graph = (
    graph_builder
        .add_node(chatbot)
        .add_edge(START, "chatbot")
        .add_edge("chatbot", END)
        .compile()
)


if __name__ == "__main__":
    print(model, api_key, base_url)
    messages = [
        {"role": "system", "content": "You are an assistant."},
        {"role": "user", "content": "0.11和0.8哪个大？"},
    ]
    response = llm.invoke(messages)

    print(response.additional_kwargs.get("reasoning_content", ""))
    from langchain_core.callbacks import UsageMetadataCallbackHandler