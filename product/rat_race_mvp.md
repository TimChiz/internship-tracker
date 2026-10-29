## RAT RACE 1.0 (MVP)

A user can:
- Sign up with email and password, name their rat (username) and choose one of 8 rat options, log in and log out.
- Add an application by pasting a link or typing "Company – Role".
- Edit its status, deadline, rolling flag, link and notes, or delete it.
- See their applications grouped (To apply / Applied / Closed), sorted by urgency, with labels like "Due tomorrow".
- Send a friend request by username, and accept or decline incoming ones.
- See a weekly leaderboard of themselves and their friends, ranked by applications sent this week.

Plus: unit tests pass in GitHub Actions, and docker compose up runs the app on a clean machine (once we get to dockers)

Out of MVP:
CV manager, streak of logged applications, adding friends by email, changing your Rat avatar (adding accessories, changing colour etc)

assumptions/initial configurations:

Who is on the leaderboard?
- You plus accepted friends. A platform-wide board would need no friends feature, but would show strangers' activity -> maybe in 2.0?

Week boundary and time zone
- Monday to Sunday, America/New_York for everyone

Where do rolling applications sort in To apply?
- After dated ones, before undated ones. The brief says "show these higher"; confirm higher than what

Overdue To-apply items
- Stay in To apply, sunk to the bottom, labelled "Deadline passed"

Statuses and sections
- 6 statuses in 3 sections; Closed (Offer, Rejected) collapsed behind "See more"

Login identifier
- Email. Usernames are public on the leaderboard, so they make a weaker login secret

Username rules
- 3–16 characters, letters, digits and _, unique ignoring case, set once

Leaderboard ties
- Shared rank (1, 2, 2, 4), and within - alphabetical

Final deployment target
- docker compose up on a laptop. Hosted, or multi-container with Postgres, is a week 11 decision (after we have the docker class)