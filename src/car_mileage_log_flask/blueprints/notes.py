from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_wtf import FlaskForm
from sqlalchemy import select
from wtforms import TextAreaField
from wtforms.validators import DataRequired

from car_mileage_log_flask.blueprints.auth import login_required
from car_mileage_log_flask.db.connection import Session
from car_mileage_log_flask.db.models import Note

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")


class NoteForm(FlaskForm):
    text = TextAreaField("Text", validators=[DataRequired()])


@notes_bp.get("/")
@login_required
def index():
    with Session() as session:
        notes = session.scalars(
            select(Note).order_by(Note.created_at.desc(), Note.id.desc())
        ).all()

    return render_template("notes/index.html", notes=notes)


@notes_bp.get("/<int:id>")
@login_required
def details(id: int):
    with Session() as session:
        note = session.get(Note, id)
        if note is None:
            abort(404)

        return render_template("notes/details.html", note=note)


@notes_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = NoteForm()

    if form.validate_on_submit():
        with Session() as session:
            session.add(Note(text=form.text.data))
            session.commit()

        flash("Note created", "success")
        return redirect(url_for("notes.index"))

    return render_template("notes/new.html", form=form)


@notes_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id: int):
    with Session() as session:
        note = session.get(Note, id)
        if note is None:
            abort(404)

        form = NoteForm(obj=note)

        if form.validate_on_submit():
            form.populate_obj(note)
            session.commit()

            flash("Note updated", "success")
            return redirect(url_for("notes.index"))

        return render_template("notes/edit.html", form=form, note=note)


@notes_bp.post("/<int:id>/delete")
@login_required
def delete(id: int):
    with Session() as session:
        note = session.get(Note, id)
        if note is None:
            abort(404)

        session.delete(note)
        session.commit()

    flash("Note deleted", "success")
    return redirect(url_for("notes.index"))
