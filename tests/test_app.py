import unittest, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from app import app

class TestTransactionAPI(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_transactions_no_params(self):
        response = self.client.get("/transactions")
        self.assertEqual(response.status_code, 400)

    def test_transactions_invalid_days(self):
        response = self.client.get("/transactions?days=abc")
        self.assertEqual(response.status_code, 400)

    def test_transactions_valid_days(self):
        response = self.client.get("/transactions?days=9999")
        self.assertEqual(response.status_code, 200)

    def test_count_invalid_card_type(self):
        response = self.client.get("/transactions/count?days=30&card_type=rubbish")
        self.assertEqual(response.status_code, 400)

    def test_count_valid_params(self):
        response = self.client.get("/transactions/count?days=999&card_type=VISA")
        self.assertEqual(response.status_code, 200)

    def test_card_invalid_case(self):
        response = self.client.get("/transactions/count?days=9999&card_type=mastercard")
        self.assertEqual(response.status_code, 400)

    def test_count_returns_count_field(self):
        response = self.client.get("/transactions/count?days=9999&card_type=VISA")
        data = response.get_json()
        self.assertIn("count", data)

if __name__ == "__main__":
    unittest.main()