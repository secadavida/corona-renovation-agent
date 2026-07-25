from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from cachetools import TTLCache
from .scraper import get_corona_catalog

app = FastAPI(
    title="Corona.co Catalog API",
    description="Polished, production-ready scraping API for Vite/Vanilla JS frontend.",
    version="2.0.0"
)

# 1. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        # Add production frontend URLs here later
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# 2. In-Memory Cache: Stores up to 200 unique searches for 15 minutes (900 seconds)
catalog_cache = TTLCache(maxsize=200, ttl=900)

# 3. Pydantic Models for Strict Data Contracts
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

# 4. API Routes
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
    
    # Check cache first
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

    # Fetch live data if not cached
    try:
        raw_result = await get_corona_catalog(query=q, page=page)
        products_list = raw_result.get("products", [])
        
        # Save to TTL cache
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
        # Triggered when tenacity exhausts all retries
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Target e-commerce server is unavailable or rate-limiting: {str(upstream_error)}"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the catalog data."
        )

@app.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
async def health_check():
    """Simple health check endpoint for uptime monitors."""
    return {"status": "online", "cache_size": len(catalog_cache)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
