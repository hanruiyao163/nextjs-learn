import orjson
import json


def sse_encode(content: dict):
    return f"data: {orjson.dumps(content).decode('utf-8')}\n\n"
