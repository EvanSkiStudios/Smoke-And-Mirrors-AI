import datetime


# Get current date and time
def current_date_time():
    now = datetime.datetime.now()
    date = now.strftime("%B %d, %Y")
    time = now.strftime("%I:%M %p")

    return f"The current date is {date}. The current time is {time}."
