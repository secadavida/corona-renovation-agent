from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes.agent import router as agent_router
from backend.api.routes.catalog import catalog_service, router as catalog_router
from backend.core.config import APP_HOST, APP_PORT, CORS_ORIGINS

app = FastAPI(
    title="Corona.co Catalog API",
    description="API de catálogo Corona preparada para persistencia en PostgreSQL.",
    version="3.0.0",
)

# 1. Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

app.include_router(catalog_router)
app.include_router(agent_router)

@app.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
async def health_check():
    """Simple health check endpoint for uptime monitors."""
    return {"status": "online", "cache_size": len(catalog_service.cache)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host=APP_HOST, port=APP_PORT, reload=True)
