def map_to_color(value):
    value = float(value)  # Convert the string to a numerical value
    # Map the value to a color spectrum (from red to green)
    red = int((1 - value/100) * 255)
    green = int((value/100) * 255)
    return f'rgb({red}, {green}, 0)'