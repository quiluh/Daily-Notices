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
        # DATABASE
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def Index():
    pass

@app.route("/login",methods=["GET","POST"])
def LogIn():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * from teachers where username=%s",(username,))
                user = cursor.fetchone()
        
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