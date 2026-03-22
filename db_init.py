from peewee import *
import yaml
import pymysql


## Creatin a "blank" database object
pymysql.install_as_MySQLdb()
db = MySQLDatabase(None)

class Transaction(Model):
    Id = CharField(max_length=36, primary_key=True)
    Date = BigIntegerField()
    Currency = CharField(max_length=10)
    Amount = DecimalField(max_digits=10, decimal_places=2)
    Vendor = CharField(max_length=255)
    CardType = CharField()
    CardNumber = CharField(max_length=16, constraints=[Check('LENGTH(CardNumber) = 16')])
    Address = CharField(max_length=255)
    CountryOrigin = CharField(max_length=3)

    class Meta:
        database = db 

def initialize_db(config_path):    
    # full_path = os.path.abspath(config_path)
    # print(f"debugger : {sys.executable}")
    with open(config_path, "r") as f:
        db_config = yaml.safe_load(f)["database"]

    '''Initialize the database connection and create tables if they don't exist'''

    ## Create db if not exists
    conn = pymysql.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        port=db_config["port"]
    )
    conn.cursor().execute(f"CREATE DATABASE IF NOT EXISTS {db_config['name']}")
    conn.close()
    
    
    db.init(
        db_config["name"], ## DB name
        host=db_config["host"], 
        user=db_config["user"],
        password=db_config["password"], 
        port=db_config["port"])
    
    db.connect()
    db.create_tables([Transaction])
    return db
