from flask import Flask, url_for, request, session, render_template, redirect, g
from werkzeug.security import generate_password_hash, check_password_hash

import psycopg2
import os
import pickle 
from dotenv import load_dotenv
import numpy as np

from initdb import close_db, init_db, get_db
from initml import init_model

load_dotenv()

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

app = Flask(__name__, template_folder='templates', static_folder='static')
app.teardown_appcontext(close_db)
app.secret_key = os.getenv('FLASK_SECKEY')


@app.cli.command('init-db')
def init_db_command():
    init_db()
    print("DB init successfully")

@app.before_request
def check_status():
    allowed_routes = ['register', 'login', 'static']
    if 'user_id' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method=='POST':
        mail_text = request.form['prompt']
        error = None 

        if not mail_text:
            error = "Введите текст"
        
        if error is not None:
            return render_template('index.html', error = error)

        init_model()

        y_pred_false = (g.pipeline.predict([mail_text]) == 0).astype(int)
        y_pred_true = (g.pipeline.predict([mail_text]) == 1).astype(int)

        y_proba = np.round(g.pipeline.predict_proba([mail_text]), 2)*100

        if y_pred_false == 1:
            return render_template('index.html', prompt = mail_text, prediction_false=y_pred_false, not_spam_proba=y_proba[0][0])
        
        return render_template('index.html', prompt = mail_text, prediction_true=y_pred_true, not_spam_proba=y_proba[0][1])
    
    return render_template('index.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if password != request.form['confirm_password']:
            error = 'Пароли не совпадают'
            return render_template("register.html")

        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO "user" (username, password) VALUES (%s, %s)""", (username, generate_password_hash(password)))
                conn.commit()
        except psycopg2.errors.UniqueViolation:
            error = "Этот пользователь уже зарегестрирован"

        if error is None:
            session['user_id'] = username
            return render_template('index.html')
        return render_template('register.html', error=error)

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        try:
            conn = get_db()
            with conn.cursor() as cur:
                cur.execute("""SELECT username, password FROM "user" WHERE username = %s""", (username, ))
                user = cur.fetchone()
        except psycopg2.errors.OperationalError:
            error = 'Произошла ошибка с БД. Вы точно проинициализировали БД?'
        
        error = None
        if user is None:
            return render_template('login.html', error='This user doesnt exist...')
        db_user, db_pass = user
        if db_user is None:
            error = 'Пользователь не найден'
        elif not check_password_hash(db_pass, password):
            error = 'Некорректный пароль'
        
        if error is not None:
            return render_template('login.html', error=error)
        
        return render_template('index.html')
    
    return render_template('login.html')