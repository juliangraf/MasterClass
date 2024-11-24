from datetime import datetime

from django import template

register = template.Library()


@register.filter
def time_difference(end_time, start_time):
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")
    difference = (end - start).total_seconds() / 60  # Difference in minutes

    # Assuming each time slot is 30 minutes, adjust accordingly
    slot_duration = 30
    width = (difference / slot_duration) * 100  # Convert to percentage for width

    return width
