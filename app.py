from abc import ABCMeta, abstractmethod
from typing import Any, Union
import pymysql
import datetime
import hashlib
from werkzeug.routing import BaseConverter
from flask import Flask, flash, render_template, request, redirect, session, url_for

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

class SignedIntConverter(BaseConverter):
    regex = r'-?\d+' # REGEX TO ACCOMODATE NEGATIVE AND POSITIVE INTEGERS

    def to_python(self, value: str) -> int:
        return int(value)
    
    def to_url(self, value: int) -> str:
        return str(value)

app.url_map.converters["signedinteger"] = SignedIntConverter

# HASH FUNCTION, TURNS PLAINTEXT INTO A 64 CHARACTER LONG CYPHERTEXT
def hash(hashInput) -> str:
    return hashlib.sha256(hashInput.encode()).hexdigest()

@app.route("/")
def landing():
    return redirect("/index/")

@app.route("/index/", defaults={"dateIndex": 0}) # ALLOW FOR NO PARAMETERS TO BE PASSED
@app.route("/index/<signedinteger:dateIndex>") # TAKE A DATE INDEX AS A PARAMETER TO KEEP TRACK OF CURRENT DISPLAY DATE
def index(dateIndex:int=0):

    try:
        # FIND DESIRED DATE USING A DATE COUNTER
        targetDate = datetime.datetime.now() + datetime.timedelta(days=dateIndex)
    except OverflowError:
        # FLASH ERROR
        flash("Date out of range!")
        return redirect(url_for("index"))
    
    # GET ALL NOTICES RELEVANT TO THE DATE
    with create_connection() as connection:
        with connection.cursor() as cursor:
            # JOIN DAILY NOTICES TABLE AND TEACHERS TABLE USING FOREIGN KEY
            cursor.execute(
                """SELECT 
                    dailynotices.id,
                    dailynotices.name,
                    dailynotices.category,
                    dailynotices.information,
                    dailynotices.startDate,
                    dailynotices.endDate,
                    teachers.code AS teacherCode
                    FROM dailynotices JOIN teachers ON dailynotices.teacherInChargeID = teachers.id
                    WHERE startDate <= %s AND endDate >= %s
                """,
                (targetDate,targetDate)
            )
            notices = cursor.fetchall()
    
    return render_template(
        "index.html",notices=[notices[i:i+3] for i in range(0,len(notices),3)],
        userInSession="user" in session,
        targetDate=targetDate,
        dateIndex=dateIndex
    )

@app.route("/login",methods=["GET","POST"])
def login():

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
        if user and user["password"] == hash(password):
            session["user"] = user["username"]
            return redirect("/")
        else:
            # FLASH ERROR
            flash("Invalid username or password!")
            return redirect(url_for("login"))
    elif request.method == "GET":
        return render_template("login.html",userInSession="user" in session)
    
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")
    
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        with create_connection() as connection:
            with connection.cursor() as cursor:
                # CHECK IF USERNAME ALREADY EXISTS
                cursor.execute("SELECT * from teachers where username=%s",(request.form["username"],))
                user = cursor.fetchone()
                if user is None:
                    cursor.execute(
                        "INSERT INTO teachers (name,code,username,password) VALUES (%s,%s,%s,%s)",
                        [{"name":request.form[i],"code":request.form[i].upper(),"username":request.form[i].lower().replace(" ",""),"password":hash(request.form[i])}[i] for i in ("name","code","username","password")] # LOOP THROUGH FORM AND PASS EACH FIELD AS A PARAMETER, ENCRYPTING PASSWORD
                    ) 
                    connection.commit()
                    return redirect("/login") # MAYBE ADD SYSTEM OF VISIBILITY STATUS
                else:
                    # FLASH ERROR
                    flash("Username already in use!")
                    return redirect(url_for("register"))
        
    elif request.method == "GET":
        return render_template("register.html",userInSession="user" in session)
    
@app.route("/add",methods=["GET","POST"])
def add():
    if "user" in session:
        if request.method == "GET":
            return render_template("add.html",userInSession="user" in session)
        elif request.method == "POST":
            with create_connection() as connection:
                with connection.cursor() as cursor:
                    # GET USER ID
                    cursor.execute("SELECT id FROM teachers where username=%s",(session["user"],))
                    userID = cursor.fetchone()["id"]

                    # ADD NEW DAILY NOTICE
                    cursor.execute(
                        "INSERT INTO dailynotices (name,category,information,startDate,endDate,teacherInChargeID) VALUES (%s,%s,%s,%s,%s,%s)",
                        [request.form[i] for i in ("name","category","info","startDate","endDate")]+[userID]
                    )
                    connection.commit()

                    return redirect("/")
    else:
        # FLASH ERROR
        flash("You aren't logged in!")
        return redirect(url_for("index"))

@app.route("/delete/<int:noticeID>",methods=["GET","POST"])
def delete(noticeID:int):
    if "user" in session:
        # DELETE DAILY NOTICE FROM PASSED ID
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM dailynotices WHERE id=%s",(noticeID,))
                connection.commit()
        return redirect("/edit")
    else:
        # FLASH ERROR
        flash("You aren't logged in!")
        return redirect(url_for("index"))

@app.route("/edit/", defaults={"dateIndex": 0}, methods=["GET","POST"]) # ALLOW FOR NO PARAMETERS TO BE PASSED
@app.route("/edit/<signedinteger:dateIndex>", methods=["GET","POST"]) # TAKE A DATE INDEX AS A PARAMETER TO KEEP TRACK OF CURRENT DISPLAY DATE
def edit(dateIndex:int=0):
    if "user" in session:

        try:
            # FIND DESIRED DATE USING A DATE COUNTER
            targetDate = datetime.datetime.now() + datetime.timedelta(days=dateIndex)
        except OverflowError:
            # FLASH ERROR
            flash("Date out of range!")
            return redirect(url_for("index"))

        if request.method == "GET":
            # GET ALL NOTICES RELEVANT TO THE DATE
            with create_connection() as connection:
                 with connection.cursor() as cursor:
                      cursor.execute("SELECT * FROM dailynotices WHERE startDate <= %s AND endDate >= %s",(targetDate,targetDate))
                      notices = cursor.fetchall()
            
            return render_template(
                "edit.html",notices=[notices[i:i+2] for i in range(0,len(notices),2)],
                userInSession="user" in session,
                targetDate=targetDate,
                dateIndex=dateIndex
            )
            
        elif request.method == "POST":
            # LOOP THROUGH ALL FIELDS IN FORM
            for field in request.form:
                if field.startswith("name_"):
                    # GET ID
                    noticeID = field.split("_")[1]

                    # UPDATE CORRESPONDING ROW
                    with create_connection() as connection:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE dailynotices SET name=%s, category=%s, information=%s, startDate=%s, endDate=%s WHERE id=%s",
                                [request.form[f"{i}_{noticeID}"] for i in ("name","category","info","startDate","endDate")]+[noticeID]
                            )
                            connection.commit()
            return redirect("/")
    else:
        # FLASH ERROR
        flash("You aren't logged in!")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run()