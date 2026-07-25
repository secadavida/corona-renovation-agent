import unittest
from unittest.mock import AsyncMock, patch

from backend.services.catalog_service import CatalogService


class FakeQuery:
    def __init__(self, database: "FakeDatabase") -> None:
        self.database = database
        self.external_id = ""

    def filter_by(self, **kwargs: str) -> "FakeQuery":
        self.external_id = kwargs["external_id"]
        return self

    def one_or_none(self):
        return self.database.products.get(self.external_id)


class FakeDatabase:
    def __init__(self) -> None:
        self.products: dict[str, object] = {}
        self.commits = 0

    def query(self, _model: object) -> FakeQuery:
        return FakeQuery(self)

    def add(self, product: object) -> None:
        self.products[product.external_id] = product

    def flush(self) -> None:
        pass

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        raise AssertionError("No rollback expected")


class CatalogImportTests(unittest.IsolatedAsyncioTestCase):
    async def test_stops_when_corona_repeats_a_page(self) -> None:
        product = {
            "id": "sku-1",
            "title": "Producto",
            "url": "https://corona.co/p/sku-1",
            "price": 10.0,
            "in_stock": True,
        }
        database = FakeDatabase()

        with patch(
            "backend.services.catalog_service.get_corona_catalog",
            new=AsyncMock(return_value={"products": [product]}),
        ):
            result = await CatalogService().import_all_pages(database, "piso", max_pages=10)

        self.assertEqual(result["pages_imported"], 1)
        self.assertEqual(result["created"], 1)
        self.assertEqual(result["stopped_reason"], "repeated_page")
        self.assertEqual(database.commits, 1)


if __name__ == "__main__":
    unittest.main()
