import pymysql
import datetime
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
    return render_template("index.html")

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
    
@app.route("/logout")
def LogOut():
    session.pop("user", None)
    return redirect("/login")
    
@app.route("/register",methods=["GET","POST"]) # STORE USERNAME APPENDED TO PASSWORD FOR EXTRA SECURITY
def Register():
    if request.method == "POST":
        # GRAB INPUTTED FIELDS
        name = request.form["name"]
        code = request.form["code"]
        username = request.form["username"]
        password = request.form["password"]

        with create_connection() as connection:
            with connection.cursor() as cursor:
                # CHECK IF USERNAME ALREADY EXISTS
                cursor.execute("SELECT * from teachers where username=%s",(username,))
                user = cursor.fetchone()
                if user is None:
                    cursor.execute("INSERT INTO teachers (name,code,username,password) VALUES (%s,%s,%s,%s)",(name,code,username,password)) 
                    connection.commit()
                    return redirect("/")  
                else:
                    pass # CODE THIS LATER
        
    elif request.method == "GET":
        return render_template("register.html")
    
@app.route("/add")
def Add():
    pass

@app.route("/delete")
def Delete():
    pass

@app.route("/edit",methods=["GET","POST"])
def Edit():
    if "user" in session:
        # GET CURRENT DATE
        currentDate = datetime.datetime.now()

        if request.method == "GET":
            # GET ALL NOTICES RELEVANT TO THE DATE
            with create_connection() as connection:
                 with connection.cursor() as cursor:
                      cursor.execute("SELECT * FROM dailynotices WHERE startDate <= %s AND endDate >= %s",(currentDate,currentDate))
                      notices = cursor.fetchall()
            
            return render_template("edit.html",notices=notices)
            
        elif request.method == "POST":
            pass
    else:
        pass # CODE THIS LATER

app.run()