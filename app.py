from flask import Flask, request
from flask_restful import Api, Resource
import time, os
from db_init import initialize_db, Transaction

app = Flask(__name__)
api = Api(app)

VALID_CARD_TYPES = ["VISA", "MASTERCARD", "AMEX"]

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "config.yaml"))
initialize_db(CONFIG_PATH)

class Home(Resource):
    def get(self):
        return {"message": "Welcome to the Transactions API! Please use the /transactions endpoint to query transaction data."}    



class Transactions(Resource):
    def get(self):
        n = request.args.get("days")

        if n is None:
            return {"error": "please provide a 'days' query parameter"}, 400

        try:
            n = int(n)
        except ValueError:
            return {"error": "'days' must be a number"}, 400

        cutoff = int(time.time() * 1000) - (n * 24 * 60 * 60 * 1000)
        
        tranx = Transaction.select().where(Transaction.Date >= cutoff)

        return [{
            "Id": t.Id,
            "Date": t.Date,
            "Amount": float(t.Amount),
            "Currency": t.Currency,
            "Vendor": t.Vendor,
            "CardType": t.CardType
            } 
            for t in tranx]

class TransactionCount(Resource):
    def get(self):
        n = request.args.get("days")
        card_type = request.args.get("card_type")        

        if n is None or card_type is None:
            return {"error": "please provide both 'days' and 'card_type' query parameters"}, 400

        if card_type not in VALID_CARD_TYPES:
            return {"error": "invalid card type"}, 400
        
        card_type = card_type.capitalize()  # Convert to proper case for DB query

        try:
            n = int(n)
        except ValueError:
            return {"error": "'days' must be a number"}, 400

        cutoff = int(time.time() * 1000) - (n * 24 * 60 * 60 * 1000)

        tranx = Transaction.select().where(
            (Transaction.Date >= cutoff) & 
            (Transaction.CardType == card_type)
        ).count()

        return {"days": n, "card_type": card_type, "count": tranx}

class TransactionCountry(Resource):
    def get(self):
        n = request.args.get("days")
        country_of_origin = request.args.get("country")

        if n is None or country_of_origin is None:
            return {"error": "please provide both 'days' and 'country_of_origin' query parameters"}, 400

        try:
            n = int(n)
        except ValueError:
            return {"error": "'days' must be a number"}, 400

        cutoff = int(time.time() * 1000) - (n * 24 * 60 * 60 * 1000)

        tranx = Transaction.select().where(
                (Transaction.Date >= cutoff) & 
                (Transaction.CountryOrigin == country_of_origin)
            )
        
        return {
            "days": n, "country_of_origin": country_of_origin, 
            "transactions": [{
                    "Id": t.Id,
                    "Date": t.Date,
                    "Amount": float(t.Amount),
                    "Currency": t.Currency,
                    "Vendor": t.Vendor,
                    "CardType": t.CardType
                    } 
                    for t in tranx
                ]
        }
        

class TransactionAmount(Resource):
    def get(self):
        n = request.args.get("days")
        min_amount = request.args.get("min_amount")
        max_amount = request.args.get("max_amount")

        if n is None or min_amount is None or max_amount is None:
            return {"error": "please provide all 'days', 'min_amount', and 'max_amount' query parameters"}, 400

        try:
            n = int(n)
            min_amount = float(min_amount)
            max_amount = float(max_amount)

        except ValueError:
            return {"error": "Please ensure 'days', 'min_amount' and max_amount are supplied as numbers"}, 400

        cutoff = int(time.time() * 1000) - (n * 24 * 60 * 60 * 1000)

        tranx = Transaction.select().where(
                (Transaction.Date >= cutoff) & 
                (Transaction.Amount >= min_amount) & 
                (Transaction.Amount <= max_amount)
            )
        
        return {
            "days": n, 
            "min_amount": min_amount, 
            "max_amount": max_amount, 
            "total_count": tranx.count(),
            "transactions": [{
                    "Id": t.Id,
                    "Date": t.Date,
                    "Amount": float(t.Amount),
                    "Currency": t.Currency,
                    "Vendor": t.Vendor,
                    "CardType": t.CardType
                    } 
                    for t in tranx
                ]
        }
api.add_resource(Home, "/")
api.add_resource(Transactions, "/transactions")
api.add_resource(TransactionCount, "/transactions/count")
api.add_resource(TransactionCountry, "/transactions/country")
api.add_resource(TransactionAmount, "/transactions/amount")

if __name__ == "__main__":
    app.run(debug=True)