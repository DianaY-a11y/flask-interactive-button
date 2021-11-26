import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)
app.secret_key = "super secret key"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Float, default=10000, nullable=False)

    stocks = db.relationship('Stock', backref="user", lazy=True)
    transactions = db.relationship('Transaction', backref="user", lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username

class Stock(db.Model):
    __tablename__ = "stock"
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Transaction(db.Model):
    __tablename__ = "transaction"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    ticker = db.Column(db.String(128), nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
 

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    uid = session['user_id']
    user = db.session.query(User).get(uid)

    stocks = user.stocks
    formatted_stocks = []

    # fetch latest data about the stocks
    for s in stocks:
        f_s = {}
        quote = lookup(s.ticker)
        f_s['symbol'] = s.ticker
        f_s['name'] = quote['name']
        f_s['volume'] = s.volume
        f_s['price'] = quote['price']
        f_s['total'] = quote['price'] * s.volume
        formatted_stocks.append(f_s)

    stock_worth = 0.0
    for s in formatted_stocks:
        stock_worth += s['total']

    net_worth = stock_worth + user.balance

    return render_template("index.html", stocks=formatted_stocks, balance=user.balance, net_worth=net_worth)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        num_of_shares = request.form.get("shares")

        if symbol is None:
            return apology("Please enter valid value")
        if num_of_shares is None or int(num_of_shares) < 1:
            return apology("Invalid amount of shares")
        num_of_shares = int(num_of_shares)

        quote = lookup(symbol)
        current_price = quote['price']

        # 1) check user balance, and subtract total amt from user balance
        uid = session['user_id']
        user = db.session.query(User).get(uid)

        trx_amount = current_price * float(num_of_shares)
        if user.balance < trx_amount:
            return apology("You're broke")

        user.balance = user.balance - trx_amount
        db.session.commit()

        new_transaction = Transaction(
            user_id=uid,
            ticker=quote['symbol'],
            volume=num_of_shares,
            price=current_price
        )

        db.session.add(new_transaction)
        db.session.commit()

        # 2) create a new stock in stock table
        for s in user.stocks:
            # find if user has brought stock
            if s.ticker == symbol:
                s.volume += num_of_shares
                db.session.commit()
                return render_template("buy.html", bought=True)

        new_stock = Stock(
            user_id=uid, 
            ticker=quote['symbol'],
            volume=num_of_shares, 
        )
        db.session.add(new_stock)
        db.session.commit()
        return render_template("buy.html", bought=True)
        
    return render_template("buy.html", bought=False)
        


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    uid = session['user_id']
    user = db.session.query(User).get(uid)

    transactions = user.transactions

    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()
    if request.method == "POST":
        # form check
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        username = request.form.get("username")
        password = request.form.get("password")

        user = db.session.query(User).filter_by(username=username).one_or_none()

        if user is None:
            return apology("please check username or password", 403)
        
        if not check_password_hash(user.hashed_password, password):
            return apology("please check username or password", 403)

        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if symbol is None:
            return apology("Please enter valid value", 403)

        quote = lookup(symbol)

        if quote is None:
            return apology("Invlaid symbol. Please try again")

        return render_template("quoted.html", quote=quote, usd_convert = usd)

    return render_template("quote.html")
    


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # require user input username 
    if request.method == "POST":
        data = request.form.to_dict(flat = True)
        password = data['password']
        username = data['username']
        confirm = data['confirmation']

        if password is None:
            return apology("provide a password")
        if confirm is None:
            return apology("provide a confirm")
        if username is None:
            return apology("provide a username")
        if password != confirm:
            return apology("must provide password that matches confirmation password")
         
        hash = generate_password_hash(password)
        new_user = User(username=username, hashed_password=hash)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/')
    else: 
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    uid = session['user_id']
    user = db.session.query(User).get(uid)

    stocks = set()
    for s in user.stocks:
        stocks.add(s.ticker)

    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        num_of_shares = request.form.get("shares")

        if symbol is None:
            return apology("Please enter valid value")
        if num_of_shares is None or int(num_of_shares) < 1:
            return apology("Invalid amount of shares")
        num_of_shares = int(num_of_shares)

        for s in user.stocks:
            if s.ticker == symbol:
                if s.volume < num_of_shares:
                    return apology("You don't have enough volume")

                s.volume -= num_of_shares
                db.session.commit()

                if s.volume < 1:
                    db.session.query(Stock).filter_by(id=s.id).delete()
                    db.session.commit()

                quote = lookup(symbol)
                current_price = quote['price']
                user.balance += current_price * num_of_shares
                db.session.commit()

                new_transaction = Transaction(
                    user_id=uid,
                    ticker=quote['symbol'],
                    volume=(-num_of_shares),
                    price=current_price
                )

                db.session.add(new_transaction)
                db.session.commit()
                
                return render_template("sell.html", stocks=stocks, sold=True)
                    
        
        return apology("You don't own this stock")


    return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == '__main__':
    # Make sure API key is set
    if not os.environ.get("API_KEY"):
        raise RuntimeError("API_KEY not set")

    # Ensure templates are auto-reloaded
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.jinja_env.filters["usd"] = usd
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"

    app.run(debug=True) 