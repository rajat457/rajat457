from flask import Flask, render_template, redirect, url_for, flash, request, abort
from functools import wraps
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"


login_manager = LoginManager()
login_manager.init_app(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tbt.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    phone = db.Column(db.String(100), unique = True)


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    

db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template("index.html", current_user = current_user)


@app.route('/login', methods = ["POST", "GET"])
def login():
    form = True
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get('password')
        user = User.query.filter_by(email = email).first()
        if user==None:
            return render_template('login.html', login_error_message = "That email does not exist, please try again!!", signup_error_message = '')
        else:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                return render_template('login.html', login_error_message = "The password is incorrect, please try again!!", signup_error_message = '')
    return render_template("login.html")

@app.route('/signup', methods = ["POST"])
def signup():
    form = True
    if request.method == "POST":
        if form:
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get('password')
            phone = request.form.get("phone")


            user = User.query.filter_by(email = email).first()
            if user == None:
              user2 = User.query.filter_by(phone = phone).first()
              if user2 == None:
                hash_pass = generate_password_hash(password = password, method='pbkdf2:sha256', salt_length=8)
                new_user = User(email = email, password = hash_pass, name = name, phone = phone)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('home'))
              else:
                return render_template('login.html', login_error_message = '', signup_error_message = "That phone number already exists!!")
            else:
                return render_template('login.html', login_error_message = '', signup_error_message = "You've already signed up with that email, please login instead!!")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/products")
def products():
    return render_template("products.html", current_user = current_user)


@app.route("/contact", methods = ['POST', "GET"])
def contact():
    # message = "Contact Me"
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    message = request.form.get("message")

    if request.method == "POST":
        new_user = Message(email = email, name = name, phone = phone, message = message)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template("contact.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)