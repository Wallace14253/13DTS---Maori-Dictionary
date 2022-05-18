# Importing modules
from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime

# Creating database variable and the secret key
app = Flask(__name__)
bcrypt = Bcrypt(app)
DATABASE = "identifier-w10521.sqlite"
app.secret_key = "gjmbr'j'mybrb5yj3htivgha;'ej3q4238h"


# Create a function to make a connection with the database
def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        connection.execute('pragma foreign_keys=ON')
        return connection
    except Error as e:
        print(e)
    return None


# Create a function to check if the user is logged in
def is_logged_in():
    if session.get("email") is None:
        # print("not logged in")
        return False
    else:
        # print("logged in")
        return True


# Create a function to check if the user is a teacher
def is_teacher():
    if session.get("login_id") is None:
        print("no email")
        return False
    else:
        con = create_connection(DATABASE)
        cur = con.cursor()
        login_id = session['login_id']
        query = "SELECT Admin FROM Admin_logins WHERE id = ?"
        cur.execute(query, (login_id,))
        admin = cur.fetchall()
        print(admin[0][0])
        if admin[0][0] == "Teacher":
            print("is teacher")
            return True
        else:
            print("is student")
            return False


def get_categories():
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT id, Category_Name FROM Categories"

    cur.execute(query)
    category = cur.fetchall()
    con.close()
    # print(category)
    return category


def get_words():
    query = "SELECT * FROM Dictionary"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    word_data = cur.fetchall()
    return word_data


@app.route('/', methods=['GET', 'POST'])
def home_page():
    query = "SELECT id, Maori, English, Description, Level, image FROM Dictionary"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    word_data = cur.fetchall()
    con.close()

    if request.method == 'POST':
        category = request.form.get('category').title().strip()
        # print(category)
        con = create_connection(DATABASE)
        query = "INSERT INTO Categories (id, Category_Name) VALUES(NULL, ?)"

        cur = con.cursor()
        try:
            cur.execute(query, (category,))
        except sqlite3.IntegrityError:
            return redirect('/?error=category+already+exists')
        con.commit()
        con.close()

        return redirect("/")

    error = request.args.get("error")
    if error == None:
        error = ""

    return render_template("Home.html", logged_in=is_logged_in(), words=word_data, categories=get_categories(),
                           is_teacher=is_teacher())


@app.route('/search')
def search_page():
    search = request.args.get('search', type=str)
    if search is None:
        search = ''
        searched = False
    else:
        search = search + "%"
        searched = True
    query = "SELECT * FROM Dictionary WHERE English LIKE ? OR Maori LIKE ?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (search, search))
    word_data = cur.fetchall()


    return render_template('search.html', categories=get_categories(), word_data=word_data, searched=searched)


@app.route('/categories/<category_id>', methods=['POST', 'GET'])
def categories_page(category_id):
    query = "SELECT category_id, Maori, English, Description, Level, image, id FROM Dictionary"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    word_data = cur.fetchall()

    if is_logged_in():
        if request.method == 'POST':
            print(request.form)
            Maori = request.form.get('Maori_word').title().strip()
            English = request.form.get('English_translation').title().strip()
            Level = request.form.get('Level')
            Description = request.form.get('Description')
            Date_Added = datetime.now()
            login_id = session["login_id"]
            image = 'noimage.png'
            con = create_connection(DATABASE)
            query = "INSERT INTO dictionary (id, Maori, English, Description, Level, Date_Added, Login_id, Category_id, image) VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?)"

            cur = con.cursor()
            try:
                cur.execute(query, (Maori, English, Description, Level, Date_Added, login_id, category_id, image))
            except sqlite3.IntegrityError:
                return redirect('/?error=category+already+exists')
            con.commit()
            con.close()
            return redirect(request.url)

        error = request.args.get("error")
        if error == None:
            error = ""

    return render_template("categories.html", words=word_data, categories=get_categories(), category_id=int(category_id),
                           logged_in=is_logged_in(), is_teacher=is_teacher())


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
        # print(word)
        maori = request.form["Maori_word"].strip().lower()
        english = request.form["English_translation"].strip().lower()
        level = request.form["Level"]
        description = request.form["Description"].strip()
        login_id = session['login_id']
        query = "UPDATE Dictionary SET Maori=?, English=?, Description=?, Level=?, Login_id=? WHERE id=?"
        cur.execute(query, (maori, english, description, level, login_id, int(word)))
        con.commit()
        return redirect(request.url)
    con.close()
    return render_template('word.html', words=word_data, word_id=int(word), logged_in=is_logged_in(),
                           categories=get_categories(), user_data=user_data, is_teacher=is_teacher())


