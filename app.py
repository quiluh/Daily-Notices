import pymysql
from flask import Flask, render_template, request, redirect
app = Flask(__name__)

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