from .simple_graph import graph, model
from langchain_core.callbacks import UsageMetadataCallbackHandler
import uuid
from ..utils.response_utils import sse_encode


def generate_response(message):
    usage_callback = UsageMetadataCallbackHandler()
    reasoning_flag = False
    text_flag = False
    for message, metadata in graph.stream(
        {"messages": [{"role": "user", "content": message}]},
        stream_mode="messages",
        config={"callbacks": [usage_callback]},
    ):

        if metadata["langgraph_node"] == "chatbot":
            if "reasoning_content" in message.additional_kwargs:
                if not reasoning_flag:
                    reasoning_flag = True
                    yield "event: response_type\n"
                    yield "data: reasoning_text\n\n"
                
                yield sse_encode(
                    {
                        "type": "reasoning_text",
                        "content": message.additional_kwargs["reasoning_content"],
                    }
                )
            else:
                if not text_flag:
                    text_flag = True
                    yield "event: response_type\n"
                    yield "data: text\n\n"
                yield sse_encode(
                    {
                        "type": "text",
                        "content": message.content,
                    }
                )

    yield sse_encode(
        {
            "type": "meta",
            "content": {
                "total_tokens": usage_callback.usage_metadata[model]["total_tokens"],
                "id": str(uuid.uuid4()),
            },
            "finish_reason": "done",
        }
    )
