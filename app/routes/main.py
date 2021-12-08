import json
import os

from app.helper import apology, login_required
from app.models import User, db
from flask import Blueprint, flash, redirect, render_template, request, session
from sqlalchemy import inspect
from sqlalchemy.orm import clear_mappers
from twilio.rest import Client
from werkzeug.security import check_password_hash, generate_password_hash

main = Blueprint("main", __name__)  # initialize blueprint
twilio_sid = "AC7e0d1d4fc254d789473b7f8229ffa74e"
twilio_secret = "6350511dc5f11c56fcc24d77d53ae36a" 

@main.route("/")
def index(): 
    if not session.get("user_id"):
        return render_template("index.html")
    return redirect('/message')

@main.route("/message", methods=["GET","POST"])
@login_required
def message():
    if request.method == "POST":
        if not request.form.get("recipient_phone"):
            return apology("must provide phone number")
        if not request.form.get("recipient_phone").isdecimal():
            return apology("must be real number")
        elif not request.form.get("message"):
             return apology("must provide a message")

        client = Client(twilio_sid, twilio_secret)

        my_phone = '+17313180503'
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
        for s in phone:
            if not s.isdigit():
                return apology ("must be real number")
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

@main.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    return redirect("/")

@main.route("/past")
@login_required
def past():
    client = Client(twilio_sid, twilio_secret)

    messages = client.messages.list(limit=8)

    x = []
    
    for record in messages:
        d = dict()
        d['body'] = record.body.split(' - ')[1]
        d['to'] = record.to
        x.append(d)
    print(x)
    
    return render_template('past.html', messages=x)