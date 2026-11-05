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
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from models import Service, Ticket, User, db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = os.environ.get("SQLALCHEMY_ECHO") == "1"

db.init_app(app)
migrate = Migrate(app, db)

# Philippine Timezone (UTC+8)
PH_TIME = timezone(timedelta(hours=8))


@app.template_filter("local")
def local_time(value):
    """Show a database timestamp in Philippine time, e.g. Oct 26, 08:01 AM."""
    return value.astimezone(PH_TIME).strftime("%b %d, %I:%M %p") if value else ""


def people_ahead(t):
    """Count tickets still waiting for the same service that joined before t."""
    stmt = (
        db.select(func.count())
        .select_from(Ticket)
        .where(
            Ticket.service_id == t.service_id,
            Ticket.status == "waiting",
            Ticket.created_at < t.created_at,
        )
    )
    return db.session.scalar(stmt)


ACTIVE_STATUSES = ("waiting", "called")
MINUTES_PER_TICKET = 5  # rough estimate for the approximate wait (FR-02)
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def all_services():
    """Retrieve all services, active or inactive."""
    return db.session.scalars(db.select(Service).order_by(Service.name)).all()


def active_services():
    """Retrieve only active services for visitor operations."""
    stmt = db.select(Service).filter_by(active=True).order_by(Service.name)
    return db.session.scalars(stmt).all()


@app.get("/my-place")
def my_place():
    number = session.get("ticket_id")
    if number is not None and db.session.get(Ticket, number):
        return redirect(url_for("ticket", ticket_id=number))
    session.pop("ticket_id", None)
    return render_template("find.html", form={})


@app.post("/my-place")
def find_ticket():
    raw = request.form.get("number", "").strip().lstrip("#")
    t = db.session.get(Ticket, int(raw)) if raw.isdigit() else None
    if t is None:
        flash("Please fix the highlighted field.", "danger")
        return (
            render_template(
                "find.html",
                form=request.form,
                error="We couldn't find that ticket number. Check your ticket and try again.",
            ),
            404,
        )
    session["ticket_id"] = t.id
    return redirect(url_for("ticket", ticket_id=t.id))


@app.get("/find")
def find_form():
    return render_template("find.html", form={})


@app.route("/")
def index():
    stmt = (
        db.select(Ticket)
        .where(Ticket.status.in_(ACTIVE_STATUSES))
        .order_by(Ticket.created_at)
    )
    active = db.session.scalars(stmt).all()
    called = [t for t in active if t.status == "called"]
    waiting = [t for t in active if t.status == "waiting"]
    services = {s.id: s.name for s in all_services()}

    mine_id = session.get("ticket_id")
    mine = db.session.get(Ticket, mine_id) if mine_id else None
    if mine and mine.status not in ACTIVE_STATUSES:
        mine = None
    my_ahead = people_ahead(mine) if mine else None

    return render_template(
        "index.html",
        called=called,
        waiting=waiting,
        services=services,
        mine=mine,
        my_ahead=my_ahead,
    )


@app.get("/join")
def join_form():
    return render_template("join.html", services=active_services(), form={})


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
    if service is None or not service.active:
        errors["service_id"] = "Choose a service."
    if copies_requested < 1 or copies_requested > 5:
        errors["copies_requested"] = "Copies requested must be between 1 and 5."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return (
            render_template(
                "join.html", services=active_services(), form=form, errors=errors
            ),
            400,
        )

    user = db.session.scalar(db.select(User).filter_by(email=email))
    if user is None:
        user = User(name=name, email=email)

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
                "join.html", services=active_services(), form=form, errors={}
            ),
            409,
        )

    session["ticket_id"] = ticket.id
    flash(f"You joined the queue. Your ticket is #{ticket.id}.", "success")
    return redirect(url_for("ticket", ticket_id=ticket.id))


STAFF_COUNTER = 3  # Donna's counter number (shown on the dashboard)
STAFF_ACTIONS = {"call": "called", "serve": "served", "no-show": "no-show"}


def staff_redirect():
    return redirect(
        url_for("staff_dashboard", service_id=request.form.get("service_id", type=int))
    )


# 8d. Staff Dashboard Route
@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    stmt = (
        db.select(Ticket)
        .where(Ticket.status.in_(["waiting", "called"]))
        .order_by(Ticket.created_at)
    )
    if service_id:
        stmt = stmt.where(Ticket.service_id == service_id)
    queue = db.session.scalars(stmt).all()
    return render_template(
        "staff.html", queue=queue, services=all_services(), selected=service_id
    )


