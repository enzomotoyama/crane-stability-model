"""
This script simulates crane tipping conditions under braking.
It uses parameters inspired by a real engineering project at Tadano.
For confidentiality reasons, all numerical data has been modified.
"""

import sqlite3
import numpy as np
from forces import make_F, rk4

def fetch_data():
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
    IT = mass_total * (a0 ** 2 + h0 ** 2)

    return {
        "x_cog": x_cog,
        "z_cog": z_cog,
        "radius": radius,
        "width": width,
        "mass_total": mass_total,
        "g": g,
        "IT": IT
    }

def tipping_time(i, v0, t_brake, Tsim, dt, vals):
    s_eff = 0.5 * v0 * t_brake
    F = make_F(
        s_eff,
        vals["IT"][i],
        vals["mass_total"][i],
        v0,
        vals["x_cog"][i],
        vals["z_cog"][i],
        vals["width"],
        vals["g"]
    )
    *_, t_tip = rk4(F, dt, Tsim, vals["x_cog"][i], vals["z_cog"][i], vals["width"])
    return t_tip is not None

def compute_vmax_tbrake(i, t_brake, Tsim, dt, vals, v_sup=10.0, eps=1e-3):
    def tip(v):
        return tipping_time(i, v, t_brake, Tsim, dt, vals)

    low = 0.05
    up = 0.1
    while up < v_sup and not tip(up):
        low = up
        up *= 1.5
    if up >= v_sup and not tip(up):
        return v_sup

    while (up - low) > eps:
        mid = 0.5 * (low + up)
        if tip(mid):
            up = mid
        else:
            low = mid
    return low

def main():
    vals = fetch_data()
    dt = 0.001
    Tsim = 5.0
    T_grid = np.arange(1, 2.1, 0.5)

    conn = sqlite3.connect("data/crane_vmax.sqlite")
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS analysis_time")
    cur.execute("""
        CREATE TABLE analysis_time(
            i INTEGER,
            radius REAL,
            t_brake REAL,
            vmax_ms REAL,
            vmax_kmh REAL,
            PRIMARY KEY (i, t_brake)
        )
    """)
    conn.commit()

    for i in range(len(vals["radius"])):
        R = vals["radius"][i]
        for t_b in T_grid:
            vmax = compute_vmax_tbrake(i, t_b, Tsim, dt, vals)
            cur.execute(
                "INSERT OR REPLACE INTO analysis_time(i, radius, t_brake, vmax_ms, vmax_kmh) "
                "VALUES (?, ?, ?, ?, ?)",
                (i, R, t_b, vmax, 3.6 * vmax)
            )
            print(
                f"i={i}, R={R:.1f} m, t_b={t_b:.1f} s : "
                f"vmax={vmax:.3f} m/s ({3.6 * vmax:.2f} km/h)"
            )

        conn.commit()

    conn.close()
    print("done")

if __name__ == "__main__":
    main()
