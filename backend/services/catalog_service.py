from cachetools import TTLCache
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.services.scraper_service import fetch_product_details, get_corona_catalog
from backend.services.product_service import ProductService


class CatalogService:
    """Coordinates catalog retrieval and its short-lived cache."""

    def __init__(self) -> None:
        self.cache: TTLCache[str, list[dict]] = TTLCache(maxsize=200, ttl=900)
        self.product_service = ProductService()

    async def search(self, query: str, page: int) -> tuple[list[dict], bool]:
        cache_key = f"{query.lower().strip()}_page_{page}"
        if cache_key in self.cache:
            return self.cache[cache_key], True

        result = await get_corona_catalog(query=query, page=page)
        products = result["products"]
        self.cache[cache_key] = products
        return products, False

    async def get_details(self, product_url: str) -> dict:
        return await fetch_product_details(product_url)

    async def import_all_pages(self, db: Session, query: str, max_pages: int) -> dict:
        """Persist each available Corona catalog page for a search query."""
        created = updated = skipped = pages_imported = 0
        seen_product_ids: set[str] = set()

        for page in range(1, max_pages + 1):
            result = await get_corona_catalog(query=query, page=page)
            products = result["products"]
            if not products:
                return self._import_result(query, pages_imported, created, updated, skipped, "no_products")

            page_ids = {
                str(product.get("id") or product.get("url"))
                for product in products
                if product.get("id") or product.get("url")
            }
            if not page_ids:
                return self._import_result(
                    query, pages_imported, created, updated, skipped + len(products), "no_valid_products"
                )
            if page_ids.issubset(seen_product_ids):
                return self._import_result(query, pages_imported, created, updated, skipped, "repeated_page")

            try:
                for product_data in products:
                    if not product_data.get("id") or not product_data.get("url"):
                        skipped += 1
                        continue

                    _, was_created = self.product_service.upsert_from_catalog(db, product_data)
                    created += was_created
                    updated += not was_created

                db.commit()
            except SQLAlchemyError:
                db.rollback()
                raise

            pages_imported += 1
            seen_product_ids.update(page_ids)

        return self._import_result(query, pages_imported, created, updated, skipped, "max_pages_reached")

    @staticmethod
    def _import_result(
        query: str,
        pages_imported: int,
        created: int,
        updated: int,
        skipped: int,
        stopped_reason: str,
    ) -> dict:
        return {
            "query": query,
            "pages_imported": pages_imported,
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "stopped_reason": stopped_reason,
        }
