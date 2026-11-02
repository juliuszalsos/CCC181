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

# In-memory storage baseline from Week 3 (prior to Part 7 persistence refactoring)
TICKETS = []
SERVICES = {
    1: {"id": 1, "name": "Birth certificate", "avg_minutes": 10},
    2: {"id": 2, "name": "Marriage certificate", "avg_minutes": 10},
    3: {"id": 3, "name": "Death certificate", "avg_minutes": 10},
    4: {"id": 4, "name": "PhilSys National ID", "avg_minutes": 15},
}
ACTIVE_STATUSES = ("waiting", "called")
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


@app.template_filter("local")
def local_time(value):
    """Show a timestamp in Philippine time, e.g. Oct 26, 08:01 AM."""
    return value.astimezone(PH_TIME).strftime("%b %d, %I:%M %p") if value else ""


@app.route("/")
def index():
    called = [t for t in TICKETS if t.get("status") == "called"]
    waiting = [t for t in TICKETS if t.get("status") == "waiting"]
    mine_id = session.get("ticket_id")
    mine = next((t for t in TICKETS if t["id"] == mine_id), None) if mine_id else None
    if mine and mine.get("status") not in ACTIVE_STATUSES:
        mine = None

    return render_template(
        "index.html",
        called=called,
        waiting=waiting,
        services=SERVICES,
        mine=mine,
    )


@app.get("/join")
def join_form():
    return render_template("join.html", services=list(SERVICES.values()), form={})


@app.post("/join")
def join():
    form = request.form
    name = form.get("name", "").strip()
    email = form.get("email", "").strip().lower()
    service_id = form.get("service_id", type=int)

    errors = {}
    if not name or len(name) > 80:
        errors["name"] = "Enter your name (up to 80 characters)."
    if not EMAIL_PATTERN.fullmatch(email) or len(email) > 120:
        errors["email"] = "Enter a valid email address."
    if service_id not in SERVICES:
        errors["service_id"] = "Choose a service."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return (
            render_template(
                "join.html", services=list(SERVICES.values()), form=form, errors=errors
            ),
            400,
        )

    ticket_id = len(TICKETS) + 1
    ticket = {
        "id": ticket_id,
        "name": name,
        "email": email,
        "service_id": service_id,
        "status": "waiting",
        "created_at": datetime.now(PH_TIME),
    }
    TICKETS.append(ticket)
    session["ticket_id"] = ticket_id
    flash(f"You joined the queue. Your ticket is #{ticket_id}.", "success")
    return redirect(url_for("ticket", ticket_id=ticket_id))


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = next((t for t in TICKETS if t["id"] == ticket_id), None)
    if not t:
        abort(404)
    service = SERVICES.get(t["service_id"])
    return render_template("ticket.html", ticket=t, service=service)


@app.get("/staff")
def staff_dashboard():
    return render_template("staff.html", queue=TICKETS, services=list(SERVICES.values()))


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