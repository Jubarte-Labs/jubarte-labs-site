import os
from flask import Flask, render_template
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.secret_key = os.getenv("FLASK_SECRET_KEY")

@app.route("/")
def index():
    """Renders the dashboard page."""
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
