# Complete MVP 1 Documentation

**Rat Race MVP 1** is tagged on GitHub as [`v1.0-mvp1`](https://github.com/TimChiz/internship-tracker/tree/v1.0-mvp1) .

MVP 1 is the first version of Rat Race that a student can use from start to finish: create an account, name their rat, track internship applications, and log out. 

## Contents

1. [What MVP 1 is](#1-what-mvp-1-is)
2. [Features](#2-features)
3. [Implementation](#3-implementation)
4. [How to run it](#4-how-to-run-it)
5. [Known limitations](#5-known-limitations)
6. [Who built what](#6-who-built-what)
7. [User testing](#7-user-testing)

---

## 1. What MVP 1 is

**Goal:** let a student keep all their internship applications in one place and always see what to do next.

**Target users:** undergraduate students in the US applying for summer internships.

### In and out of MVP 1

Compared with the full Rat Race 1.0 plan in [`product/rat_race_mvp.md`](../../product/rat_race_mvp.md):

| Feature | In MVP 1? |
| --- | --- |
| Sign up with email and password, log in, log out | ✅ |
| Name your rat and pick a rat | ✅ (2 rats so far, out of a planned 8) |
| Add an application | ✅ through the **+ ADD** popup |
| Edit status, deadline, rolling flag, link and notes, or delete | ✅ |
| Applications grouped (To apply / Applied / Closed), sorted by urgency, with labels like "Due tomorrow" | ✅ |
| Friend requests by username | ❌ planned for a later MVP |
| Weekly leaderboard with friends | ❌ planned for a later MVP |
| Unit tests in GitHub Actions, and `docker compose up` | ❌ not set up yet |

Decided out of MVP 1 in review: **quick add** (pasting a link or "Company – Role" into one box), replaced by the **+ ADD** form ([#32](https://github.com/TimChiz/internship-tracker/pull/32)), and the **CV / document manager**.

---

## 2. Features

### The user's journey

```
/register → /name-your-rat → /applications → (add, edit, change status, delete) → Log out → /login
```

Going to `/` sends logged-in users to `/applications` and everyone else to `/login`.

### Accounts

- **Sign up** (`/register`): email, password and confirm password. The password must be at least 8 characters. An email that's already registered is rejected. After signing up, the user is logged in and sent to Name Your Rat.
- **Name Your Rat** (`/name-your-rat`): the user flips between rats with the arrows, picks one, and names it. The name is their public username: 3–16 characters, letters, digits and `_`, and unique ignoring capitals.
- **Log in** (`/login`): email and password. A wrong email or password shows the same message, "Email or password is incorrect.", so the page doesn't reveal which emails have an account. Users who haven't named their rat yet are sent to Name Your Rat.
- **Log out:** a button in the header (a form, so a link can't log anyone out by accident).
- **Protected pages:** every Applications page needs a logged-in user with a username. Logged-out users go to `/login`.

### The Applications table (`/applications`)

- **Three sections:**
  - **To apply** (To-do, In progress): most urgent first. Soonest deadline first, then rolling, then no deadline, then overdue at the bottom.
  - **Applied** (Applied, Interviewing): most recently applied first.
  - **Closed** (Offer, Rejected): most recently updated first, hidden behind **See more**.
- **Columns:** Name, Link ("Open ↗"), Status, Notes (first two lines), Deadline.
- **Deadline labels** (To apply only): "Due today" and "Due tomorrow" in red, "n days left", "Rolling", "No deadline" and "Deadline passed".
- **Empty states:** "No applications yet" for a new user, and "Nothing here yet" for an empty section.

### Adding, editing and deleting

- **+ ADD popup:** company and role (required), link, status, deadline, rolling deadline and notes. If something's wrong, the popup reopens with the error next to the field and everything typed still filled in.
- **Status menu:** clicking a row's status tag opens the six statuses, and one click saves the new one.
- **Edit page** (`/applications/<id>/edit`): clicking a name opens every field, already filled in, with **SAVE**, **Cancel** and **Delete**.
- **Delete** (`/applications/<id>/delete`): asks "Delete Stripe - SWE Intern? This can't be undone." before deleting.

### The header and the racing rat

- **Shared header** on every logged-in page: the RR logo, the username in big type, the user's rat with the number of applications they've sent, Log out, and the day/night switch.
- **The racing rat:** the first time an application is marked as sent (it leaves To apply), the rat races a lap in a red car next to the page title. It plays once, and is switched off for people who ask their device for less motion.

### Other

- **Day and night mode:** the sun or moon switches modes, and the choice carries over between pages.
- **Error pages:** every HTTP error, such as 404 or 500, shows a Rat Race page with the code and a message, such as "404 Page not found".

---

## 3. Implementation

### Tech stack

| Part | What we use |
| --- | --- |
| Language | Python 3 |
| Web framework | Flask, with blueprints for each area of the app |
| Database | SQLite, through Flask-SQLAlchemy |
| Logins | Flask-Login, with passwords hashed by Werkzeug |
| Pages | Jinja templates, HTML and CSS |
| JavaScript | Only for day/night mode (`theme.js`) and the show-password buttons (`auth_form.js`). The popup, status menu and "See more" use plain HTML (`popover` and `<details>`). |
| Tests | Python's `unittest`, with Flask's test client and an in-memory database |

### How the code is organised

Each layer performs one task, and only talks to the layer below it:

```
routes/        Read the request, call a service, show a page or redirect. No business rules.
  ↓
services/      The business rules: checking forms, sorting and grouping, deadline labels,
  ↓            when an application counts as sent, the racing rat.
repositories/  Database queries. They never commit; the service decides when to save.
  ↓
models.py      The tables (SQLAlchemy classes).
```

| Folder | Main files |
| --- | --- |
| `app/routes/` | `auth.py` (sign up, log in, log out, Name Your Rat), `applications.py` (table, add, status, edit, delete), `errors.py` (error pages), `home.py` (`/`) |
| `app/services/` | `auth.py`, `applications.py`, `tracker.py`, `deadlines.py`, `header.py`, `stats.py`, `rats.py` |
| `app/repositories/` | `users.py`, `applications.py` |
| `app/templates/` | `auth/`, `applications/`, `components/` (shared pieces such as the header and race track), `error.html` |
| `app/static/` | `css/` (`tokens.css` holds every color and font), `js/`, `fonts/`, `images/` |

`app/__init__.py` holds `create_app()`, which builds the app, connects the database and the login manager, and registers the blueprints. Tests call it with an in-memory database, so they never touch real data.

### Data model

| Table | Columns |
| --- | --- |
| `users` | `id`, `email` (unique), `password_hash`, `username` (unique ignoring capitals; empty until Name Your Rat), `rat` (which rat they picked) |
| `applications` | `id`, `user_id` (owner), `company`, `role`, `url`, `status` (one of six, checked by the database), `deadline`, `is_rolling`, `notes`, `applied_at`, `created_at`, `updated_at` |

Values like the display name, section, deadline label and sent count are never stored. They're calculated each time from these columns. The full design is in [`backend_design/data_model.md`](../../backend_design/data_model.md).

### Routes

| Route | What it does |
| --- | --- |
| `GET /` | Sends the user to `/applications` or `/login` |
| `GET, POST /register` | Sign-up form |
| `GET, POST /login` | Log-in form |
| `POST /logout` | Log out |
| `GET, POST /name-your-rat` | Pick and name a rat |
| `GET /applications` | The table |
| `POST /applications/new` | Save from the + ADD popup |
| `POST /applications/<id>/status` | Save a status from the row's status menu |
| `GET, POST /applications/<id>/edit` | Edit page |
| `GET, POST /applications/<id>/delete` | Delete confirmation, then delete |
| `POST /applications/quick-add` | Quick add from a one-line box. **Not used by any page in MVP 1** (see limitations) |

### Rules worth knowing

- **When an application counts as sent:** `applied_at` is set the first time an application leaves To apply, whether from the popup, the status menu or the edit page, and it's never cleared. The header's count and the racing rat both use it, and the future leaderboard will too.
- **Ownership:** every application is loaded with both the user's id and the application's id. Another user's application, or one that doesn't exist, gives the same 404, so nobody can find out which ids exist.
- **Time zone:** "today" and deadlines use New York time (`app/clock.py`).
- **No double submits:** every form that saves something redirects afterwards, so refreshing the page doesn't save it twice.

### Tests

152 tests, all passing at the MVP 1 tag. Run them with `python -m unittest discover tests`. They cover:

- Sign-up and username rules, registering, logging in and out, and Name Your Rat
- Protected pages and redirects
- The Add form rules, sorting and grouping, and deadline labels
- Editing, the status menu, deleting, and that users can't touch each other's applications
- When `applied_at` is set, the header's count, and when the race plays
- Error pages

---

## 4. How to run it

You need Python 3.10 or newer.

1. Get the MVP 1 code:
   ```bash
   git clone https://github.com/TimChiz/internship-tracker.git
   cd internship-tracker
   git checkout v1.0-mvp1
   ```
2. Install the packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   python -m flask --app app run
   ```
4. Open http://127.0.0.1:5000 and create an account.

The database is created automatically at `instance/ratrace.sqlite`. **If you ran an older version before**, delete or rename that file first: the app doesn't update existing tables, so an old database is missing newer columns, and sign-up will fail.

To run the tests:
```bash
python -m unittest discover tests
```

---

## 5. Known limitations

- **2 rats instead of 8.** The second rat is placeholder art until the rest are drawn.
- **The quick-add route has no button.** `POST /applications/quick-add` ([#41](https://github.com/TimChiz/internship-tracker/pull/41)) works, but no page uses it, since adding goes through the + ADD popup. It will be removed in MVP 2.
- **No CI or Docker yet.** Tests run only on our own laptops, and running the app needs Python installed.

---

## 6. Who built what

| Area | Pull requests |
| --- | --- |
| Product and planning | MVP definitions [#11](https://github.com/TimChiz/internship-tracker/pull/11) (@klarakonkel) · Applications table plan [#32](https://github.com/TimChiz/internship-tracker/pull/32) (@TimChiz) · user research form [#5](https://github.com/TimChiz/internship-tracker/pull/5) (@AhmedUsmanKhan) · MVP 1 feedback form [#36](https://github.com/TimChiz/internship-tracker/pull/36) (@TimChiz) |
| App setup and database | Backend schema [#10](https://github.com/TimChiz/internship-tracker/pull/10) · Flask app setup [#18](https://github.com/TimChiz/internship-tracker/pull/18) · database tables [#19](https://github.com/TimChiz/internship-tracker/pull/19) (@klarakonkel) |
| Accounts | Validators [#22](https://github.com/TimChiz/internship-tracker/pull/22) · registering and claiming usernames [#27](https://github.com/TimChiz/internship-tracker/pull/27) · Flask-Login [#28](https://github.com/TimChiz/internship-tracker/pull/28) · working auth pages and log out [#44](https://github.com/TimChiz/internship-tracker/pull/44) (@AhmedUsmanKhan) |
| Design and pages | Login and register pages [#23](https://github.com/TimChiz/internship-tracker/pull/23) · error pages [#30](https://github.com/TimChiz/internship-tracker/pull/30) · shared header and racing rat [#43](https://github.com/TimChiz/internship-tracker/pull/43) · Name Your Rat [#45](https://github.com/TimChiz/internship-tracker/pull/45) (@NokuChimbetete) |
| Tracker logic | Deadline labels and week boundaries [#21](https://github.com/TimChiz/internship-tracker/pull/21) · quick add and status changes [#31](https://github.com/TimChiz/internship-tracker/pull/31) · tracker services [#37](https://github.com/TimChiz/internship-tracker/pull/37) (@litwu1) · tracker routes [#41](https://github.com/TimChiz/internship-tracker/pull/41) (@klarakonkel) |
| Applications pages | Table and + ADD popup [#35](https://github.com/TimChiz/internship-tracker/pull/35) · edit page, delete confirmation and status menu [#42](https://github.com/TimChiz/internship-tracker/pull/42) (@TimChiz) |

---

## 7. User testing & Feedback

- **Tests** All done in-person or virtually pusing a team member's laptop.
- **Feedback form:** The questions are in [`docs/user_research/mvp1_feedback_form.md`](../user_research/mvp1_feedback_form.md).
- **Results:** In this spreadsheet: https://docs.google.com/spreadsheets/d/19TrP4lc6EGUcYgHhIebUCTFnFtLoSi7fhRYGr-BC9zY/edit?usp=sharing

