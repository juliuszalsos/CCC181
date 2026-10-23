# QueuExpress: Government Agency Queue Tracker

QueuExpress is a web app for the Philippine Statistics Authority provincial office in Iligan City, where citizens line up for civil registry documents and PhilSys National ID applications. Citizens join the queue and follow their ticket status and position from their phone, while counter staff filter, call and process applicants from a desktop dashboard. This is the Week 2 starter built with Flask and Jinja2; run it with `flask --app app run --debug` and open http://127.0.0.1:5000.

## Project structure

```
my-app/
├── app.py              # creates the app, holds SERVICES and TICKETS, defines routes
├── requirements.txt    # packages to rebuild the environment
├── .gitignore          # keeps .venv, caches and secrets out of Git
├── .venv/              # your virtual environment (not committed)
├── templates/          # Jinja2 HTML files for render_template()
│   ├── base.html       # shared layout
│   ├── index.html      # home page with the active queue
│   └── ticket.html     # page for /queue/<ticket_id>
└── static/             # served at /static/...
    ├── css/style.css
    └── js/main.js
```

## Routes

| URL | View function | What you see |
|---|---|---|
| `/` | `index()` | The active queue (waiting and called tickets), rendered with `index.html` |
| `/queue/<int:ticket_id>` | `ticket()` | Ticket number, service, status and people ahead, e.g. `/queue/2` |
| `/hello` | `hello()` | The plain text "Hello, QueuExpress!" |

Try `/queue/abc`: the `int` converter only accepts numbers, so Flask returns 404. A number with no ticket, like `/queue/99`, also returns 404.