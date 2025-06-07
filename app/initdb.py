import psycopg2
import os 
from dotenv import load_dotenv

from flask import g, current_app

load_dotenv()

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_HOST = os.getenv('POSTGRES_HOST')

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        
    return g.db

def init_db():
    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """
                DROP TABLE IF EXISTS "user";
                CREATE TABLE IF NOT EXISTS "user" (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
                );
                """
            ) 
            db.commit()
    finally:
        db.close()


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()