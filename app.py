"""QueuExpress: a queue tracker for the PSA Iligan City office.

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
from flask import Flask, abort, render_template

app = Flask(__name__)

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
    active = [t for t in TICKETS if t["status"] in ACTIVE_STATUSES]
    return render_template("index.html", tickets=active, services=service_names())


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