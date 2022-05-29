# Importing modules
from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)
# Creating database variable and the secret key
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
        return False
    else:
        return True


# Create a function to check if the user is a teacher
def is_teacher():
    if session.get("login_id") is None:
        return False
    else:
        con = create_connection(DATABASE)
        cur = con.cursor()
        login_id = session['login_id']
        query = "SELECT Admin FROM Admin_logins WHERE id = ?"
        cur.execute(query, (login_id,))
        admin = cur.fetchall()
        if admin[0][0] == "Teacher":
            return True
        else:
            return False


# Create a function that gets all the category ids and names and return them
def get_categories():
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT id, Category_Name FROM Categories ORDER BY Category_Name"

    cur.execute(query)
    category = cur.fetchall()
    con.close()
    return category


# Create a function that gets everything from the dictionary database and returns themn
def get_words():
    query = "SELECT * FROM Dictionary ORDER BY English"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    word_data = cur.fetchall()
    return word_data


# The home page
@app.route('/', methods=['GET', 'POST'])
def home_page():
    # Check if the method of the form to add a category is post
    if request.method == 'POST':
        # If the method is post then get the category from the form
        category = request.form.get('category').title().strip()
        # Insert the category into the database
        con = create_connection(DATABASE)
        query = "INSERT INTO Categories (id, Category_Name) VALUES(NULL, ?)"

        cur = con.cursor()
        # Check if the category already exists
        try:
            cur.execute(query, (category,))
        except sqlite3.IntegrityError:
            # If the category already exists return them to the home page with an error
            return redirect('/?error=category+already+exists')
        con.commit()
        con.close()
    # Check to see if there is a message
    message = request.args.get("message")
    # If there is no message set message to an empty string
    if message == None:
        message = ""
    # Check to see if there was an error
    error = request.args.get("error")
    # If there is no error set error to an empty string
    if error == None:
        error = ""

    # Render the home page
    return render_template("Home.html", logged_in=is_logged_in(), categories=get_categories(),
                           is_teacher=is_teacher(), error=error, message=message)


# The search page
@app.route('/search')
def search_page():
    # Get the search argument
    search = request.args.get('search', type=str)
    # Check if the search is empty
    if search is None or search == '':
        # If the search is empty set search to an empty string and searched to false
        search = ''
        searched = False
    else:
        # I the search isn't empty add a % wildcard to the end of the string for sql
        # and set searched to true
        search = "%" + search + "%"
        searched = True
    # Select all the words that match the search and store it in the word_data variable
    query = "SELECT * FROM Dictionary WHERE English LIKE ? OR Maori LIKE ?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (search, search))
    word_data = cur.fetchall()

    # Render the search page
    return render_template('search.html', categories=get_categories(), word_data=word_data, searched=searched,
                           logged_in=is_logged_in())


# The category page
@app.route('/categories/<category_id>', methods=['POST', 'GET'])
def categories_page(category_id):
    # Get all the categories and store them in the variable categories
    categories = get_categories()
    # Check if the category they are looking for is in the database
    try:
        category_id = int(category_id)
    except:
        return redirect('/')
    for category in categories:
        if category[0] == category_id:
            # If the category is found, make the page_found variable true
            page_found = True
            break
        else:
            # If the category is not found, make the page_found variable false
            page_found = False

    # Check if the user is logged in
    if is_logged_in():
        # Check if the method of the form to add a category is post
        if request.method == 'POST':
            # Get all the information from the form
            Maori = request.form.get('Maori_word').title().strip()
            English = request.form.get('English_translation').title().strip()
            Level = request.form.get('Level')
            Description = request.form.get('Description')
            Date_Added = datetime.now().strftime('%d-%m-%y')
            login_id = session["login_id"]
            image = 'noimage.png'

            # Insert all the information into the database as a new word
            con = create_connection(DATABASE)
            query = "INSERT INTO dictionary (id, Maori, English, Description, Level, Date_Added, Login_id, Category_id, image) VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
            cur = con.cursor()
            cur.execute(query, (Maori, English, Description, Level, Date_Added, login_id, category_id, image))
            con.commit()
            con.close()
    # Render the category page
    return render_template("categories.html", words=get_words(), categories=categories, category_id=int(category_id),
                           logged_in=is_logged_in(), is_teacher=is_teacher(), page_found=page_found)


# The page that displays the word
@app.route('/word/<word_id>', methods=['POST', 'GET'])
def word_page(word_id):
    # Get all the words and store them in the variable words
    words = get_words()
    # Check if the category they are looking for is in the database
    try:
        int(word_id)
    except:
        return redirect('/')
    for word in words:
        if word[0] == int(word_id):
            # If the category is found, make the page_found variable true
            page_found = True
            break
        else:
            # If the category is not found, make the page_found variable false
            page_found = False

    # Get the first name and last name of all the users with a login and store it in user_data
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT id, First_name, Last_Name FROM Admin_Logins"
    cur.execute(query)
    user_data = cur.fetchall()

    # Check if the method of the form to add a category is post
    if request.method == "POST":
        # Get all the information from the form
        maori = request.form["Maori_word"].strip().lower()
        english = request.form["English_translation"].strip().lower()
        level = request.form["Level"]
        description = request.form["Description"].strip()
        login_id = session['login_id']
        # Update the word in the database with the new information from the form
        query = "UPDATE Dictionary SET Maori=?, English=?, Description=?, Level=?, Login_id=? WHERE id=?"
        cur.execute(query, (maori, english, description, level, login_id, int(word_id)))
        con.commit()
    con.close()
    # Render the word page
    return render_template('word.html', words=get_words(), word_id=int(word_id), logged_in=is_logged_in(),
                           categories=get_categories(), user_data=user_data, is_teacher=is_teacher(),
                           page_found=page_found)


