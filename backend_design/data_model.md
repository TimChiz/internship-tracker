The MVP needs three tables: `users`, `applications` and `friend_requests`. 

### users

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | integer | PK |  |
| `email` | varchar(255) | unique, not null | Stored lowercase and stripped |
| `password_hash` | varchar(255) | not null | `werkzeug.security.generate_password_hash` |
| `username` | varchar(16) | nullable; unique index on `lower(username)` | Null until Name Your Rat. Letters, digits and `_`, 3–16 characters |
| `avatar` | varchar(32) | not null, default `'grey'` | Everyone is grey in the MVP. The column exists now so v2 rats need no schema change |
| `created_at` | datetime | not null | UTC |

### applications

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | integer | PK |  |
| `user_id` | integer | FK → users.id, not null, on delete cascade |  |
| `company` | varchar(120) | not null, default `''` | Blank when added from a  link, user will set up later |
| `role` | varchar(120) | not null, default `''` |  |
| `url` | varchar(2048) | nullable |  |
| `status` | varchar(20) | not null, default `'to_do'`, `CHECK` in the six statuses | `to_do`, `in_progress`, `applied`, `interviewing`, `offer`, `rejected` |
| `deadline` | date | nullable |  |
| `is_rolling` | boolean | not null, default false |  |
| `notes` | text | not null, default `''` | Never shown to friends |
| `applied_at` | datetime | nullable | Set the first time status leaves the "To apply" section; never cleared. Drives the leaderboard |
| `created_at`, `updated_at` | datetime | not null | `updated_at` sorts the Closed section |

Index: `(user_id, applied_at)`.

### friend\_requests

One row per pair of users. An `accepted` row is what makes two users friends.

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | integer | PK |  |
| `from_user_id` | integer | FK → users.id, not null, on delete cascade |  |
| `to_user_id` | integer | FK → users.id, not null, on delete cascade |  |
| `status` | varchar(10) | not null, default `'pending'`, `CHECK IN ('pending','accepted')` |  |
| `created_at` | datetime | not null |  |
| `responded_at` | datetime | nullable |  |

Constraints: unique `(from_user_id, to_user_id)` and `CHECK (from_user_id <> to_user_id)`. The service also refuses a request when one already exists in the other direction. Index: `(to_user_id, status)` for "my incoming requests".



Note: avoid duplication -> things like display name, deadline labels, ranks, weekly counts etc should always be computed/joined from tables (data normalization)