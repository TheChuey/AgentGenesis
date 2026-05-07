from moduels.tools import tool
from datetime import datetime

@tool(name="get_current_datetime", description="Returns the current local date and time.")
def get_current_datetime():
    """Returns the current date and time as a string."""
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y - %H:%M:%S")
