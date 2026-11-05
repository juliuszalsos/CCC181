"""QueuExpress: a queue tracker for the PSA Iligan City office.

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
import os
import re
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

from models import Service, Ticket, User, db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = os.environ.get("SQLALCHEMY_ECHO") == "1"

# Part 3 & 4: Database & Migration setup
db.init_app(app)
migrate = Migrate(app, db)

# Philippine Timezone (UTC+8)
PH_TIME = timezone(timedelta(hours=8))

ACTIVE_STATUSES = ("waiting", "called")
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


# Part 6: Read services from database helper
def all_services():
    """Retrieve all available service categories from PostgreSQL."""
    return db.session.scalars(db.select(Service).order_by(Service.name)).all()


@app.template_filter("local")
def local_time(value):
    """Show a timestamp in Philippine time, e.g. Oct 26, 08:01 AM."""
    return value.astimezone(PH_TIME).strftime("%b %d, %I:%M %p") if value else ""


@app.route("/")
def index():
    services = {s.id: s.name for s in all_services()}
    mine_id = session.get("ticket_id")
    mine = db.session.get(Ticket, mine_id) if mine_id else None
    if mine and mine.status not in ACTIVE_STATUSES:
        mine = None

    return render_template(
        "index.html",
        called=[],
        waiting=[],
        services=services,
        mine=mine,
    )


# Part 7: Join Queue with PostgreSQL Persistence
@app.get("/join")
def join_form():
    return render_template("join.html", services=all_services(), form={})


@app.post("/join")
def join():
    form = request.form
    name = form.get("name", "").strip()
    email = form.get("email", "").strip().lower()
    service_id = form.get("service_id", type=int)
    service = db.session.get(Service, service_id) if service_id else None

    is_priority = bool(form.get("is_priority"))
    copies_requested = form.get("copies_requested", 1, type=int)

    errors = {}
    if not name or len(name) > 80:
        errors["name"] = "Enter your name (up to 80 characters)."
    if not EMAIL_PATTERN.fullmatch(email) or len(email) > 120:
        errors["email"] = "Enter a valid email address."
    if service is None:
        errors["service_id"] = "Choose a service."
    if copies_requested < 1 or copies_requested > 5:
        errors["copies_requested"] = "Copies requested must be between 1 and 5."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return (
            render_template(
                "join.html", services=all_services(), form=form, errors=errors
            ),
            400,
        )

    # Find existing user by email or instantiate a new User
    user = db.session.scalar(db.select(User).filter_by(email=email))
    if user is None:
        user = User(name=name, email=email)
    else:
        user.name = name  # Update existing user's display name if changed

    # Instantiate Ticket connected to User & Service
    ticket = Ticket(
        user=user,
        service=service,
        is_priority=is_priority,
        copies_requested=copies_requested,
    )
    db.session.add(ticket)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Something went wrong saving your ticket. Please try again.", "danger")
        return (
            render_template(
                "join.html", services=all_services(), form=form, errors={}
            ),
            409,
        )

    session["ticket_id"] = ticket.id
    flash(f"You joined the queue. Your ticket is #{ticket.id}.", "success")
    return redirect(url_for("ticket", ticket_id=ticket.id))


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    return render_template("ticket.html", ticket=t, service=t.service)


@app.get("/staff")
def staff_dashboard():
    return render_template("staff.html", queue=[], services=all_services())


@app.route("/hello")
def hello():
    return "Hello, QueuExpress!"


# Part 5: Database Seed Command
@app.cli.command("seed")
def seed():
    """Add the starting services if they are not there yet."""
    starting = [
        ("Birth certificate", 10),
        ("Marriage certificate", 10),
        ("Death certificate", 10),
        ("PhilSys National ID", 15),
    ]
    for name, minutes in starting:
        exists = db.session.scalar(db.select(Service).filter_by(name=name))
        if exists is None:
            db.session.add(Service(name=name, avg_minutes=minutes))
    db.session.commit()
    print("Services are ready.")


if __name__ == "__main__":
    app.run(debug=True)