# The page for confirmation that the user wants to delete the word from the database
@app.route('/confirm_word/<word>')
def confirm_word_page(word):
    return render_template('confirm_word.html', word_id=int(word), categories=get_categories(), words=get_words(),
                           is_teacher=is_teacher())


# Removing the word from the database
@app.route('/remove_word/<word>')
def remove_word_page(word):
    query = "DELETE FROM Dictionary WHERE id=?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (word,))
    con.commit()
    con.close()
    # Redirect them to the home page after deleting the word
    return redirect('/?message=Word+deleted+successfully')


# The login page
@app.route('/login', methods=['POST', 'GET'])
def login_page():
    # Check if the user is logged in
    if is_logged_in():
        # If they are, redirect them to the home page
        return redirect("/")
    # Check if the method of the form to add a category is post
    if request.method == "POST":
        # Get all the information from the form
        email = request.form["email"].strip().lower()
        password = request.form["password"].strip()
        # Get the first name and password of the corresponding email
        query = """SELECT id, First_name, Password FROM Admin_Logins WHERE Email = ?"""
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        con.close()
        try:
            # Try to store the data in variables
            login_id = user_data[0][0]
            db_password = user_data[0][2]
        except IndexError:
            # If there is an index error than redirect them back to the login page with an error message
            return redirect("/login?error=Email+or+password+incorrect")
        # Check if the password that the user entered matches the one in the database
        if not bcrypt.check_password_hash(db_password, password):
            # If the passwords don't match redirect them to the login page with an error message
            return redirect("/login?error=Email+invalid+or+password+incorrect")
        # Create a session of their id and email
        session['login_id'] = login_id
        session['email'] = email
        # After successfully logging in, redirect them to the home page
        return redirect('/?message=Successfully+logged+in')

    # Check to see if there was an error
    error = request.args.get("error")
    # If there is no error set error to an empty string
    if error == None:
        error = ""
    # Render the login page
    return render_template("Login.html", logged_in=is_logged_in(), categories=get_categories(), is_teacher=is_teacher(),
                           error=error)


# The signup page
@app.route('/signup', methods=['POST', 'GET'])
def signup_page():
    # Check if the user is logged in
    if is_logged_in():
        # If they are, redirect them to the home page
        return redirect("/")
    # Check if the method of the form to add a category is post
    if request.method == 'POST':
        # Get all the information from the form
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        admin = request.form.get('admin')
        # Check if the passwords they entered is the same
        if password != cpassword:
            # If they don't match return them to the signup page with an error message
            return redirect("/signup?error=Passwords+dont+match")
        # Check if the passwords are longer than 8 characters long
        if len(password) < 8:
            # If they aren't return them to the signup page with an error message
            return redirect("/signup?error=Password+must+have+more+than+8+characters")
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password)
        # Insert the login info into the database
        con = create_connection(DATABASE)
        query = "INSERT INTO Admin_logins (id, First_name, Last_name, Email, Password, Admin) VALUES(NULL, ?, ?, ?, ?, ?)"
        cur = con.cursor()
        # Check if the email has already been used
        try:
            cur.execute(query, (fname, lname, email, hashed_password, admin))
        except sqlite3.IntegrityError:
            # If it has return them to the signup page with an error message
            return redirect('/signup?error=Email+is+already+in+use')
        con.commit()
        con.close()

        # If the successfully sign up redirect them to the login page
        return redirect("/login")

    # Check to see if there was an error
    error = request.args.get("error")
    # If there is no error set error to an empty string
    if error == None:
        error = ""

    # Render the sign up page
    return render_template("Signup.html", error=error, logged_in=is_logged_in(), categories=get_categories(),
                           is_teacher=is_teacher())


# Log the user out by deleting the sessions
@app.route('/logout', methods=['POST', 'GET'])
def logout_page():
    [session.pop(key) for key in list(session.keys())]
    # Redirect them to the home page after logging them out
    return redirect('/?message=see+you+next+time!')


# The page for confirmation that the user wants to delete the category from the database
@app.route('/confirm/<category>')
def confirm_page(category):
    return render_template('confirm_category.html', category_id=int(category), categories=get_categories(),
                           words=get_words(),
                           is_teacher=is_teacher())


# Removing the category from the database
@app.route('/remove_category/<category>')
def remove_category_page(category):
    query = "DELETE FROM categories WHERE id=?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (category,))
    con.commit()
    con.close()
    # Redirect them to the home page after deleting the category
    return redirect('/?message=Category+deleted+successfully')


# Run the code
if __name__ == '__main__':
    app.run()
