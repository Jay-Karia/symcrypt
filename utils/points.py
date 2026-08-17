def generate_points(secret_key, ascii_values):
    points = []
    for i in range(len(secret_key)):
        x = secret_key[i]
        y = ascii_values[i]
        points.append((x, y))
    return points
