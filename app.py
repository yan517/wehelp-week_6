from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import json

def databaseConn():
    cnx = mysql.connector.connect(user='yan', password='',
                                host='127.0.0.1',
                                database='website')
    return cnx                              

app = Flask(__name__)
app.secret_key="donotguessyouwillbeafraid"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def register():
    name = request.form["name"]
    username = request.form["usrname"]
    pwd = request.form["passwd"]
    if(name and username and pwd):
        check_user_exist = ("SELECT * FROM member WHERE username = %s;")
        usrname = (username,)
        cnx = databaseConn()
        cursor = cnx.cursor()
        cursor.execute(check_user_exist,usrname)
        if (cursor.fetchone() is not None):
            return redirect(url_for("error", message="帳號已經被註冊"))
        else:
            create_user = ("INSERT INTO member "
                           "(name, username, password)"
                           "VALUES (%s, %s, %s);")
            data = (name,username,pwd)     
            cursor.execute(create_user,data)
            cnx.commit()
            cursor.close()
            cnx.close()
            return redirect(url_for("index"))
    else:
        return redirect(url_for("error", message="姓名、帳號、密碼不能空"))

@app.route("/signin", methods=["POST"])
def signIn():
    usrname = request.form["username"]
    passwd = request.form["pwd"]
    if(usrname and passwd):
        check_user_passwd = ("SELECT id, name, follower_count FROM member WHERE BINARY username = %s and BINARY password = %s;")
        data = (usrname,passwd)
        cnx = databaseConn()
        cursor = cnx.cursor()
        cursor.execute(check_user_passwd,data)
        fetchdata = cursor.fetchone()
        if (fetchdata is not None):
            session["login"] = "success"
            session["userProfile"] = fetchdata
            return redirect("/member")
        else:
            session["login"] = "fail"
            return redirect(url_for("error", message="帳號、或密碼輸入錯誤"))
    else:
        session["login"] = "fail"
        return redirect(url_for("error", message="請輸入帳號、密碼"))

@app.route("/member")
def member():
    if (session["login"] == "success"):
        data = getData()
        username = session["userProfile"][1]
        return render_template("member.html", name=username, datum=data)
    return redirect("/")

@app.route("/error")
def error():
    message = request.args.get("message")
    return render_template("error.html", mes=message)

@app.route("/signout")
def signOut():
    session["login"] = "fail"
    session["userProfile"] = ""
    return render_template("index.html")       

@app.route("/message", methods=["POST"])
def addCom():
    comment = request.form["comment"]
    if(comment):
        cnx = databaseConn()
        cursor = cnx.cursor()
        add_comment = ("INSERT INTO message "
                       "(member_id, content)"
                       "VALUES (%s, %s);")
        data = (session["userProfile"][0],comment)
        cursor.execute(add_comment,data) 
        cnx.commit()
        cursor.close()
        cnx.close()   
        return redirect("/member")

def getData():
    if (session["login"] == "success"):
        cnx = databaseConn()
        cursor = cnx.cursor()
        get_commemt = ("SELECT name, content, message.time from message left join member on member.id = message.member_id order by message.time DESC;")
        cursor.execute(get_commemt)
        data = cursor.fetchall()
        cursor.close()
        cnx.close()   
        return data


app.run(port=3000)