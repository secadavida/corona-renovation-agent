import json
from decimal import Decimal
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from backend.agent.llm_provider import LLMProvider
from backend.models.product import Product
from backend.services.scraper_service import fetch_product_details


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "analizarImagen",
            "description": "Analiza evidencia visible en una imagen de un espacio de renovacion.",
            "parameters": {
                "type": "object",
                "properties": {"image_url": {"type": "string", "description": "URL de la imagen"}},
                "required": ["image_url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "verProductos",
            "description": "Busca candidatos exclusivamente en el catalogo oficial Corona almacenado localmente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Termino libre de busqueda"},
                    "category": {"type": "string", "description": "Categoria solicitada"},
                    "style": {"type": "string", "description": "Estilo solicitado"},
                    "max_price": {"type": "number", "description": "Precio maximo en COP"},
                    "in_stock": {"type": "boolean", "description": "Requiere disponibilidad"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "verFichaTecnica",
            "description": "Obtiene la ficha tecnica oficial de un producto Corona por su id o URL.",
            "parameters": {
                "type": "object",
                "properties": {"product_id": {"type": "string", "description": "SKU o URL del producto"}},
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "estimarPresupuesto",
            "description": "Calcula el presupuesto usando precios oficiales almacenados para productos seleccionados.",
            "parameters": {
                "type": "object",
                "properties": {
                    "products": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string", "description": "SKU devuelto por verProductos"},
                                "quantity": {"type": "integer", "minimum": 1, "default": 1},
                            },
                            "required": ["product_id"],
                        },
                    }
                },
                "required": ["products"],
            },
        },
    },
]


async def execute_tool(
    name: str, arguments: dict[str, Any], db: Session, llm_provider: LLMProvider
) -> str:
    if name == "analizarImagen":
        return await _analyze_image(arguments["image_url"], llm_provider)
    if name == "verProductos":
        return _search_products(arguments, db)
    if name == "verFichaTecnica":
        return await _get_technical_sheet(arguments["product_id"], db)
    if name == "estimarPresupuesto":
        return _estimate_budget(arguments["products"], db)
    return json.dumps({"error": f"Herramienta no soportada: {name}"}, ensure_ascii=False)


async def _analyze_image(image_url: str, llm_provider: LLMProvider) -> str:
    prompt = """Analiza esta imagen de un espacio de renovacion. Retorna JSON valido con room, objects,
observations y unknown. Describe solo evidencia visible. No estimes dimensiones ni infieras plomeria
oculta o condiciones de instalacion. Explicita la incertidumbre."""
    return await llm_provider.vision(image_url, prompt)


def _search_products(filters: dict[str, Any], db: Session) -> str:
    statement: Select[tuple[Product]] = select(Product)
    for term in (filters.get("query"), filters.get("category"), filters.get("style")):
        if term:
            statement = statement.where(func.lower(Product.title).contains(str(term).lower()))
    if filters.get("max_price") is not None:
        statement = statement.where(Product.price <= Decimal(str(filters["max_price"])))
    if filters.get("in_stock") is True:
        statement = statement.where(Product.in_stock.is_(True))

    products = db.execute(statement.order_by(Product.in_stock.desc(), Product.price.asc()).limit(10)).scalars().all()
    return json.dumps(
        {
            "products": [
                {
                    "id": product.external_id,
                    "title": product.title,
                    "brand": product.brand,
                    "price": float(product.price),
                    "currency": product.currency,
                    "in_stock": product.in_stock,
                    "image_url": product.image_url,
                    "url": product.source_url,
                }
                for product in products
            ]
        },
        ensure_ascii=False,
    )


async def _get_technical_sheet(product_id: str, db: Session) -> str:
    product = db.execute(
        select(Product).where(or_(Product.external_id == product_id, Product.source_url == product_id))
    ).scalar_one_or_none()
    if product is None:
        return json.dumps({"error": "Producto no encontrado en el catalogo local."}, ensure_ascii=False)

    if not product.specifications:
        details = await fetch_product_details(product.source_url)
        product.description = details.get("description", "")
        product.specifications = details.get("specifications", {})
        product.attributes = details.get("attributes", [])
        product.advantages = details.get("advantages", [])
        product.price = Decimal(str(details.get("price", product.price)))
        product.currency = details.get("currency", product.currency)
        db.commit()

    return json.dumps(
        {
            "id": product.external_id,
            "title": product.title,
            "url": product.source_url,
            "description": product.description,
            "price": float(product.price),
            "currency": product.currency,
            "specifications": product.specifications,
            "attributes": product.attributes,
            "advantages": product.advantages,
        },
        ensure_ascii=False,
    )


def _estimate_budget(selected_products: list[dict[str, Any]], db: Session) -> str:
    product_ids = [item.get("product_id") for item in selected_products if item.get("product_id")]
    products = db.execute(select(Product).where(Product.external_id.in_(product_ids))).scalars().all()
    products_by_id = {product.external_id: product for product in products}
    breakdown = []
    missing_ids = []
    total = Decimal("0")

    for item in selected_products:
        product_id = item.get("product_id")
        quantity = item.get("quantity", 1)
        if not isinstance(quantity, int) or quantity < 1:
            return json.dumps({"error": "Cada cantidad debe ser un entero mayor o igual a uno."}, ensure_ascii=False)
        product = products_by_id.get(product_id)
        if product is None:
            missing_ids.append(product_id)
            continue
        subtotal = product.price * quantity
        total += subtotal
        breakdown.append(
            {
                "product_id": product.external_id,
                "title": product.title,
                "unit_price": float(product.price),
                "quantity": quantity,
                "subtotal": float(subtotal),
            }
        )

    if missing_ids:
        return json.dumps({"error": "Productos no encontrados.", "product_ids": missing_ids}, ensure_ascii=False)
    return json.dumps(
        {
            "products_subtotal": float(total),
            "total_estimate": float(total),
            "currency": "COP",
            "breakdown": breakdown,
            "note": "Incluye solo productos Corona seleccionados. No incluye mano de obra ni materiales no seleccionados.",
        },
        ensure_ascii=False,
    )
