import os
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.secret_key = os.getenv("FLASK_SECRET_KEY")

@app.route("/")
def index():
    """A simple index route."""
    return "<h1>Client Labs</h1>"

if __name__ == "__main__":
    app.run(debug=True)