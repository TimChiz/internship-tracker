# internship-tracker
A full-stack internship application tracker for undergraduate students featuring priority deadline sorting, and social progress sharing. Made by the best group ever!

## backend schema:
```
ratrace/
├── run.py                     # create_app() and app.run(); 
├── requirements.txt           # Flask, Flask-SQLAlchemy, Flask-Login, whatever else comes up during coding
├── Dockerfile, docker-compose.yml, .github/workflows/ci.yml
├── app/
│   ├── __init__.py            # create_app(config_name), db, login_manager, registers blueprints
│   ├── config.py              # Config / TestConfig classes; reads SECRET_KEY, DATABASE_URL from env
│   ├── constants.py           # STATUSES, STATUS_LABELS, SECTIONS, APP_TIMEZONE
│   ├── models.py              # User, Application, FriendRequest; tables and constraints only
│   ├── repositories/          # every database query lives here
│   │   ├── users.py  applications.py  friends.py
│   ├── services/              # business rules; no `request`, no `db.session`
│   │   ├── auth.py            # sign-up and login validation, username rules
│   │   ├── tracker.py         # quick-add parsing, CRUD rules, grouping, sorting
│   │   ├── deadlines.py       # pure date math: labels, urgency, week bounds
│   │   └── social.py          # friend requests, leaderboard
│   ├── routes/                # thin: parse form → call service → flash + redirect, or render
│   │   ├── auth.py  applications.py  social.py
│   ├── cli.py                 # `flask seed`: demo users, friends, applications
│   ├── templates/  static/    # the frontend team's area - tbd
└── tests/
    ├── test_deadlines.py  test_tracker.py  test_auth.py  test_social.py
    └── test_routes.py

```