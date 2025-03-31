import orjson
import json


def sse_encode(content: dict):
    return f"data: {json.dumps(content)}\n\n"
