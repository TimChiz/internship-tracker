# Applications table: plan

This is the plan for issue #20. It defines what the Applications table contains and how it behaves, so issue #29 can build it.

It follows `product/rat_race_mvp.md`, `backend_design/data_model.md`, `app/constants.py`, and the code in progress for the model (`database-tables`) and deadline labels (`feature/date-function-weekly-counts`).

**Adding an application:** a user clicks **+ ADD**, fills in a form with the application's details, and clicks **SAVE**. Nothing is added until they save. This replaces the earlier idea of pasting a link and having the fields filled in automatically, which was never specified.

**About the sketch:** the issue asks for a paper sketch. Instead, the lo-fi sketch is the text wireframe in section 3, drafted with Claude. Noku's mockups (`frontend-design/v0_Individual_dashboard.png` and `reference_day.png`) already show the visual design, so this plan only needs to pin down structure and behaviour.

**No JavaScript:** the page uses only Flask, Jinja, HTML and CSS. Every action is a normal form that submits to the server, which then redirects back to the page.

## 1. What a row is

### Fields

| Field | Stored or derived | Required? | Notes |
| --- | --- | --- | --- |
| `company` | Stored | Required | Up to 120 characters |
| `role` | Stored | Required | Up to 120 characters |
| `url` | Stored | Optional | The job posting link |
| `status` | Stored | Required | Defaults to `to_do`. One of the six statuses below |
| `deadline` | Stored | Optional | A date with no time |
| `is_rolling` | Stored | Required | Defaults to false |
| `notes` | Stored | Optional | Defaults to blank. Never shown to friends |
| `applied_at` | Stored, set by the app | — | Set the first time the application leaves To apply; never cleared. Drives the leaderboard |
| `created_at`, `updated_at` | Stored, set by the app | — | `updated_at` sorts the Closed section |
| Display name | Derived | — | "Company - Role" |
| Section | Derived | — | From the status: To apply, Applied or Closed (`SECTIONS` in `app/constants.py`) |
| Deadline label and urgency | Derived | — | e.g. "Due tomorrow", "7 days left", "Rolling", "Deadline passed" (`get_deadline_label`) |
| Formatted deadline | Derived | — | e.g. "Nov 2, 2026" (`format_date`) |

Derived values are never stored. They're computed every time the page loads, as the data model requires.

### Statuses

There are six real statuses, not notes. Rejected, Interviewing and Offer were notes in the old mockup, and are now statuses.

| Status | Shown as | Section |
| --- | --- | --- |
| `to_do` | To-do | To apply |
| `in_progress` | In progress | To apply |
| `applied` | Applied | Applied |
| `interviewing` | Interviewing | Applied |
| `offer` | Offer | Closed |
| `rejected` | Rejected | Closed |

## 2. What the table is for

**Main job:** show me what I need to do next.

### Columns and detail view

The table shows what you need when scanning. Everything else lives on the edit page.

| In the table | On the edit page only |
| --- | --- |
| Name (display name) | Company and role, separately |
| Link ("Open ↗") | The full link |
| Status | Rolling flag |
| Notes (first two lines) | Full notes |
| Deadline (date and label) | Delete |

### Grouping and sorting

The table has three sections, in this order:

1. **To apply** (To-do, In progress), sorted by urgency:
   1. Dated applications, soonest deadline first
   2. Rolling applications with no deadline
   3. Applications with no deadline and not rolling
   4. Overdue applications, at the bottom, labelled "Deadline passed"

   Ties are broken by when the application was added, oldest first.
2. **Applied** (Applied, Interviewing): most recently applied first.
3. **Closed** (Offer, Rejected): most recently updated first. Collapsed behind "See more (n)".

### Urgency

Deadline labels only appear in the To apply section, since once you've applied the deadline no longer matters.

| Days until the deadline | Label | Look |
| --- | --- | --- |
| 0 | Due today | Urgent: red (`--rr-urgent`) |
| 1 | Due tomorrow | Urgent: red |
| 2–7 | "n days left" | Normal text |
| More than 7 | "n days left" | Secondary text |
| Overdue | Deadline passed | Secondary text, not red, since red means something you can still act on (design doc) |

## 3. Layout

### Lo-fi sketch

```
Applications                                                       [ + ADD ]
──────────────────────────────────────────────────────────────────────────────
NAME                  LINK     STATUS          NOTES            DEADLINE
──────────────────────────────────────────────────────────────────────────────
TO APPLY · 3
Stripe - SWE Intern   Open ↗   [In progress]   Ask Sam for...   Nov 8
                                                                Due tomorrow  (red)
Google - STEP Intern  Open ↗   [To-do]                          Nov 20
                                                                13 days left
Meta - DE Intern      —        [To-do]                          Rolling
──────────────────────────────────────────────────────────────────────────────
APPLIED · 2
JP Morgan - Analyst   Open ↗   [Interviewing]  Round 2 on Fri   Sep 30
TikTok - PM Intern    Open ↗   [Applied]                        Sep 12
──────────────────────────────────────────────────────────────────────────────
▸ See more (1)    ← the Closed section, collapsed
```

