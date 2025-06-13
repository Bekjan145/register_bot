from os import getenv
from dotenv import load_dotenv

load_dotenv()

db_user = getenv("db_user")
password = getenv("password")
host = getenv("host")
port = getenv("port")
db_name = getenv("db_name")

if __name__ == "__main__":
    print(db_user, password, host, port, db_name)