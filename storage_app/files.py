import uuid
from io import BytesIO

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from .extensions import db
from .models import StoredFile

files = Blueprint("files", __name__)


@files.get("/")
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("files.dashboard"))
    return render_template("landing.html")


@files.get("/dashboard")
@login_required
def dashboard():
    user_files = StoredFile.query.filter_by(user_id=current_user.id).order_by(
        StoredFile.created_at.desc()
    ).all()
    total_size = sum(item.size for item in user_files)
    return render_template(
        "dashboard.html", files=user_files, total_size=total_size
    )


@files.post("/upload")
@login_required
def upload():
    uploaded = request.files.get("file")
    if uploaded is None or not uploaded.filename:
        flash("Choose a file before uploading.", "error")
        return redirect(url_for("files.dashboard"))

    filename = secure_filename(uploaded.filename)
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if not filename or extension not in current_app.config["ALLOWED_EXTENSIONS"]:
        allowed = ", ".join(sorted(current_app.config["ALLOWED_EXTENSIONS"]))
        flash(f"This file type is not allowed. Allowed types: {allowed}.", "error")
        return redirect(url_for("files.dashboard"))

    data = uploaded.read()
    storage_key = f"{current_user.id}/{uuid.uuid4().hex}-{filename}"
    content_type = uploaded.mimetype or "application/octet-stream"
    storage = current_app.extensions["file_storage"]
    try:
        storage.save(data, storage_key, content_type)
        record = StoredFile(
            user_id=current_user.id,
            original_name=filename,
            storage_key=storage_key,
            content_type=content_type,
            size=len(data),
        )
        db.session.add(record)
        db.session.commit()
    except Exception:
        db.session.rollback()
        try:
            storage.delete(storage_key)
        except Exception:
            pass
        current_app.logger.exception("Upload failed")
        flash("The upload failed. Check the storage configuration and try again.", "error")
    else:
        flash(f"{filename} uploaded successfully.", "success")
    return redirect(url_for("files.dashboard"))


@files.get("/files/<int:file_id>/download")
@login_required
def download(file_id):
    record = StoredFile.query.filter_by(id=file_id, user_id=current_user.id).first_or_404()
    data = current_app.extensions["file_storage"].read(record.storage_key)
    return send_file(
        BytesIO(data),
        as_attachment=True,
        download_name=record.original_name,
        mimetype=record.content_type,
    )


@files.post("/files/<int:file_id>/delete")
@login_required
def delete(file_id):
    record = StoredFile.query.filter_by(id=file_id, user_id=current_user.id).first_or_404()
    storage = current_app.extensions["file_storage"]
    try:
        storage.delete(record.storage_key)
        db.session.delete(record)
        db.session.commit()
        flash(f"{record.original_name} deleted.", "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Delete failed")
        flash("The file could not be deleted.", "error")
    return redirect(url_for("files.dashboard"))
