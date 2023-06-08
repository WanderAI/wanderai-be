from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self, db_engine: str) -> None:
        self.conn = create_engine(db_engine).connect()

import os

db_user = "root"
db_password = "wanderainihngab"
db_host = "34.101.159.179"
db_port = "3306"
db_database = "staging"

db_engine = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
dbInstance = DatabaseManager(db_engine=db_engine)