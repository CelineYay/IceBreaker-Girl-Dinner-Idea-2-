from flask_sqlalchemy import SQLAlchemy
from flask import Flask


app = Flask(__name__)
app.secret_key = 'very very secret key, no one would guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Ice_Breaker.db'
db = SQLAlchemy(app)
