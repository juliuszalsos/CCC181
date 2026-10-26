"""QueuExpress: a queue tracker for the PSA Iligan City office.

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
import re

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "dev-only-change-me"  # Week 11 moves this into an environment variable

# Services offered at the PSA Iligan City provincial office.
SERVICES = [
    {"id": 1, "name": "Birth certificate"},
    {"id": 2, "name": "Marriage certificate"},
    {"id": 3, "name": "Death certificate"},
    {"id": 4, "name": "PhilSys National ID"},
]

# Each ticket: number, name, email, service_id, status
# status is one of: waiting, called, served, no-show, cancelled
TICKETS = [
    {"number": 1, "name": "Ana Reyes", "email": "ana@example.com", "service_id": 1, "status": "called"},
    {"number": 2, "name": "Ben Cruz", "email": "ben@example.com", "service_id": 4, "status": "waiting"},
    {"number": 3, "name": "Carla Santos", "email": "carla@example.com", "service_id": 2, "status": "waiting"},
    {"number": 4, "name": "Dino Lopez", "email": "dino@example.com", "service_id": 4, "status": "served"},
]

ACTIVE_STATUSES = ("waiting", "called")
MINUTES_PER_TICKET = 5  # rough estimate for the approximate wait (FR-02)
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")

def get_ticket(number):
    return next((t for t in TICKETS if t["number"] == number), None)

@app.get("/my-place")
def my_place():
    number = session.get("ticket_id")
    if number is not None and get_ticket(number):
        return redirect(url_for("ticket", ticket_id=number))
    session.pop("ticket_id", None)  # stale, e.g. the in-memory data was reset
    return render_template("find.html", form={})


@app.post("/my-place")
def find_ticket():
    raw = request.form.get("number", "").strip().lstrip("#")
    t = get_ticket(int(raw)) if raw.isdigit() else None
    if t is None:
        flash("Please fix the highlighted field.", "danger")
        return render_template(
            "find.html",
            form=request.form,
            error="We couldn't find that ticket number. Check your ticket and try again.",
        ), 404
    session["ticket_id"] = t["number"]
    return redirect(url_for("ticket", ticket_id=t["number"]))

@app.get("/find")
def find_form():
    # Always shows the lookup form, even when a ticket is remembered.
    return render_template("find.html", form={})

@app.route("/")
def index():
    active = sorted(
        (t for t in TICKETS if t["status"] in ACTIVE_STATUSES),
        key=lambda t: t["number"],
    )
    called = [t for t in active if t["status"] == "called"]
    waiting = [t for t in active if t["status"] == "waiting"]
    services = {s["id"]: s["name"] for s in SERVICES}

    mine = get_ticket(session.get("ticket_id"))
    if mine and mine["status"] not in ACTIVE_STATUSES:
        mine = None
    my_ahead = None
    if mine:
        my_ahead = sum(
            1 for x in TICKETS
            if x["service_id"] == mine["service_id"]
            and x["status"] == "waiting"
            and x["number"] < mine["number"]
        )
    return render_template(
        "index.html",
        called=called, waiting=waiting, services=services,
        mine=mine, my_ahead=my_ahead,
    )


@app.get("/join")
def join_form():
    return render_template("join.html", services=SERVICES, form={})


@app.post("/join")
def join():
    form = request.form
    name = form.get("name", "").strip()
    email = form.get("email", "").strip().lower()
    service_id = form.get("service_id", type=int)

    errors = {}
    if not name:
        errors["name"] = "Enter your name."
    elif len(name) > 100:
        errors["name"] = "Your name is too long (100 characters at most)."
    if not EMAIL_PATTERN.fullmatch(email):
        errors["email"] = "Enter a valid email address, like juan@example.com."
    if service_id not in [s["id"] for s in SERVICES]:
        errors["service_id"] = "Choose a service."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=SERVICES, form=form, errors=errors), 400

    number = TICKETS[-1]["number"] + 1 if TICKETS else 1
    TICKETS.append({"number": number, "name": name, "email": email,
                    "service_id": service_id, "status": "waiting"})
    session["ticket_id"] = number
    flash(f"You joined the queue. Your ticket is #{number}.", "success")
    return redirect(url_for("ticket", ticket_id=number))

STAFF_COUNTER = 3  # Donna's counter number (shown on the dashboard)
STAFF_ACTIONS = {"serve": "served", "no-show": "no-show"}


def active_tickets(service_id=None):
    """Called tickets first, then waiting, each in ticket-number order."""
    queue = [t for t in TICKETS if t["status"] in ACTIVE_STATUSES]
    if service_id:
        queue = [t for t in queue if t["service_id"] == service_id]
    return sorted(queue, key=lambda t: (t["status"] != "called", t["number"]))


def staff_redirect():
    # Keeps the chosen service filter after an action.
    return redirect(url_for("staff_dashboard",
                            service_id=request.form.get("service_id", type=int)))


@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    queue = active_tickets(service_id)
    called = [t for t in queue if t["status"] == "called"]
    waiting = [t for t in queue if t["status"] == "waiting"]
    names = {s["id"]: s["name"] for s in SERVICES}
    # Star feature: how many are waiting per service
    counts = {
        s["id"]: sum(1 for t in TICKETS
                     if t["service_id"] == s["id"] and t["status"] == "waiting")
        for s in SERVICES
    }
    return render_template(
        "staff.html",
        queue=queue, called=called, waiting=waiting,
        current=called[0] if called else None,
        next_ticket=waiting[0] if waiting else None,
        services=SERVICES, names=names, counts=counts,
        selected=service_id, counter=STAFF_COUNTER,
    )


@app.post("/staff/call-next")
def staff_call_next():
    service_id = request.form.get("service_id", type=int)
    waiting = [t for t in active_tickets(service_id) if t["status"] == "waiting"]
    if waiting:
        waiting[0]["status"] = "called"
        flash(f"Ticket #{waiting[0]['number']} called. Send them to Counter {STAFF_COUNTER}.", "success")
    else:
        flash("No one is waiting.", "info")
    return staff_redirect()


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    new_status = STAFF_ACTIONS.get(action)
    t = get_ticket(ticket_id)
    if t is None or new_status is None:
        abort(404)
    if t["status"] != "called":
        flash(f"Ticket #{ticket_id} is not being called, so nothing changed.", "warning")
    else:
        t["status"] = new_status
        flash(f"Ticket #{ticket_id} marked {new_status}.", "success")
    return staff_redirect()


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    # <int:ticket_id> only matches numbers, so /queue/abc returns 404.
    t = get_ticket(ticket_id)
    if t is None:
        abort(404)
    ahead = [
        x for x in TICKETS
        if x["service_id"] == t["service_id"]
        and x["status"] == "waiting"
        and x["number"] < t["number"]
    ]
    service = next(s for s in SERVICES if s["id"] == t["service_id"])
    return render_template(
        "ticket.html",
        ticket=t,
        service=service,
        ahead=len(ahead),
        wait_minutes=len(ahead) * MINUTES_PER_TICKET,
    )


@app.post("/queue/<int:ticket_id>/leave")
def leave(ticket_id):
    t = get_ticket(ticket_id)
    if t is None:
        abort(404)
    if t["status"] in ACTIVE_STATUSES:
        t["status"] = "cancelled"
        if session.get("ticket_id") == ticket_id:
            session.pop("ticket_id")
        flash(f"You left the queue. Ticket #{t['number']} was cancelled.", "info")
        return redirect(url_for("index"))
    flash("That ticket is no longer in the queue.", "warning")
    return redirect(url_for("ticket", ticket_id=ticket_id))

@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    t = get_ticket(ticket_id)
    if t is None:
        abort(404)
    ahead = sum(
        1 for x in TICKETS
        if x["service_id"] == t["service_id"]
        and x["status"] == "waiting"
        and x["number"] < t["number"]
    )
    return {
        "status": t["status"],
        "ahead": ahead,
        "wait_minutes": ahead * MINUTES_PER_TICKET,
    }
    
@app.route("/hello")
def hello():
    return "Hello, QueuExpress!"


if __name__ == "__main__":
    app.run(debug=True)