from flask import Blueprint, flash, redirect, render_template, request, session
from app.models import db, User
from sqlalchemy import inspect
from app.helper import apology, login_required
from werkzeug.security import check_password_hash, generate_password_hash


main = Blueprint("main", __name__)  # initialize blueprint

@main.route("/")
def index(): 
    return render_template("index.html")

@main.route("/login", methods=["GET", "POST"])
def login():
        return render_template("login.html")

@main.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # require user input username 
    if request.method == "POST":
        data = request.form.to_dict(flat = True)
        phone = data['phone']
        password = data['password']
        name = data['name']
        confirm = data['confirmation']

        if phone is None:
            return apology("provide a phone")
        if password is None:
            return apology("provide a password")
        if confirm is None:
            return apology("provide a confirm")
        if name is None:
            return apology("provide a name")
        if password != confirm:
            return apology("must provide password that matches confirmation password")

        hash = generate_password_hash(password)
        new_user = User(name=name, phone=phone, hashed_password=hash)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/')
    else: 
        return render_template("register.html")