@app.route('/confirm_word/<word>')
def confirm_word_page(word):
    query = "SELECT * FROM Dictionary"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    word_data = cur.fetchall()
    return render_template('confirm_word.html', word_id=int(word), categories=get_categories(), words=word_data,
                           is_teacher=is_teacher())


@app.route('/remove_word/<word>')
def remove_word_page(word):
    # print(word)
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
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        con.close()
        # print(user_data)

        try:
            login_id = user_data[0][0]
            db_password = user_data[0][2]
        except IndexError:
            return redirect("/login?error=Email+or+password+incorrect")

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

        session['login_id'] = login_id
        session['email'] = email
        # print(session)
        return redirect('/')

    return render_template("Login.html", logged_in=is_logged_in(), categories=get_categories(), is_teacher=is_teacher())


@app.route('/signup', methods=['POST', 'GET'])
def signup_page():
    if is_logged_in():
        return redirect("/")
    if request.method == 'POST':
        # print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        admin = request.form.get('admin')

        if password != cpassword:
            error = "Passwords do not match"
            return redirect("/signup?error=Passwords+dont+match")
        if len(password) < 8:
            error = "Password needs to be longer than 8 characters"
            return redirect("/signup?error=Password+must+have+more+than+8+characters")

        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(DATABASE)

        query = "INSERT INTO Admin_logins (id, First_name, Last_name, Email, Password, Admin) VALUES(NULL, ?, ?, ?, ?, ?)"

        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, hashed_password, admin))
        except sqlite3.IntegrityError:
            return redirect('/signup?error=email+is+already+used')
            error = "Email is already in use"
        con.commit()
        con.close()

        return redirect("/login")

    error = request.args.get("error")
    if error == None:
        error = ""

    return render_template("Signup.html", error=error, logged_in=is_logged_in(), categories=get_categories(),
                           is_teacher=is_teacher())


@app.route('/logout', methods=['POST', 'GET'])
def logout_page():
    # print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    # print(list(session.keys()))
    return redirect('/?message=see+you+next+time!')


@app.route('/add_category', methods=['POST', 'GET'])
def add_category_page():
    if not is_logged_in():
        return redirect('/')

    if request.method == 'POST':
        category = request.form.get('category').title().strip()
        # print(category)
        con = create_connection(DATABASE)
        query = "INSERT INTO Categories (id, Category_Name) VALUES(NULL, ?)"

        cur = con.cursor()
        try:
            cur.execute(query, (category,))
        except sqlite3.IntegrityError:
            return redirect('/?error=category+already+exists')
        con.commit()
        con.close()

        return redirect("/")

    return render_template('add_category.html', categories=get_categories(), logged_in=is_logged_in(),
                           is_teacher=is_teacher())


@app.route('/confirm/<category>')
def confirm_page(category):
    query = "SELECT category_id, Maori, English, Description, Level, image, id FROM Dictionary"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    word_data = cur.fetchall()
    return render_template('confirm.html', category_id=int(category), categories=get_categories(), words=word_data,
                           is_teacher=is_teacher())


@app.route('/remove_category/<category>')
def remove_category_page(category):
    query = "DELETE FROM Dictionary WHERE Category_id=?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (category,))
    query = "DELETE FROM categories WHERE id=?"
    cur.execute(query, (category,))
    con.commit()
    con.close()

    return redirect('/')


if __name__ == '__main__':
    app.run()
