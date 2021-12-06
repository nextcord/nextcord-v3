from docs._pygments.dark import CustomDarkStyle


def clamp(val, minimum=0, maximum=255):
    if val < minimum:
        return minimum
    if val > maximum:
        return maximum
    return val


class CustomLightStyle(CustomDarkStyle):
    background_color = "#f3f3f3"
    styles = {}
    for k, v in CustomDarkStyle.styles.items():
        try:
            inverted = 0xFFFFFF ^ int(v[-6:], 16)
            new = str(hex(inverted))[2:]
            while len(new) < 6:
                new = "0" + new
            r, g, b = int(new[:2], 16), int(new[2:4], 16), int(new[4:], 16)

            r = round(clamp(r * 0.75))
            g = round(clamp(g * 0.75))
            b = round(clamp(b * 0.75))

            new = "%02x%02x%02x" % (r, g, b)
            styles[k] = v[:-6] + new
        except:
            continue
