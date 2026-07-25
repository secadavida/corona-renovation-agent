from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from cachetools import TTLCache
from .scraper import get_corona_catalog, fetch_product_details

app = FastAPI(
    title="Corona.co Catalog API",
    description="Polished, production-ready scraping API for Vite/Vanilla JS frontend.",
    version="2.0.0"
)

# 1. Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        # Añadir URLs del frontend de producción aquí más adelante
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# 2. Caché en Memoria (TTL): Guarda hasta 200 búsquedas durante 15 minutos (900 segundos)
catalog_cache = TTLCache(maxsize=200, ttl=900)

# 3. Modelos Pydantic para la Validación de Datos
class ProductModel(BaseModel):
    id: str = Field(..., description="Product SKU")
    title: str = Field(..., description="Display name of the product")
    brand: str = Field(default="Corona")
    image_url: str = Field(default="", description="Absolute URL to product image")
    url: str = Field(..., description="Absolute URL to the store product page")
    price: float = Field(..., ge=0, description="Price in local currency")
    currency: str = Field(default="COP")
    in_stock: bool
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    review_count: int = Field(default=0, ge=0)

class CatalogResponseModel(BaseModel):
    status: str
    cached: bool
    query: str
    page: int
    total_results: int
    data: List[ProductModel]

class ProductDetailResponse(BaseModel):
    url: str
    sku: Optional[str] = ""
    title: str
    description: Optional[str] = ""
    price: float
    currency: str = "COP"
    specifications: Dict[str, str] = Field(
        default_factory=dict,
        description="Diccionario con las especificaciones técnicas (ej: Materiales, Formato, M2 por caja)"
    )
    attributes: List[str] = Field(default_factory=list, description="Atributos especiales")
    advantages: List[str] = Field(default_factory=list, description="Ventajas del producto")


# 4. Rutas de la API
@app.get(
    "/api/catalog",
    response_model=CatalogResponseModel,
    status_code=status.HTTP_200_OK,
    summary="Search Corona.co Catalog",
    description="Returns structured, scraped product data with pagination and caching support."
)
async def fetch_catalog_endpoint(
    q: str = Query("piso", min_length=2, max_length=50, description="Search term"),
    page: int = Query(1, ge=1, le=20, description="Page number for pagination")
):
    cache_key = f"{q.lower().strip()}_page_{page}"
    
    # Revisar caché primero
    if cache_key in catalog_cache:
        cached_data = catalog_cache[cache_key]
        return {
            "status": "success",
            "cached": True,
            "query": q,
            "page": page,
            "total_results": len(cached_data),
            "data": cached_data
        }

    # Obtener datos en vivo si no están en caché
    try:
        raw_result = await get_corona_catalog(query=q, page=page)
        products_list = raw_result.get("products", [])
        
        # Guardar en caché TTL
        catalog_cache[cache_key] = products_list
        
        return {
            "status": "success",
            "cached": False,
            "query": q,
            "page": page,
            "total_results": len(products_list),
            "data": products_list
        }
    except RuntimeError as upstream_error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Target e-commerce server is unavailable or rate-limiting: {str(upstream_error)}"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the catalog data."
        )

@app.get(
    "/api/product",
    response_model=ProductDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle y especificaciones de un producto",
    description="Extrae las especificaciones técnicas, ventajas y atributos de la página de detalle de Corona."
)
async def get_product_specifications(
    url: str = Query(
        ...,
        description="URL completa o ruta relativa del producto (ej: /productos/revestimientos/pisos/piso-bhukhara-60x120/p/18193586)"
    )
):
    try:
        details = await fetch_product_details(product_url=url)
        return details
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error obteniendo especificaciones del producto: {str(e)}"
        )

@app.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
async def health_check():
    """Simple health check endpoint for uptime monitors."""
    return {"status": "online", "cache_size": len(catalog_cache)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
