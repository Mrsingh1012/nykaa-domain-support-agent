
import unittest

from src.product_tool import search_products
from src.support_agent import detect_intent, handle_customer_message


class TestProductTool(unittest.TestCase):

    def test_search_existing_product(self):
        products = search_products("serum")

        self.assertTrue(products)
        self.assertTrue(
            any("serum" in p["name"].casefold() for p in products)
        )

    def test_budget_filter(self):
        products = search_products("skincare", max_price=500)

        for product in products:
            self.assertLessEqual(float(product["price"]), 500)

    def test_unknown_product(self):
        products = search_products("nonexistentproductxyz")
        self.assertEqual(products, [])

    def test_out_of_stock_excluded(self):
        products = search_products("cleanser")
        self.assertEqual(products, [])

    def test_product_intent(self):
        self.assertEqual(
            detect_intent("Show me face serum"),
            "product_search",
        )

    def test_product_response(self):
        response = handle_customer_message("Show me face serum")

        self.assertIn("Vitamin C Face Serum", response)
        self.assertIn("₹699", response)


if __name__ == "__main__":
    unittest.main(verbosity=2)
