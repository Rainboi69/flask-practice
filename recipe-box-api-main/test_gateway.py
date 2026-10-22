
"""Basic acceptance checks for the Recipe Box API Gateway."""

import unittest
import requests

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 3


class GatewayTests(unittest.TestCase):

    def test_01_gateway_home(self):
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["message"],
            "Recipe Box API Gateway",
        )

    def test_02_public_recipe_list(self):
        response = requests.get(
            f"{BASE_URL}/recipes", timeout=TIMEOUT
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_03_missing_recipe(self):
        response = requests.get(
            f"{BASE_URL}/recipes/999999", timeout=TIMEOUT
        )
        self.assertEqual(response.status_code, 404)

    def test_04_authentication_required(self):
        response = requests.get(
            f"{BASE_URL}/auth/me", timeout=TIMEOUT
        )
        self.assertEqual(response.status_code, 401)

    def test_05_recipe_creation_requires_login(self):
        response = requests.post(
            f"{BASE_URL}/recipes",
            json={
                "title": "Unauthorized Gateway Test",
                "ingredients": "test",
            },
            timeout=TIMEOUT,
        )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
