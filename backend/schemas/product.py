from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductSummary(BaseModel):
    """Product data returned by catalog searches."""

    model_config = ConfigDict(from_attributes=True)

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


class CatalogResponse(BaseModel):
    status: str
    cached: bool
    query: str
    page: int
    total_results: int
    data: list[ProductSummary]


class ProductDetail(BaseModel):
    url: str
    sku: Optional[str] = ""
    title: str
    description: Optional[str] = ""
    price: float
    currency: str = "COP"
    specifications: dict[str, str] = Field(default_factory=dict)
    attributes: list[str] = Field(default_factory=list)
    advantages: list[str] = Field(default_factory=list)


class CatalogImportResponse(BaseModel):
    query: str
    pages_imported: int
    created: int
    updated: int
    skipped: int
    stopped_reason: str
