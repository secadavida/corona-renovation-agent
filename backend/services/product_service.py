from typing import Any

from sqlalchemy.orm import Session

from backend.models.product import Product


class ProductService:
    """Encapsulates product persistence independently from HTTP routes."""

    def upsert_from_catalog(self, db: Session, data: dict[str, Any]) -> tuple[Product, bool]:
        """Create or update a product identified by the source SKU."""
        product = db.query(Product).filter_by(external_id=data["id"]).one_or_none()
        created = product is None
        if created:
            product = Product(
                external_id=data["id"],
                title=data["title"],
                source_url=data["url"],
                price=data["price"],
                in_stock=data["in_stock"],
            )
            db.add(product)

        product.title = data["title"]
        product.brand = data.get("brand", "Corona")
        product.image_url = data.get("image_url", "")
        product.source_url = data["url"]
        product.price = data["price"]
        product.currency = data.get("currency", "COP")
        product.in_stock = data["in_stock"]
        product.rating = data.get("rating")
        product.review_count = data.get("review_count", 0)
        db.flush()
        return product, created
