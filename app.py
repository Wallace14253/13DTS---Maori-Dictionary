from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime
import smtplib, ssl
from smtplib import SMTPAuthenticationError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
bcrypt = Bcrypt(app)
DATABASE = ""
app.secret_key = "gjmbr'j'mybrb5yj3htivgha;'ej3q4238h"


def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        connection.execute('pragma foreign_keys=ON')
        return connection
    except Error as e:
        print(e)
    return None


@app.route('/')
def home():
    return render_template("Home.html")

@app.route('/categories/<catagories>')
def categories():
    return render_template("home.html")