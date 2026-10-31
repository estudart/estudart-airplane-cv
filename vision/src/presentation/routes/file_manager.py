from fastapi import APIRouter, Response, HTTPException

from src.dependencies import get_file_manager_service

file_manager_router = APIRouter(prefix="api/file_manager", tags=["File Manager"])


@file_manager_router.get("/get-file")
async def get_file(file_path: str):
    try:
        service = get_file_manager_service()
        file = service.get_frame(file_path)
        return Response(
            content=file,
            media_type="image/png",
            status_code=200
        )
    except Exception as err:
        return HTTPException(
            status_code=400,
            detail=str(err)
        )
