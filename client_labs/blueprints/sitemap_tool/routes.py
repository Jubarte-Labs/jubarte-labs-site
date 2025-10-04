import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from functools import wraps
from werkzeug.utils import secure_filename
from ... import database
from sitemap_tool.main import run_tool_full_process

sitemap_tool_bp = Blueprint('sitemap_tool', __name__, template_folder='templates')

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
    if request.method == "POST":
        # 1. Get form data and files
        supplier_dir = request.form.get('supplier_dir')
        old_sitemap_file = request.files['old_sitemap_file']
        empty_pages_file = request.files['empty_pages_file']
        new_urls_file = request.files.get('new_urls_file') # Optional
        new_sitemap_filename = request.form.get('new_sitemap_filename')

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
        with database.get_db_connection() as client:
            client.execute(
                "INSERT INTO logs (tool_name, input_data, output_data) VALUES (?, ?, ?)",
                ("sitemap_processor", f"Directory: {supplier_dir}", result_string)
            )
        return render_template("sitemap_tool.html", result=result_string)

    return render_template("sitemap_tool.html", result=None)