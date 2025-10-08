import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from functools import wraps
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from ... import database
from sitemap_tool.main import run_tool_full_process

sitemap_tool_bp = Blueprint('sitemap_tool', __name__, template_folder='templates')

class SitemapToolForm(FlaskForm):
    job_name = StringField('Job Name', validators=[DataRequired()])
    old_sitemap_file = FileField('Old Sitemap File', validators=[FileRequired(), FileAllowed(['xml'], 'XML files only!')])
    empty_pages_file = FileField('Empty Pages File', validators=[FileRequired(), FileAllowed(['txt'], 'Text files only!')])
    new_urls_file = FileField('New URLs File (Optional)', validators=[FileAllowed(['txt'], 'Text files only!')])
    new_sitemap_filename = StringField('New Sitemap Filename', validators=[DataRequired()])
    submit = SubmitField('Process Sitemap')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@sitemap_tool_bp.route("/tools/sitemap-processor", methods=["GET", "POST"])
@login_required
def sitemap_processor():
    form = SitemapToolForm()
    if form.validate_on_submit():
        # 1. Get form data and files
        job_name = form.job_name.data
        old_sitemap_file = form.old_sitemap_file.data
        empty_pages_file = form.empty_pages_file.data
        new_urls_file = form.new_urls_file.data
        new_sitemap_filename = form.new_sitemap_filename.data

        # 2. Create a unique, secure directory for this job
        job_id = str(uuid.uuid4())
        upload_path = os.path.join(current_app.root_path, 'uploads', job_id)
        os.makedirs(upload_path, exist_ok=True)

        # 3. Save uploaded files
        old_sitemap_filename_s = secure_filename(old_sitemap_file.filename)
        empty_pages_filename_s = secure_filename(empty_pages_file.filename)
        old_sitemap_file.save(os.path.join(upload_path, old_sitemap_filename_s))
        empty_pages_file.save(os.path.join(upload_path, empty_pages_filename_s))

        new_urls_filename_s = None
        if new_urls_file:
            new_urls_filename_s = secure_filename(new_urls_file.filename)
            new_urls_file.save(os.path.join(upload_path, new_urls_filename_s))

        # 4. Call the tool's main function
        result_string = run_tool_full_process(
            supplier_dir_absolute=upload_path,
            old_sitemap_filename=old_sitemap_filename_s,
            empty_pages_filename=empty_pages_filename_s,
            new_sitemap_filename=secure_filename(new_sitemap_filename),
            new_urls_filename=new_urls_filename_s
        )

        # 5. Log and render result
        log_input_data = (
            f"Job ID: {job_id}, "
            f"Job Name: {job_name}, "
            f"Old Sitemap: {old_sitemap_filename_s}, "
            f"Empty Pages: {empty_pages_filename_s}, "
            f"New URLs: {new_urls_filename_s}"
        )
        with database.get_db_connection() as client:
            client.execute(
                "INSERT INTO logs (tool_name, input_data, output_data) VALUES (?, ?, ?)",
                ("sitemap_processor", log_input_data, result_string)
            )
        return render_template("sitemap_tool.html", form=form, result=result_string)

    return render_template("sitemap_tool.html", form=form, result=None)