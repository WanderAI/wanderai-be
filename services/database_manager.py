from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self, db_engine: str) -> None:
        self.conn = create_engine(db_engine).connect()

import os

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_database = os.getenv("DB_DATABASE")

db_engine = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
dbInstance = DatabaseManager(db_engine=db_engine)