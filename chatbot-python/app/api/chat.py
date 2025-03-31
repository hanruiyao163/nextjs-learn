from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ..llm.generate import generate_response

router = APIRouter()

@router.get("/chat")
async def chat():
    return StreamingResponse(generate_response("你好"), media_type="text/event-stream")