from flask import Flask, render_template, redirect, request, url_for, flash, abort
from config import config
from flask_mysqldb import MySQL
from models.ModelUsers import ModelUsers
from models.entities.users import User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps

app = Flask(__name__)
db = MySQL(app)
login_manager_app = LoginManager(app)
login_manager_app.login_view = "login"  # Set the login view for redirects

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # Verify if the user is authenticated and is an administrator
        if not current_user.is_authenticated or current_user.usertype != 1:
            abort(403)  # Forbidden access
        return func(*args, **kwargs)
    return decorated_view

@app.route("/")
def index():
    return redirect(url_for("login"))  # Use url_for for better maintainability

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User(0, request.form['username'], request.form['password'], 0)
        logged_user = ModelUsers.login(db, user)
        if logged_user != None:
            login_user(logged_user)
            if logged_user.usertype == 1:
                flash("Acceso a administrador otorgado...", "warning")
                return redirect(url_for("admin"))
            else:
                flash("Acceso a usuario otorgado...", "success")
                return redirect(url_for("home"))
        else:
            flash("Acceso rechazado...", "danger")
            return render_template("auth/login.html")
    else:
        return render_template("auth/login.html")

@app.route("/home")
@login_required
def home():
    return render_template("home.html")

@app.route("/admin")
@login_required
@admin_required
def admin():
    return render_template("admin.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@login_manager_app.user_loader
def load_user(id):
    return ModelUsers.get_by_id(db, id)

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()