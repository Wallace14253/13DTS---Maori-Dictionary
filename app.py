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
DATABASE = "MaoriDictionary.db"
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


def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True

@app.route('/login', methods=['POST', 'GET'])
def login():
    if is_logged_in():
        return redirect("/")
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"].strip()

        query = """SELECT id, First_name, Password FROM Admin_Logins WHERE Email = ?"""
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email, ))
        user_data = cur.fetchall()
        con.close()
        print(user_data)

        try:
            customerid = user_data[0][0]
            firstname = user_data[0][1]
            db_password = user_data[0][2]
        except IndexError:
            return redirect("/login?error=Email+or+password+incorrect")


        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")



        session['email'] = email
        session['customerid'] = customerid
        session['firstname'] = firstname
        print(session)
        return redirect('/')

    return render_template("Login.html", logged_in=is_logged_in())

@app.route('/signup')
def signup():
    return render_template('signup.html', logged_in=is_logged_in())


if __name__ == '__main__':
    app.run()