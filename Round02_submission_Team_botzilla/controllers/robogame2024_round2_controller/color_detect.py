import math

def rgb_to_lab(rgb):
    """
    Convert an RGB color to Lab color space without using NumPy.

    :param rgb: Tuple (R, G, B) in 0-255 range
    :return: Tuple (L, a, b) in Lab space
    """
    # Step 1: Normalize RGB values to [0,1] range
    r, g, b = [x / 255.0 for x in rgb]

    # Step 2: Apply gamma correction (sRGB to linear RGB)
    def gamma_correct(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = gamma_correct(r), gamma_correct(g), gamma_correct(b)

    # Step 3: Convert RGB to XYZ using standard matrix
    X = (r * 0.4124564 + g * 0.3575761 + b * 0.1804375)
    Y = (r * 0.2126729 + g * 0.7151522 + b * 0.0721750)
    Z = (r * 0.0193339 + g * 0.1191920 + b * 0.9503041)

    # Step 4: Normalize XYZ to reference white D65 (Standard daylight)
    X, Y, Z = X / 0.95047, Y / 1.00000, Z / 1.08883

    # Step 5: Convert XYZ to Lab
    def f(t):
        return math.pow(t, 1/3) if t > (6/29)**3 else (t / (3 * (6/29)**2)) + (4/29)

    fx, fy, fz = f(X), f(Y), f(Z)

    L = (116 * fy) - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)

    return (L, a, b)

def deltaE_ciede2000(Lab1, Lab2):
    """
    Compute the color difference (ΔE CIEDE2000) between two Lab colors.

    :param Lab1: Tuple (L1, a1, b1) - First color in Lab space
    :param Lab2: Tuple (L2, a2, b2) - Second color in Lab space
    :return: ΔE2000 color difference (float)
    """
    L1, a1, b1 = Lab1
    L2, a2, b2 = Lab2

    # Step 1: Compute C1, C2 (Chroma values)
    C1 = math.sqrt(a1**2 + b1**2)
    C2 = math.sqrt(a2**2 + b2**2)

    # Step 2: Compute average Chroma
    C_avg = (C1 + C2) / 2

    # Step 3: Compute G factor (chromatic adaptation)
    G = 0.5 * (1 - math.sqrt((C_avg**7) / (C_avg**7 + 25**7)))

    # Step 4: Adjusted a' values
    a1_prime = (1 + G) * a1
    a2_prime = (1 + G) * a2

    # Step 5: Compute C' (adjusted chroma)
    C1_prime = math.sqrt(a1_prime**2 + b1**2)
    C2_prime = math.sqrt(a2_prime**2 + b2**2)
    
    # Step 6: Compute h' (adjusted hue angle)
    h1_prime = math.degrees(math.atan2(b1, a1_prime)) % 360
    h2_prime = math.degrees(math.atan2(b2, a2_prime)) % 360

    # Step 7: Compute ΔL', ΔC', ΔH'
    delta_L_prime = L2 - L1
    delta_C_prime = C2_prime - C1_prime

    delta_h_prime = h2_prime - h1_prime
    if abs(delta_h_prime) > 180:
        delta_h_prime += 360 if delta_h_prime < 0 else -360

    delta_H_prime = 2 * math.sqrt(C1_prime * C2_prime) * math.sin(math.radians(delta_h_prime) / 2)

    # Step 8: Compute average L', C', and h'
    L_avg_prime = (L1 + L2) / 2
    C_avg_prime = (C1_prime + C2_prime) / 2

    if abs(h1_prime - h2_prime) > 180:
        h_avg_prime = (h1_prime + h2_prime + 360) / 2 if h1_prime + h2_prime < 360 else (h1_prime + h2_prime - 360) / 2
    else:
        h_avg_prime = (h1_prime + h2_prime) / 2

    # Step 9: Compute weighting functions
    T = 1 - 0.17 * math.cos(math.radians(h_avg_prime - 30)) + \
        0.24 * math.cos(math.radians(2 * h_avg_prime)) + \
        0.32 * math.cos(math.radians(3 * h_avg_prime + 6)) - \
        0.20 * math.cos(math.radians(4 * h_avg_prime - 63))

    SL = 1 + (0.015 * ((L_avg_prime - 50) ** 2)) / math.sqrt(20 + ((L_avg_prime - 50) ** 2))
    SC = 1 + 0.045 * C_avg_prime
    SH = 1 + 0.015 * C_avg_prime * T

    delta_theta = 30 * math.exp(-((h_avg_prime - 275) / 25) ** 2)
    RC = 2 * math.sqrt((C_avg_prime ** 7) / (C_avg_prime ** 7 + 25 ** 7))
    RT = -RC * math.sin(math.radians(2 * delta_theta))

    # Step 10: Compute final ΔE2000
    delta_E = math.sqrt(
        (delta_L_prime / SL) ** 2 +
        (delta_C_prime / SC) ** 2 +
        (delta_H_prime / SH) ** 2 +
        RT * (delta_C_prime / SC) * (delta_H_prime / SH)
    )

    return delta_E

def get_color_deltas(imageArray, target_rgb, width=64, height=64, threshold=20):
    target_lab = rgb_to_lab(target_rgb)

    deltas = []

    for y in range(height):
        for x in range(width):
            color = imageArray[y][x]
            color_lab = rgb_to_lab(color)

            delta_E = deltaE_ciede2000(target_lab, color_lab)

            if delta_E < threshold:
                deltas.append(delta_E)

    return min(deltas) if deltas else None

def is_color_exists(imageArray, target_rgb, width=64, height=64, threshold=10):
    target_lab = rgb_to_lab(target_rgb)

    for y in range(height):
        for x in range(width):
            color = imageArray[y][x]
            color_lab = rgb_to_lab(color)

            delta_E = deltaE_ciede2000(target_lab, color_lab)

            if delta_E < threshold:
                return True

    return False