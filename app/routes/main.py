from flask import Blueprint, flash, redirect, render_template, request, session
from sqlalchemy.orm import clear_mappers
from app.models import db, User
from sqlalchemy import inspect
from app.helper import apology, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from twilio.rest import Client
import json
from tkinter import * 
from tkinter.ttk import *

main = Blueprint("main", __name__)  # initialize blueprint

@main.route("/")
def index(): 
    return render_template("index.html")

@main.route("/message", methods=["GET","POST"])
def message():
    session.clear()
    if request.method == "POST":
        if not request.form.get("recipient_phone"):
            return apology("must provide phone number")
        elif not request.form.get("message"):
             return apology("must provide a message")

        twilio_sid = "AC7e0d1d4fc254d789473b7f8229ffa74e"
        twilio_secret = "fd26b688d7108fdb71620b593e9e9df2"        
        client = Client(twilio_sid, twilio_secret)

        my_phone = +17313180503
        recipient_phone = request.form.get("recipient_phone")
        send_sms = request.form.get("message")
        client.messages.create(body=send_sms,from_=my_phone, to=recipient_phone)

        return redirect("/message")
    else:
        return render_template("message.html")
    

@main.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()
    if request.method == "POST":
        # form check
        if not request.form.get("phone"):
            return apology("must provide username")
        elif not request.form.get("password"):
            return apology("must provide password")

        phone = request.form.get("phone")
        password = request.form.get("password")

        user = db.session.query(User).filter_by(phone=phone).one_or_none()

        if user is None:
            return apology("please check phone number or password")
        
        if not check_password_hash(user.hashed_password, password):
            return apology("please check phone number or password")

        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")
    else:
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

        return redirect("/login") 
    else: 
        return render_template("register.html")


