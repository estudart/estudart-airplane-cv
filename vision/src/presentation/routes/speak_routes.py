from fastapi import APIRouter, Response, HTTPException

from src.dependencies import get_speak_service

speak_router = APIRouter(prefix="/api", tags=["speak"])


@speak_router.post("/speak")
async def speak(text: str):
    speak_service = get_speak_service()
    try:
        speak_service.speak(text=text)
        return Response(
            content="Text spoken!",
            status_code=200,
        )
    except Exception as err:
        raise HTTPException(
            detail=f"Could not speak text, reason: {err}",
            status_code=400,
        )
