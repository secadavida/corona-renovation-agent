from cachetools import TTLCache

from backend.services.scraper_service import fetch_product_details, get_corona_catalog


class CatalogService:
    """Coordinates catalog retrieval and its short-lived cache."""

    def __init__(self) -> None:
        self.cache: TTLCache[str, list[dict]] = TTLCache(maxsize=200, ttl=900)

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
