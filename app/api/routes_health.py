from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
def root() -> dict[str, str]:
    """Human-friendly default route for platform checks and browser visits."""
    return {
        "status": "ok",
        "service": "ecoflow-sizing-v13",
        "health": "/health",
        "metadata": "/metadata",
        "analyze": "/analyze",
        "export_xlsx": "/export/xlsx",
        "docs": "/docs",
    }


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
