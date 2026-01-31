"""Serve stored files (passport PDF, share image)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.storage import get_storage_path

router = APIRouter(prefix="/storage", tags=["storage"])


@router.get("/{path:path}")
def serve_file(path: str):
    try:
        full = get_storage_path(path)
        if not full.is_file():
            raise HTTPException(status_code=404, detail="File non trovato")
        return FileResponse(full, filename=full.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File non trovato")
