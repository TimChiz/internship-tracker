#values shared across the app (in other files, import them from here instead of typing yourself)

STATUS_OPTIONS = ("to_do", "in_progress", "applied", "interviewing", "offer", "rejected")
#making it a tuple so that it can't be accidentally changed

# "translation" of status options in code to what we want to show in the front end to the users
STATUS_LABELS = {
    "to_do": "To_do",
    "in_progress": "In progress",
    "applied": "Applied",
    "interviewing": "Interviewing",
    "offer": "Offer",
    "rejected": "Rejected",
}

#which statuses belong in which section on the applications page
SECTIONS = (
    ("to_apply", "To apply", ("to_do", "in_progress")),
    ("applied", "Applied", ("applied", "interviewing")),
    ("closed", "Closed", ("offer", "rejected")),
)
