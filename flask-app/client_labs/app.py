import os
import hmac
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, Blueprint
from .auth import login_required, RegistrationForm, LoginForm
from .tools import word_count
from werkzeug.security import generate_password_hash, check_password_hash
from . import database
from .database import init_db_command
from .blueprints.sitemap_tool.routes import sitemap_tool_bp
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.cli.add_command(init_db_command)

# --- Blueprints --- 

# Blueprint for client-specific static files (CSS)
client_labs_bp = Blueprint('client_labs', __name__,
                           static_folder='static', static_url_path='/client_labs/static')
app.register_blueprint(client_labs_bp)

# Blueprint for shared, main-site assets (logo, main CSS)
main_assets_bp = Blueprint('main_assets', __name__, 
                           static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'main-site', 'assets')),
                           static_url_path='/assets')
app.register_blueprint(main_assets_bp)

# Register other functional blueprints
app.register_blueprint(sitemap_tool_bp)


# --- App Configuration ---

app.config.from_object('config.DevelopmentConfig')
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=app.config.get('GOOGLE_CLIENT_ID'),
    client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

def setup_app(app):
    # Initialize database
    with app.app_context():
        database.init_db()

@app.before_request
def load_logged_in_user():
    """If a user id is in the session, load the user object from
    the database into g.user."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        with database.get_db_connection() as client:
            result_set = client.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = result_set.rows[0] if result_set.rows else None
            g.user = dict(zip(result_set.columns, user)) if user else None

# --- Routes ---
@app.route("/")
@login_required
def index():
    """Renders the dashboard page."""
    return render_template("dashboard.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Handles user login."""
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        with database.get_db_connection() as client:
            result_set = client.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = result_set.rows[0] if result_set.rows else None

        if user and user[4] and check_password_hash(user[4], password):
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        with database.get_db_connection() as client:
            result_set = client.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = result_set.rows[0] if result_set.rows else None

            if user:
                flash('Email address already exists')
                return redirect(url_for('register'))

            client.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, generate_password_hash(password))
            )

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login/google')
def google_login():
    """Redirects to Google's authorization page."""
    redirect_uri = url_for('google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def google_authorize():
    """Handles the callback from Google."""
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.parse_id_token(token, nonce=session.get('nonce'))

    google_id = user_info['sub']
    email = user_info['email']
    name = user_info.get('name')

    with database.get_db_connection() as client:
        result_set = client.execute("SELECT * FROM users WHERE google_id = ?", (google_id,))
        user = result_set.rows[0] if result_set.rows else None

        if user is None:
            client.execute(
                "INSERT INTO users (google_id, email, name) VALUES (?, ?, ?)",
                (google_id, email, name)
            )
            result_set = client.execute("SELECT * FROM users WHERE google_id = ?", (google_id,))
            user = result_set.rows[0] if result_set.rows else None

    # Store the user's ID in the session
    session['user_id'] = user[0] # The user's ID is the first column

    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    """Logs the user out."""
    session.pop("user_id", None)
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
        logs = [dict(zip([d.name for d in result_set.column_descriptions], row)) for row in result_set.rows]
        columns = [d.name for d in result_set.column_descriptions]
        logs = [dict(zip(columns, row)) for row in result_set.rows]
    
    return render_template("logs.html", logs=logs)

if __name__ == "__main__":
    setup_app(app)
    app.run(debug=app.config['DEBUG'])