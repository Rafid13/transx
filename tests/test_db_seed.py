import unittest, sys, os, time, uuid, random
from peewee import SqliteDatabase, chunked

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import db_init

VENDORS = ["Supermarket-1", "Supermarket-2", "Shop-1", "Shop-2", "ServiceProvider-1", "ServiceProvider-2"]
CARD_TYPES = ["VISA", "MASTERCARD", "AMEX"]
COUNTRIES = {"UK", "US", "EUR", "AUD", "CAD"}
ADDRESSES = ["12 Baker Street, London", "London Eye, London", "Times Square, New York", "Eiffel Tower, Paris", "Sydney Opera House, Sydney", "CN Tower, Toronto"]


test_db = SqliteDatabase(":memory:")


def seed_records(count=50, start_date="2025-01-01", end_date="2025-12-31"):
    """Generates and inserts transaction records intp the in memory database."""

    start_ms = int(time.mktime(time.strptime(start_date, "%Y-%m-%d")) * 1000)
    end_ms = int(time.mktime(time.strptime(end_date, "%Y-%m-%d")) * 1000)

    transactions = []
    for _ in range(count):
        transactions.append({
            "Id": str(uuid.uuid4()),
            "Date": random.randint(start_ms, end_ms),
            "Currency": random.choice(list(COUNTRIES)),
            "Amount": round(random.uniform(1.0, 1000.0), 2),
            "Vendor": random.choice(list(VENDORS)),
            "CardType": random.choice(list(CARD_TYPES)),
            "CardNumber": ''.join(random.choices("0123456789", k=16)),
            "Address": random.choice(list(ADDRESSES)),
            "CountryOrigin": random.choice(list(COUNTRIES))
        })

    with test_db.atomic():
        for batch in chunked(transactions, 500):
            db_init.Transaction.insert_many(batch).execute()


class TestDbSeedData(unittest.TestCase):

    def setUp(self):
        db_init.db = test_db
        db_init.Transaction._meta.database = test_db
        test_db.connect(reuse_if_open=True)
        test_db.create_tables([db_init.Transaction])

    def tearDown(self):
        test_db.drop_tables([db_init.Transaction])

    def test_correct_number_of_records(self):
        """Test for inserted transaction count."""
        seed_records(count=50)
        self.assertEqual(db_init.Transaction.select().count(), 50)

    def test_correct_number_large_batch(self):
        """Test for batch insertion logic."""
        seed_records(count=750)
        self.assertEqual(db_init.Transaction.select().count(), 750)

    def test_ids_are_unique(self):
        """Test for unique UUIDs in the Id field."""
        seed_records(count=100)
        ids = [t.Id for t in db_init.Transaction.select()]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate IDs found")

    def test_card_number_is_16_digits(self):
        """Test for card number length and digit only constraint."""
        seed_records(count=50)
        for t in db_init.Transaction.select():
            self.assertEqual(len(t.CardNumber), 16, f"CardNumber wrong length: {t.CardNumber}")
            self.assertTrue(t.CardNumber.isdigit(), f"CardNumber contains non-digits: {t.CardNumber}")

    def test_all_required_fields_present(self):
        """Test for inserted data quality by checking presence of all required fields."""
        required_fields = {"Id", "Date", "Amount", "Currency", "Vendor",
                           "CardType", "CardNumber", "Address", "CountryOrigin"}
        seed_records(count=20)
        for t in db_init.Transaction.select():
            record_fields = {col.name for col in db_init.Transaction._meta.sorted_fields}
            self.assertEqual(required_fields, record_fields)


if __name__ == "__main__":
    unittest.main()