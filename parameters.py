
import numpy as np

def get_values():
    x_cog = np.array([2.8, 2.9, 3.0 , 3.1, 3.2, 3.3, 3.4, 3.4 , 3.5, 3.5, 3.6], dtype=float)
    z_cog = np.array([31.1, 29.5, 28.1, 26.8, 25.6, 24.6, 23.6, 22.7, 21.8, 21.1, 20.4], dtype=float)
    radius = np.array([10,11,12,13,14,15,16,17,18,19,20], dtype=float)

    width = 10.0

    mass_list = 1000*np.array([259.9,232.4,209.4,190.0,173.4,159.0,146.4,135.3,125.4,116.6,108.6])
    mass_structure = np.ones(len(mass_list))*1000*(765.94-260.0)
    mass_total = mass_structure + mass_list

    g = 9.81

    a0 = width/2.0 - x_cog
    h0 = z_cog
    r  = np.sqrt(a0*a0 + h0*h0)
    IT = mass_total * (r*r)

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
