"""QueuExpress: a queue tracker for the PSA Iligan City office.

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
from flask import Flask, abort, flash, redirect, render_template, request, url_for

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


def service_names():
    """Map service id -> service name for easy lookup in templates."""
    return {s["id"]: s["name"] for s in SERVICES}


def get_ticket(number):
    return next((t for t in TICKETS if t["number"] == number), None)


def people_ahead(ticket):
    """Count waiting tickets with a lower number than this one."""
    return sum(
        1 for t in TICKETS
        if t["status"] == "waiting" and t["number"] < ticket["number"]
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/join")
def join_form():
    # Placeholder until Part 5 adds the real form.
    return render_template("join.html")


@app.route("/staff")
def staff_dashboard():
    # Placeholder until Part 7 adds the real dashboard.
    return "Staff dashboard coming soon"


@app.route("/queue/<int:ticket_id>")
def ticket(ticket_id):
    # <int:ticket_id> only matches numbers, so /queue/abc returns 404.
    t = get_ticket(ticket_id)
    if t is None:
        abort(404)
    return render_template(
        "ticket.html",
        ticket=t,
        service_name=service_names()[t["service_id"]],
        ahead=people_ahead(t),
    )


@app.route("/hello")
def hello():
    return "Hello, QueuExpress!"


if __name__ == "__main__":
    app.run(debug=True)