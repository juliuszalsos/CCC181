# QueuExpress: Government Agency Queue Tracker

QueuExpress is a web app for the Philippine Statistics Authority provincial office in Iligan City, where citizens line up for civil registry documents and PhilSys National ID applications. Citizens join the queue and follow their ticket status and position from their phone, while counter staff filter, call and process applicants from a desktop dashboard. It is built with Flask, Jinja2 and Bootstrap 5. Run it with `flask --app app run --debug` and open http://127.0.0.1:5000.

**Note:** The staff dashboard (`/staff`) is open to anyone, with no login, until authentication is added in a later week. Tickets are kept in memory, so they reset whenever the server restarts.

## Features

- **Join the queue:** a form with server-side validation (name, email, service) that creates a ticket.
- **My place:** the ticket number, service, status badge, people ahead and approximate wait, updated automatically every 10 seconds. The ticket can be cancelled with "Leave the queue".
- **Find a ticket:** look up a ticket by number if the phone has not remembered it.
- **Live queue:** the home page shows who is being served and who is waiting.
- **Staff dashboard:** filter by service, call the next applicant, and mark a called ticket as served or no-show.

## Project structure

```
CCC181-1/
├── app.py              # creates the app, holds SERVICES and TICKETS, defines routes
├── requirements.txt    # packages to rebuild the environment
├── .gitignore          # keeps .venv, caches and secrets out of Git
├── .venv/              # your virtual environment (not committed)
├── activities/         # course activities
├── docs/
│   ├── week1/          # project proposal
│   └── week3/          # personas, wireframes, feedback, accessibility,
│                       # usability test, report and screenshots
├── templates/          # Jinja2 HTML files for render_template()
│   ├── base.html       # shared layout: header, navigation, flash messages, footer
│   ├── index.html      # home page with the live queue
│   ├── join.html       # join form
│   ├── ticket.html     # My place page
│   ├── find.html       # ticket number lookup
│   └── staff.html      # staff dashboard
└── static/             # served at /static/...
    ├── css/style.css
    └── js/main.js
```

## Routes

| URL | Method | View function | What it does |
|---|---|---|---|
| `/` | GET | `index()` | Live queue: now serving, waiting list, and your ticket if remembered |
| `/join` | GET | `join_form()` | Shows the join form |
| `/join` | POST | `join()` | Validates the form, creates a waiting ticket, redirects to My place |
| `/my-place` | GET | `my_place()` | Goes to your remembered ticket, or shows the lookup form |
| `/my-place` | POST | `find_ticket()` | Looks up a ticket by number |
| `/find` | GET | `find_form()` | Always shows the lookup form |
| `/queue/<int:ticket_id>` | GET | `ticket()` | My place: number, service, status, people ahead, approximate wait |
| `/queue/<int:ticket_id>/leave` | POST | `leave()` | Cancels the ticket |
| `/queue/<int:ticket_id>/status.json` | GET | `ticket_status()` | Status, people ahead and wait as JSON, used for auto-refresh |
| `/staff` | GET | `staff_dashboard()` | Staff dashboard, with a `?service_id=` filter |
| `/staff/call-next` | POST | `staff_call_next()` | Calls the first waiting ticket in the current filter |
| `/staff/tickets/<int:ticket_id>/<action>` | POST | `staff_action()` | `serve` or `no-show` on a called ticket |
| `/hello` | GET | `hello()` | The plain text "Hello, QueuExpress!" |

Try `/queue/abc`: the `int` converter only accepts numbers, so Flask returns 404. A number with no ticket, like `/queue/99`, also returns 404.

## Ticket statuses

`waiting` → `called` → `served` or `no-show`. A person who leaves the queue is marked `cancelled`.

People ahead is counted per service, so each service has its own line.

## 1. Set up the Python environment

```bash
# create (once per project)
python -m venv .venv

# activate (every new terminal)
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS/Linux

# install the packages
pip install -r requirements.txt
```

Your prompt shows `(.venv)` when the environment is active. Some systems use `python3` or `py` instead of `python`.
If PowerShell blocks the activate script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use Command Prompt.

If you add more packages later, record them with:

```bash
pip freeze > requirements.txt
```

## 2. Run the app

```bash
flask --app app run --debug
```

Open http://127.0.0.1:5000. With `--debug`, the server reloads every time you save a file. Never use debug mode in production.

To try it on a phone on the same Wi-Fi, run `flask --app app run --debug --host 0.0.0.0` and open your laptop's IP address on port 5000.