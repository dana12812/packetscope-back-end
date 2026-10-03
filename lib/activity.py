# lib/activity.py — records an entry in the activity log for the admin page.

from models.activity import ActivityModel


def log_activity(db, user, action, target=None, capture_id=None):
    """Add an activity row to the session; the caller's commit saves it."""
    db.add(ActivityModel(
        actor_id=user.id,
        actor_username=user.username,
        action=action,
        target=target,
        capture_id=capture_id,
    ))
