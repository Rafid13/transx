from db_init import initialize_db, Transaction
import uuid, random, time, argparse, os
from peewee import chunked


VENDORS = ["Supermarket-1", "Supermarket-2", "Shop-1", "Shop-2", "ServiceProvider-1", "ServiceProvider-2"]
CARD_TYPES = ["VISA", "MASTERCARD", "AMEX"]
CURRENCIES = {"UK": "GBP", "US": "USD", "AU": "AUD", "CA": "CAD", "FR": "EUR"}
ADDRESSES = ["12 Baker Street, London", "London Eye, London", "Times Square, New York", "Eiffel Tower, Paris", "Sydney Opera House, Sydney", "CN Tower, Toronto"]

def main():
    parser = argparse.ArgumentParser(description="Seed the database with transaction data.")
    
    parser.add_argument("--tranx", type=int, dest="transactions_to_insert", help="Number of transactions")
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--db-config", type=str, default="../config.yaml", help="Path to config.yaml")

    args = parser.parse_args()    

    config_path = os.path.join(os.path.dirname(__file__), args.db_config)
    print(f"Initializing database connection using: {config_path}")
    db = initialize_db(config_path)
    
    count = args.transactions_to_insert 
    start_ms = int(time.mktime(time.strptime(args.start_date, "%Y-%m-%d")) * 1000)
    end_ms = int(time.mktime(time.strptime(args.end_date, "%Y-%m-%d")) * 1000)

    transactions = []

    '''Generate unique UUIDs for transactions in advance to avoid potential duplicates.'''
    ids = set()
    while len(ids) < count:
        ids.add(str(uuid.uuid4()))
    ids = list(ids)

    for i in range(count):
        country_key = random.choice(list(CURRENCIES.keys()))
        country_currency = CURRENCIES[country_key]
        transactions.append({
            "Id": ids[i],
            "Date": random.randint(start_ms, end_ms),
            "Currency": country_currency,
            "Amount": round(random.uniform(1.0, 1000.0), 2),
            "Vendor": random.choice(list(VENDORS)),
            "CardType": random.choice(list(CARD_TYPES)),
            "CardNumber": ''.join(random.choices("0123456789", k=16)),
            "Address": random.choice(list(ADDRESSES)),
            "CountryOrigin": country_key
        })

    with db.atomic():
        for batch in chunked(transactions, 500):
            Transaction.insert_many(batch).execute()

    print(f"Successfully inserted {count} records.")

if __name__ == "__main__":
    main()

# def main(db_config, transactions_to_insert=None, start_date=None, end_date=None):

