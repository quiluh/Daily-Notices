import pymysql
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "myLittleSodaPop67"

def create_connection():
    return pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Abcdefg123!",
        database="daily_notices",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def Index():
    pass

@app.route("/login",methods=["GET","POST"])
def LogIn():
    if request.method == "POST":
        # GRAB INPUTTED USERNAME AND PASSWORD
        username = request.form["username"]
        password = request.form["password"]

        # ESTABLISH CONNECTION WITH DATABASE
        with create_connection() as connection:
            with connection.cursor() as cursor:
                # FIND THE USER IN THE DATABASE -- SHOULD ONLY RETURN ONE USER
                cursor.execute("SELECT * from teachers where username=%s",(username,))
                user = cursor.fetchone()
        
        # CHECK IF USER EXISTS AND PASSWORD IS VALID, SET SESSION USER TO THE VALID USERNAME
        if user and user["password"] == password:
            session["user"] = user["username"]
            return redirect("/")
        else:
            pass # CODE THIS LATER
    elif request.method == "GET":
        return render_template("login.html")

@app.route("/add")
def Add():
    pass

@app.route("/delete")
def Delete():
    pass

@app.route("/edit")
def Edit():
    pass

app.run(debug=True)