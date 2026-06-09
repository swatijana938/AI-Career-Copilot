import email
from unittest import result

from flask import Flask, render_template, request, redirect, session
from ai import analyze_resume
from db import Base, engine, sessionLocal
import db
import models
import PyPDF2
import docx
import json

Base.metadata.create_all(bind=engine)


app = Flask(__name__)
app.secret_key="secret123"

#HOME

@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

#-----SIGNUP

@app.route("/signup", methods=["GET", "POST"])
def signup():
    db = sessionLocal()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = db.query(models.User).filter_by(email=email).first()

        if existing_user:
            return "User already exists"

        user = models.User(email=email, password=password)
        db.add(user)
        db.commit()

        return redirect("/login")

    return render_template("signup.html")

#-----LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    db = sessionLocal()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.query(models.User).filter_by(email=email, password=password).first()

        if user:
            session["user"] = user.email
            return redirect("/dashboard")
        else:
            return "Invalid credentials"

    return render_template("login.html")

#----FORGOT PASSWORD
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    return render_template("forgot_password.html")

#----DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":
        user_goal = request.form.get("role")
        resume_text = request.form.get("resume")

        file = request.files.get("file")


        #file handling

    if file and file.filename != "":

           if file.filename.endswith(".pdf"):
               try:
                 pdf_reader = PyPDF2.PdfReader(file)
                 text = ""

                 for page in pdf_reader.pages:
                     text += page.extract_text() or ""
 
                     resume_text = text

               except Exception as e:
                result = {"error": f"PDF error: {str(e)}"}

    elif file.filename.endswith(".docx"):
        try:
            doc = docx.Document(file)
            text = ""

            for para in doc.paragraphs:
                text += para.text + "\n"

            resume_text = text

        except Exception as e:
            result = {"error": f"Docx error: {str(e)}"}

    if resume_text and user_goal:
        try:
            result = analyze_resume(resume_text, user_goal)
        
            db = sessionLocal()
            user = db.query(models.User).filter_by(email=session["user"]).first()
            report = models.User.Reports(user_id=user.id, resume_text=resume_text, results=json.dumps(result))
            db.add(report)
            db.commit()

        except Exception as e:
            result = {"error": f"AI error: {str(e)}"}

    

    return render_template(
        "dashboard.html",
        user=session["user"],
        result=result
    )
#history
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")
    db = sessionLocal()
    user = db.query(models.User).filter_by(email=session["user"]).first()
    reports = db.query(models.User.Reports).filter_by(user_id=user.id).all()
    #convert JSON string back to dict

    passed_reports = []
    for r in reports:
        try:
            passed_result = json.loads(r.results)

        except:
            passed_result = {"error": "Invalid JSON"}

        passed_reports.append({
            "resume_text": r.resume_text,
            "result": passed_result
        })

    return render_template("history.html", reports=passed_reports)

#logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)