**Column order and widths:** Name 30%, Link 10%, Status 15%, Notes 30%, Deadline 15%.

### The Add page

**+ ADD** opens this page. The edit page uses the same form, with the fields already filled in and a Delete button.

```
Add an application
──────────────────────────────────────────────
Company *          [ Stripe                  ]
Role *             [ SWE Intern              ]
Link               [ https://...             ]
Status             [ To-do               ▾ ]
Deadline           [ mm/dd/yyyy            ]
                   [ ] Rolling deadline
Notes              [                         ]
                   [                         ]

                   [ SAVE ]   Cancel

* required
```

- **SAVE** adds the application and goes back to the table, where it appears in the right section.
- **Cancel** goes back to the table without adding anything.
- If something is wrong, e.g. a missing company, the page reloads with the error next to that field, and everything the user typed stays filled in.

### Where actions live

| Action | Where |
| --- | --- |
| Add | The **+ ADD** button above the table, which opens the Add page |
| Edit | Click the name to open its edit page, with every field, Save and Cancel |
| Change status | A status dropdown on the edit page |
| Delete | A Delete button on the edit page, then a confirmation page ("Delete Stripe - SWE Intern? Yes / Cancel") |

### Group headers and "See more"

- Each section starts with a header row showing its name and count, e.g. "TO APPLY · 3".
- The Closed section is wrapped in an HTML `<details>` tag, whose `<summary>` reads "See more (n)". Browsers open and close it on click without any JavaScript.

### Routes for #29

| Route | Does |
| --- | --- |
| `GET /applications` | Show the table |
| `GET` and `POST /applications/new` | Show the Add page, and save the new application |
| `GET` and `POST /applications/<id>/edit` | Show and save the edit page |
| `GET` and `POST /applications/<id>/delete` | Show the confirmation and delete |

Every route needs a logged-in user, and returns 404 for an application that belongs to someone else.

## 4. States

| State | What happens |
| --- | --- |
| **Empty** (no applications yet) | The **+ ADD** button shows as normal. Instead of the table, a panel says "No applications yet. Click + ADD to add your first one." |
| **Empty section** | To apply and Applied always show their header, with "Nothing here yet" underneath. Closed is hidden when it's empty |
| **Loading** | No separate state. The server sends the page with the data already in it, and the browser shows its usual loading indicator |
| **Error: page fails to load** | Flask's error handling shows Noku's error page (PR #30) |
| **Error: bad input when adding** | The Add page reloads with the error next to the field, and everything the user typed stays filled in |
| **Very long company or role names** | The name wraps onto more lines instead of being cut off. The 120-character limit keeps it reasonable |
| **Long notes** | Only the first two lines show in the table. The full notes are on the edit page |
| **Long links** | Never shown in the table, only "Open ↗" |
| **Many rows (50+)** | No pagination in the MVP. The header row stays visible while scrolling (CSS `position: sticky`), and Closed stays collapsed. Revisit after the MVP if it gets slow |
| **Overdue deadline** | Stays in To apply, sinks to the bottom, labelled "Deadline passed" in secondary text |
| **Missing link** | The Link column shows "—" instead of "Open ↗" |
| **Missing deadline** | "Rolling" if it's rolling, otherwise "No deadline", both in secondary text |
| **Row hover** | The row's background gets slightly darker |
| **Keyboard focus** | Links and buttons get the same 3px outline as the login pages |
| **Editing** | The same form as the Add page, already filled in, with Save, Cancel and Delete. Errors show next to the field that caused them |

## Things to fix before #29

These came up while writing this plan:

- **`STATUS_LABELS` in `app/constants.py` says `"To_do"`.** It should be `"To-do"`.
- **Quick add is replaced by the Add form.** `product/rat_race_mvp.md` still says "Add an application by pasting a link or typing Company – Role", and PR #31's `parse_quick_add` and `get_display_name` are built for that. Both need updating to match this plan.
- **`get_deadline_label` expects display names, but the app uses keys.** It checks for the section `"to apply"` and statuses `"to do"` and `"in progress"`, but `app/constants.py` uses `to_apply`, `to_do` and `in_progress`. Passed the real values, it always returns no label. It should compare against the keys in `app/constants.py`.

## Open questions for review

1. Is "most recently applied first" right for the Applied section?
2. Is changing status on the edit page enough for the MVP, or should each row have its own status dropdown with an Update button?
3. Should the Notes column be in the table at all, or only on the edit page?
4. Should company and role both be required on the Add form, or is one of them enough?

## Done when (from #20)

- [x] Field list with stored/derived and required/optional marked (section 1)
- [x] Lo-fi sketch covering the layout (section 3) and all the states (section 4)
- [ ] Reviewed and agreed by the team
