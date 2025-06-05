from flask import Flask, url_for, request, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash

import psycopg2
import os 
from dotenv import load_dotenv

from initdb import close_db, init_db, get_db

load_dotenv()

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

app = Flask(__name__, template_folder='templates/', static_folder='static/')
app.teardown_appcontext(close_db)

@app.cli.command('init-db')
def init_db_command():
    init_db()
    print("DB init successfully")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        try:
            conn = psycopg2.connect(
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host='localhost',
                port=POSTGRES_PORT
            )
            with conn.cursor() as cur:
                cur.execute("SELECT username, password WHERE username = %s", (username, ))
                user = cur.fetchone()
        except psycopg2.errors.OperationalError:
            error = 'Some error has occured with DataBase. Make sure you init db'
        
        error = None
        db_user, db_pass = user
        if db_user is None:
            error = 'User not found in database'
        elif check_password_hash(password, db_pass):
            error = 'Incorrect password'
        
        if error is not None:
            return render_template('login.html', error=error)
        
        return render_template('index.html')
    
    return render_template('login.html')