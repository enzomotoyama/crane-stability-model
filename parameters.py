import numpy as np

# Disclaimer: These values are fictional and modified for confidentiality.
# The data structure and code logic are inspired by a real-world internship project at Tadano Europe.

def get_values():
    x_cog = np.array([3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0], dtype=float)
    z_cog = np.array([30.0, 28.8, 27.6, 26.5, 25.4, 24.4, 23.5, 22.6, 21.8, 21.0, 20.3], dtype=float)
    radius = np.array([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], dtype=float)

    width = 10.0

    mass_list = 1000 * np.array([250, 225, 200, 180, 165, 150, 135, 122, 110, 99, 89])
    mass_structure = np.ones(len(mass_list)) * 1000 * (750 - 250)
    mass_total = mass_structure + mass_list

    g = 9.81

    a0 = width / 2.0 - x_cog
    h0 = z_cog
    r = np.sqrt(a0 * a0 + h0 * h0)
    IT = mass_total * (r * r)

    return {
        "x_cog": x_cog,
        "z_cog": z_cog,
        "width": width,
        "radius": radius,
        "mass_total": mass_total,
        "g": g,
        "IT": IT,
        "r": r
    }
