import logging
import json
from typing import Dict, Any, List
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("scraper_service")

BASE_URL = "https://corona.co"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    reraise=True
)
async def fetch_html(url: str, params: dict) -> str:
    """Fetches HTML with automatic retries on network blips or 5xx server errors."""
    async with httpx.AsyncClient(headers=HEADERS, timeout=12.0, follow_redirects=True) as client:
        logger.info(f"Fetching URL: {url} with params: {params}")
        response = await client.get(url, params=params)
        
        # Raise errors for 4xx or 5xx responses to trigger tenacity retries
        response.raise_for_status()
        return response.text

async def get_corona_catalog(query: str = "piso", page: int = 1) -> Dict[str, Any]:
    """Scrapes and parses SEO JSON-LD product data from Corona.co."""
    target_url = f"{BASE_URL}/search/{query}"
    
    # Most e-commerce stores use page or _page for pagination query params
    params = {"page": page} if page > 1 else {}

    try:
        html_content = await fetch_html(target_url, params)
    except Exception as e:
        logger.error(f"Failed to fetch data from Corona after retries: {str(e)}")
        raise RuntimeError(f"Upstream server unreachable: {str(e)}")

    soup = BeautifulSoup(html_content, "html.parser")
    jsonld_scripts = soup.find_all("script", type="application/ld+json")
    
    products: List[Dict[str, Any]] = []

    for index, script in enumerate(jsonld_scripts):
        if not script.string:
            continue
            
        try:
            data = json.loads(script.string)
            
            # Locate the ItemList schema
            if data.get("@type") == "WebPage" and "mainEntity" in data:
                item_list = data["mainEntity"].get("itemListElement", [])
                
                for list_item in item_list:
                    item = list_item.get("item", {})
                    if item.get("@type") == "Product":
                        offers = item.get("offers", {})
                        
                        relative_url = offers.get("url", "")
                        full_url = f"{BASE_URL}{relative_url}" if relative_url.startswith("/") else relative_url
                        
                        raw_avail = offers.get("availability", "")
                        in_stock = "InStock" in raw_avail

                        products.append({
                            "id": str(item.get("sku", "")),
                            "title": item.get("name", "Sin título"),
                            "brand": item.get("brand", {}).get("name", "Corona"),
                            "image_url": item.get("image", ""),
                            "url": full_url,
                            "price": float(offers.get("price", 0.0)),
                            "currency": offers.get("priceCurrency", "COP"),
                            "in_stock": in_stock,
                            "rating": float(item["aggregateRating"]["ratingValue"]) if "aggregateRating" in item else None,
                            "review_count": int(item["aggregateRating"]["reviewCount"]) if "aggregateRating" in item else 0
                        })
                logger.info(f"Successfully extracted {len(products)} products from script tag #{index}")
                break
                
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            logger.warning(f"Malformed JSON-LD in script tag #{index}: {str(e)}")
            continue

    return {
        "total_results": len(products),
        "products": products
    }
