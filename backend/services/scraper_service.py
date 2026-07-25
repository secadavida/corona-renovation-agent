import logging
import json
import re
from typing import Dict, Any, List
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from backend.core.config import (
    CORONA_BASE_URL,
    HTTP_TIMEOUT_SECONDS,
    LOG_LEVEL,
    SCRAPER_MAX_RETRIES,
)

# Configuración de logs estructurados
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("scraper_service")

BASE_URL = CORONA_BASE_URL

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

@retry(
    stop=stop_after_attempt(SCRAPER_MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    reraise=True
)
async def fetch_html(url: str, params: dict = None) -> str:
    """Obtiene el HTML de una URL con reintentos automáticos ante fallos de red o errores 5xx."""
    async with httpx.AsyncClient(headers=HEADERS, timeout=HTTP_TIMEOUT_SECONDS, follow_redirects=True) as client:
        logger.info(f"Fetching URL: {url} con parámetros: {params}")
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.text


async def get_corona_catalog(query: str = "piso", page: int = 1) -> Dict[str, Any]:
    """Extrae y parsea los datos JSON-LD de los productos desde las búsquedas de Corona.co."""
    target_url = f"{BASE_URL}/search/{query}"
    params = {"page": page} if page > 1 else {}

    try:
        html_content = await fetch_html(target_url, params)
    except Exception as e:
        logger.error(f"Error al obtener datos de Corona tras reintentos: {str(e)}")
        raise RuntimeError(f"Servidor upstream inalcanzable: {str(e)}")

    soup = BeautifulSoup(html_content, "html.parser")
    jsonld_scripts = soup.find_all("script", type="application/ld+json")
    
    products: List[Dict[str, Any]] = []

    for index, script in enumerate(jsonld_scripts):
        if not script.string:
            continue
            
        try:
            data = json.loads(script.string)
            
            # Localizar el esquema ItemList
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
                logger.info(f"Se extrajeron exitosamente {len(products)} productos del tag script #{index}")
                break
                
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            logger.warning(f"JSON-LD malformado en tag script #{index}: {str(e)}")
            continue

    return {
        "total_results": len(products),
        "products": products
    }


@retry(
    stop=stop_after_attempt(SCRAPER_MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    reraise=True
)
async def fetch_product_details(product_url: str) -> Dict[str, Any]:
    """
    Extrae especificaciones técnicas, atributos, ventajas y precios de la página
    de detalle del producto (PDP) en Corona.co.
    """
    # Sanitizar URL para asegurar que sea absoluta
    if not product_url.startswith("http"):
        product_url = f"{BASE_URL}{product_url}" if product_url.startswith("/") else f"{BASE_URL}/{product_url}"

    async with httpx.AsyncClient(headers=HEADERS, timeout=HTTP_TIMEOUT_SECONDS, follow_redirects=True) as client:
        logger.info(f"Fetching página de detalle: {product_url}")
        response = await client.get(product_url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # 1. Datos base del producto vía JSON-LD
    product_data: Dict[str, Any] = {
        "url": product_url,
        "sku": "",
        "title": "",
        "description": "",
        "price": 0.0,
        "currency": "COP",
        "specifications": {},
        "attributes": [],
        "advantages": []
    }

    for script in soup.find_all("script", type="application/ld+json"):
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
            if data.get("@type") == "Product":
                product_data["sku"] = str(data.get("sku", ""))
                product_data["title"] = data.get("name", "")
                product_data["description"] = data.get("description", "")
                
                offers = data.get("offers", {})
                if isinstance(offers, list) and offers:
                    offers = offers[0]
                
                product_data["price"] = float(offers.get("price", 0.0))
                product_data["currency"] = offers.get("priceCurrency", "COP")
                break
        except (json.JSONDecodeError, ValueError, TypeError):
            continue

    # Título alternativo si el JSON-LD no estaba presente
    if not product_data["title"]:
        h1 = soup.find("h1")
        if h1:
            product_data["title"] = h1.get_text(strip=True)

    # 2. Extraer tabla de especificaciones
    spec_table = soup.find("table") or soup.find("div", class_=re.compile(r"spec|atributo", re.I))
    if spec_table:
        for row in spec_table.find_all(["tr", "li"]):
            cols = row.find_all(["td", "th", "span"])
            if len(cols) >= 2:
                key = cols[0].get_text(strip=True)
                val = cols[1].get_text(strip=True)
                if key and val and key.lower() != "característica":
                    product_data["specifications"][key] = val

    # Extracción de especificaciones de respaldo (listas de descripción dt/dd)
    if not product_data["specifications"]:
        for dl in soup.find_all("dl"):
            dts = dl.find_all("dt")
            dds = dl.find_all("dd")
            for dt, dd in zip(dts, dds):
                product_data["specifications"][dt.get_text(strip=True)] = dd.get_text(strip=True)

    # 3. Extraer "Atributos Especiales" y "Ventajas"
    for section in soup.find_all(["div", "section"]):
        header = section.find(["h2", "h3", "h4", "strong", "span"])
        if not header:
            continue
        
        header_text = header.get_text(strip=True).lower()
        if "atributo" in header_text:
            items = [li.get_text(strip=True) for li in section.find_all("li") if li.get_text(strip=True)]
            if items:
                product_data["attributes"] = items
        elif "ventaja" in header_text:
            items = [li.get_text(strip=True) for li in section.find_all("li") if li.get_text(strip=True)]
            if items:
                product_data["advantages"] = items

    return product_data
