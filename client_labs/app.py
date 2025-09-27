import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Point static folder to the root 'assets' directory
app = Flask(__name__, static_folder='../assets', static_url_path='/assets')

# Configuration
app.secret_key = os.getenv("FLASK_SECRET_KEY")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():
    """Renders the dashboard page."""
    return render_template("dashboard.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login."""
    if request.method == "POST":
import hmac
# ...
        if hmac.compare_digest(username, os.getenv("APP_USERNAME")) and hmac.compare_digest(password, os.getenv("APP_PASSWORD")):
        password = request.form["password"]
        if username == os.getenv("APP_USERNAME") and password == os.getenv("APP_PASSWORD"):
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials")
            return render_template("login.html")
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Logs the user out."""
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/protected")
@login_required
def protected():
    """Renders the protected page."""
    return render_template("protected.html")

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
