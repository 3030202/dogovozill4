"""FastAPI REST Server for DocGen Platform."""

from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from adapters.api.routes.contracts import router as contracts_router
from adapters.api.routes.drafts import router as drafts_router

app = FastAPI(
    title="DocGen Omnichannel API",
    description="Deterministic Zero-LLM Document Generation Platform for Russian Civil Law Contracts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for Web SPA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(contracts_router)
app.include_router(drafts_router)

# Mount web_ui dist if built
WEB_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "../web_ui/dist"))
if os.path.exists(WEB_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(WEB_DIST, "assets")), name="assets")

    @app.get("/")
    def serve_spa():
        return FileResponse(os.path.join(WEB_DIST, "index.html"))


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "engine": "Deterministic Zero-LLM Core",
        "version": "1.0.0"
    }


def start():
    """CLI launcher for uvicorn server."""
    import uvicorn
    uvicorn.run("adapters.api.server:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
