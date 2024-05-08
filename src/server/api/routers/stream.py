from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from server.chat_models.azure_openai import completion

chat_router = APIRouter(prefix="/sse", tags=["流式接口"])


@chat_router.get("/es")
async def event_stream(prompt: str):
    headers = {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-cache",
    }
    return StreamingResponse(
        completion(
            [
                HumanMessage(content=prompt),
            ]
        ),
        headers=headers,
    )
