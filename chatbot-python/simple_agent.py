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

llm = ChatDeepSeek(model=model, api_key=api_key, api_base=base_url)


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


graph_builder.add_node(chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()


if __name__ == "__main__":
    print(model, api_key, base_url)
    messages = [
        {"role": "system", "content": "You are an assistant."},
        {"role": "user", "content": "0.11和0.8哪个大？"},
    ]
    response = llm.invoke(messages)

    print(response.additional_kwargs.get("reasoning_content", ""))

