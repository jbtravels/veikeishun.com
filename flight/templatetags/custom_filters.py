from django import template

register = template.Library()

@register.filter(name='format_time')
def format_time(minutes_str):
    try:
        minutes = int(minutes_str)
        hours = minutes/60
        remaining_minutes = minutes%60
        formatted_hours = round(hours)
        formatted_minutes = round(remaining_minutes)
        formatted_time = f"{formatted_hours}h {formatted_minutes}m"
        return formatted_time
    except ValueError:
        return "Invalid Time"
    
@register.simple_tag
def calculate_total_price(adult_amount, children_amount, infant_amount):
    try:
        adult_amount = float(adult_amount)
        children_amount = float(children_amount)
        infant_amount = float(infant_amount)

        total_price = adult_amount + children_amount + infant_amount
        total_price_rounded = round(total_price)
        return total_price_rounded
    except ValueError:
        return "Invalid Price"


