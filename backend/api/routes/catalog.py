from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.product import CatalogImportResponse, CatalogResponse, ProductDetail
from backend.services.catalog_service import CatalogService


router = APIRouter(prefix="/api", tags=["Catalog"])
catalog_service = CatalogService()


@router.get("/catalog", response_model=CatalogResponse, status_code=status.HTTP_200_OK)
async def fetch_catalog(
    q: str = Query("piso", min_length=2, max_length=50, description="Search term"),
    page: int = Query(1, ge=1, le=20, description="Page number for pagination"),
) -> dict:
    try:
        products, cached = await catalog_service.search(q, page)
        return {
            "status": "success",
            "cached": cached,
            "query": q,
            "page": page,
            "total_results": len(products),
            "data": products,
        }
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Target e-commerce server is unavailable or rate-limiting: {error}",
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the catalog data.",
        ) from error


@router.get("/product", response_model=ProductDetail, status_code=status.HTTP_200_OK)
async def get_product_specifications(
    url: str = Query(..., description="URL completa o ruta relativa del producto"),
) -> dict:
    try:
        return await catalog_service.get_details(url)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error obteniendo especificaciones del producto: {error}",
        ) from error


@router.post("/catalog/import", response_model=CatalogImportResponse, status_code=status.HTTP_200_OK)
async def import_catalog(
    q: str = Query("piso", min_length=2, max_length=50, description="Termino de busqueda a sincronizar"),
    max_pages: int = Query(100, ge=1, le=500, description="Limite de seguridad de paginas a recorrer"),
    db: Session = Depends(get_db),
) -> dict:
    """Scrape and persist every available catalog page for a search query."""
    try:
        return await catalog_service.import_all_pages(db, q, max_pages)
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"No fue posible consultar el catalogo de Corona: {error}",
        ) from error
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No fue posible guardar los productos en PostgreSQL.",
        ) from error