# 9a. Call Next Button
@app.post("/staff/call-next")
def staff_call_next():
    service_id = request.form.get("service_id", type=int)
    stmt = (
        db.select(Ticket)
        .filter_by(status="waiting")
        .order_by(Ticket.created_at)
        .limit(1)
    )
    if service_id:
        stmt = stmt.where(Ticket.service_id == service_id)
    next_ticket = db.session.scalar(stmt)

    if next_ticket:
        next_ticket.status = "called"
        next_ticket.called_at = func.now()
        db.session.commit()
        flash(
            f"Ticket #{next_ticket.id} called. Send them to Counter {STAFF_COUNTER}.",
            "success",
        )
    else:
        flash("No one is waiting.", "info")
    return staff_redirect()


# 9a. Staff Ticket Status Action
@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    new_status = STAFF_ACTIONS.get(action)
    if new_status is None:
        abort(404)
    t = db.get_or_404(Ticket, ticket_id)
    t.status = new_status
    if new_status == "called":
        t.called_at = func.now()
    db.session.commit()
    flash(f"Ticket #{ticket_id} marked {new_status}.", "info")
    return staff_redirect()


# 9c. Hard Delete: Removing a Mistaken Ticket
@app.post("/staff/tickets/<int:ticket_id>/delete")
def delete_ticket(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    db.session.delete(t)
    db.session.commit()
    flash(f"Ticket #{ticket_id} was deleted.", "warning")
    return staff_redirect()


# 9d. Manage Services Routes
@app.get("/staff/services")
def services_list():
    return render_template("staff_services.html", services=all_services())


@app.post("/staff/services")
def service_create():
    name = request.form.get("name", "").strip()
    minutes = request.form.get("avg_minutes", type=int)
    if not name or len(name) > 60 or not minutes or minutes <= 0:
        flash("Enter a name (up to 60 characters) and minutes greater than 0.", "danger")
        return redirect(url_for("services_list"))
    db.session.add(Service(name=name, avg_minutes=minutes))
    try:
        db.session.commit()
        flash(f'Service "{name}" added.', "success")
    except IntegrityError:
        db.session.rollback()
        flash(f'A service named "{name}" already exists.', "danger")
    return redirect(url_for("services_list"))


@app.post("/staff/services/<int:service_id>/edit")
def service_edit(service_id):
    s = db.get_or_404(Service, service_id)
    name = request.form.get("name", "").strip()
    minutes = request.form.get("avg_minutes", type=int)
    active = request.form.get("active") == "on"

    if not name or len(name) > 60 or not minutes or minutes <= 0:
        flash("Enter a valid name and positive average minutes.", "danger")
        return redirect(url_for("services_list"))

    s.name = name
    s.avg_minutes = minutes
    s.active = active
    try:
        db.session.commit()
        flash(f'Service "{s.name}" updated.', "success")
    except IntegrityError:
        db.session.rollback()
        flash(f'A service named "{name}" already exists.', "danger")
    return redirect(url_for("services_list"))


@app.post("/staff/services/<int:service_id>/delete")
def service_delete(service_id):
    s = db.get_or_404(Service, service_id)
    if s.tickets:
        flash(
            f'"{s.name}" has tickets, so it cannot be deleted. Turn it off instead.',
            "danger",
        )
        return redirect(url_for("services_list"))
    db.session.delete(s)
    db.session.commit()
    flash(f'Service "{s.name}" deleted.', "warning")
    return redirect(url_for("services_list"))


# 8b. My place Route
@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    return render_template(
        "ticket.html", ticket=t, service=t.service, ahead=people_ahead(t)
    )


# 8b. My place JSON Route
@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    return {"status": t.status, "ahead": people_ahead(t)}


# 9b. Soft Delete: Leaving the Queue
@app.post("/queue/<int:ticket_id>/leave")
def leave(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    if t.status == "waiting":
        t.status = "left"
        db.session.commit()
        if session.get("ticket_id") == ticket_id:
            session.pop("ticket_id")
        flash("You left the queue.", "info")
        return redirect(url_for("index"))
    flash("That ticket is no longer in the queue.", "warning")
    return redirect(url_for("ticket", ticket_id=ticket_id))


@app.route("/hello")
def hello():
    return "Hello, QueuExpress!"


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