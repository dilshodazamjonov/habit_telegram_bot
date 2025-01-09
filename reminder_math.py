from datetime import datetime, timedelta


def calculate_next_reminder_time(frequency, deadline):
    """
    Calculate the next reminder time based on the frequency and deadline.

    Args:
        frequency (str): The frequency of reminders (e.g., "every hour", "every day").
        deadline (datetime.date): The deadline for the goal.

    Returns:
        str: The next reminder time in "YYYY-MM-DD HH:MM:SS" format.
    """
    now = datetime.now()

    # Convert deadline (date) to datetime for comparison
    deadline_datetime = datetime.combine(deadline, datetime.min.time())
    if now > deadline_datetime:
        raise ValueError("The deadline has already passed. Cannot calculate reminders.")

    if frequency == "every hour":
        next_reminder = now + timedelta(hours=1)
    elif frequency == "every day":
        next_reminder = now + timedelta(days=1)
    elif frequency == "every week":
        next_reminder = now + timedelta(weeks=1)
    elif frequency == "every month":
        next_reminder = now + timedelta(days=30)
    else:
        raise ValueError("Invalid frequency. Supported values are: every hour, every day, every week, every month.")
    if next_reminder > deadline_datetime:
        next_reminder = deadline_datetime

    # Return the next reminder time as a string
    return next_reminder.strftime("%Y-%m-%d %H:%M:%S")
