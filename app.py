from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)
DATABASE = "identifier.sqlite"
app.secret_key = "gjmbr'j'mybrb5yj3htivgha;'ej3q4238h"


def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        connection.execute('pragma foreign_keys=ON')
        return connection
    except Error as e:
        print(e)
    return None


def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True


def categories():
    query = "SELECT id, Category_Name FROM Categories"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    category = cur.fetchall()
    con.close()
    print(category)
    return category



@app.route('/')
def home_page():
    query = "SELECT id, Maori, English, Description, Level, image FROM Dictionary"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    word_data = cur.fetchall()
    con.close()

    return render_template("Home.html", logged_in=is_logged_in(), words=word_data, categories=categories())


@app.route('/categories/<category_id>', methods=['POST', 'GET'])
def categories_page(category_id):
    query = "SELECT category_id, Maori, English, Description, Level, image, id FROM Dictionary"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    word_data = cur.fetchall()

    if is_logged_in():
        if request.method == 'POST':
            Maori = request.form.get('Maori_word').title().strip()
            English = request.form.get('English_translation').title().strip()
            Level = request.form.get('Level')
            Description = request.form.get('Description')
            Date_Added = datetime.now()
            con = create_connection(DATABASE)
            query = "INSERT INTO dictionary (id, Maori, English, Description, Level, Date_Added, Category_id, image) VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)"

            cur = con.cursor()
            try:
                cur.execute(query, (Maori, English, Description, Level, Date_Added, category_id, English))
            except sqlite3.IntegrityError:
                return redirect('/?error=category+already+exists')
            con.commit()
            con.close()

        error = request.args.get("error")
        if error == None:
            error = ""

    return render_template("categories.html", words=word_data, categories=categories(), category_id=int(category_id), logged_in=is_logged_in())

@app.route('/word/<word>', methods=['POST', 'GET'])
def word_page(word):
    query = "SELECT * FROM Dictionary"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    word_data = cur.fetchall()
    query = "SELECT id, First_name, Last_Name FROM Admin_Logins"
    cur.execute(query)
    user_data = cur.fetchall()

    if request.method == "POST":
        print(word)
        maori = request.form["Maori_word"].strip().lower()
        english = request.form["English_translation"].strip().lower()
        level = request.form["Level"]
        description = request.form["Description"].strip()
        query = "UPDATE Dictionary SET Maori=?, English=?, Description=?, Level=? WHERE id=?"
        cur.execute(query, (maori, english, description, level, int(word)))
        con.commit()
    con.close()
    return render_template('word.html', words=word_data, word_id=int(word), logged_in=is_logged_in(), categories=categories(), user_data=user_data)


@app.route('/confirm_word/<word>')
def confirm_word_page(word):
    query = "SELECT * FROM Dictionary"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    word_data = cur.fetchall()
    return render_template('confirm_word.html', word_id=int(word), categories=categories(), words=word_data)

@app.route('/remove_word/<word>')
def remove_word_page(word):
    print(word)
    query = "DELETE FROM Dictionary WHERE id=?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (word,))
    con.commit()
    con.close()
    return redirect('/')

@app.route('/login', methods=['POST', 'GET'])
def login_page():
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

    return render_template("Login.html", logged_in=is_logged_in(), categories=categories())

@app.route('/signup', methods=['POST', 'GET'])
def signup_page():
    if is_logged_in():
        return redirect("/")
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')

        if password != cpassword:
            return redirect("/signup?error=Passwords+dont+match")
        if len(password) < 8:
            return redirect("/signup?error=Password+must+have+more+than+8+characters")

        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(DATABASE)

        query = "INSERT INTO Admin_logins (id, First_name, Last_name, Email, Password) VALUES(NULL, ?, ?, ?, ?)"

        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, hashed_password))
        except sqlite3.IntegrityError:
            return redirect('/signup?error=email+is+already+used')
        con.commit()
        con.close()

        return redirect("/login")

    error = request.args.get("error")
    if error == None:
        error = ""

    return render_template("Signup.html", error=error, logged_in=is_logged_in(), categories=categories())


@app.route('/logout', methods=['POST', 'GET'])
def logout_page():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=see+you+next+time!')


@app.route('/add_category', methods=['POST', 'GET'])
def add_category_page():
    if not is_logged_in():
        return redirect('/')
    if request.method == 'POST':
        category = request.form.get('category').title().strip()
        print(category)
        con = create_connection(DATABASE)
        query = "INSERT INTO Categories (id, Category_Name) VALUES(NULL, ?)"

        cur = con.cursor()
        try:
            cur.execute(query,  (category, ))
        except sqlite3.IntegrityError:
            return redirect('/?error=category+already+exists')
        con.commit()
        con.close()

        return redirect("/")

    error = request.args.get("error")
    if error == None:
        error = ""
    return render_template('add_category.html', categories=categories(), logged_in=is_logged_in())


@app.route('/confirm/<category>')
def confirm_page(category):
    return render_template('confirm.html', category_id=int(category), categories=categories())

@app.route('/remove_category/<category>')
def remove_category_page(category):
    query = "DELETE FROM Dictionary WHERE Category_id=?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (category, ))
    query="DELETE FROM categories WHERE id=?"
    cur.execute(query, (category,))
    con.commit()
    con.close()

    return redirect('/')



if __name__ == '__main__':
    app.run()