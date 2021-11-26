from flask import Blueprint, flash, redirect, render_template, request, session
from app.models import db 
from sqlalchemy import inspect
from app.helper import apology, login_required

main = Blueprint("main", __name__)  # initialize blueprint

@main.route("/")
def index(): 
    return render_template("index.html")

@main.route("/login")
def login(): 
    return render_template("login.html")

@main.route("/signup")
def signup(): 
    return render_template("signup.html")


