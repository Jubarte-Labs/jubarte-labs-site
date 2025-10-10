import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("--- STARTING APP ---")
print(f"DEBUG: TURSO_DATABASE_URL is set to: {os.getenv('TURSO_DATABASE_URL')}")
# For security, we just check if the token exists, not its value.
print(f"DEBUG: TURSO_AUTH_TOKEN is set: {'Yes' if os.getenv('TURSO_AUTH_TOKEN') else 'No, this is the problem!'}")
print("--------------------")

import hmac
from flask import Flask, render_template, request, redirect, url_for, session, flash
from .tools import word_count
from . import database
from .blueprints.sitemap_tool.routes import sitemap_tool_bp
from .auth import login_required, LoginForm

def create_app():
    # Point static folder to the root 'assets' directory
    app = Flask(__name__, static_folder='../assets', static_url_path='/assets')

    # Configuration
    app.secret_key = os.getenv("FLASK_SECRET_KEY")
    app.config["WTF_CSRF_ENABLED"] = os.getenv("WTF_CSRF_ENABLED", "True").lower() in ['true', '1', 't']

    # Initialize database
    with app.app_context():
        database.init_db()

    # Register blueprints
    app.register_blueprint(sitemap_tool_bp)

    # --- Routes ---
    @app.route("/")
    @login_required
    def index():
        """Renders the dashboard page."""
        return render_template("dashboard.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Handles user login."""
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            # Note: Using hmac.compare_digest for security
            if hmac.compare_digest(username, os.getenv("APP_USERNAME")) and \
               hmac.compare_digest(password, os.getenv("APP_PASSWORD")):
                session['logged_in'] = True
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials', 'danger')
        return render_template('login.html', form=form)

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

    @app.route("/tool-1", methods=["GET", "POST"])
    @login_required
    def tool_1():
        """Renders the tool_1 page and handles form submission."""
        if request.method == "POST":
            text = request.form.get("text_input")
            result = word_count(text)

            # Log the interaction
            with database.get_db_connection() as client:
                client.execute(
                    "INSERT INTO logs (tool_name, input_data, output_data) VALUES (?, ?, ?)",
                    ("word_count", text, str(result))
                )

            return render_template("tool_1.html", result=result, text_input=text)
        return render_template("tool_1.html", result=None, text_input="")

    @app.route("/logs")
    @login_required
    def logs():
        """Displays all logs from the database."""
        with database.get_db_connection() as client:
            result_set = client.execute("SELECT * FROM logs ORDER BY timestamp DESC")
            # Convert rows to a list of dictionaries
            columns = [d.name for d in result_set.column_descriptions]
            logs = [dict(zip(columns, row)) for row in result_set.rows]

        return render_template("logs.html", logs=logs, columns=columns)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")