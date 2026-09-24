"""
This script simulates crane tipping conditions under braking.
It uses parameters inspired by a real engineering project at Tadano.
For confidentiality reasons, all numerical data has been modified.

Two tables are (re)generated in the database:
    - analysis      : vmax as a function of the braking distance s_brake
    - analysis_time : vmax as a function of the braking time t_brake
"""

import sqlite3
import numpy as np
from parameters import get_values, DB_PATH
from forces import make_F, rk4

def tips(i, v0, s_brake, Tsim, dt, vals):
    F = make_F(
        s_brake,
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

def tipping_time(i, v0, t_brake, Tsim, dt, vals):
    # constant deceleration : s = v0 * t / 2
    s_eff = 0.5 * v0 * t_brake
    return tips(i, v0, s_eff, Tsim, dt, vals)

def compute_vmax(tip, v_sup=10.0, eps=1e-3):
    low = 0.0
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

def compute_vmax_tbrake(i, t_brake, Tsim, dt, vals, v_sup=10.0, eps=1e-3):
    return compute_vmax(lambda v: tipping_time(i, v, t_brake, Tsim, dt, vals), v_sup, eps)

def compute_vmax_sbrake(i, s_brake, Tsim, dt, vals, v_sup=10.0, eps=1e-3):
    return compute_vmax(lambda v: tips(i, v, s_brake, Tsim, dt, vals), v_sup, eps)

def fill_table(cur, table, column, grid, compute, vals, Tsim, dt):
    cur.execute(f"DROP TABLE IF EXISTS {table}")
    cur.execute(f"""
        CREATE TABLE {table}(
            i INTEGER,
            radius REAL,
            {column} REAL,
            vmax_ms REAL,
            vmax_kmh REAL,
            PRIMARY KEY (i, {column})
        )
    """)

    for i in range(len(vals["radius"])):
        R = vals["radius"][i]
        for x in grid:
            vmax = compute(i, float(x), Tsim, dt, vals)
            cur.execute(
                f"INSERT OR REPLACE INTO {table}(i, radius, {column}, vmax_ms, vmax_kmh) "
                "VALUES (?, ?, ?, ?, ?)",
                (i, R, float(x), vmax, 3.6 * vmax)
            )
            print(
                f"i={i}, R={R:.1f} m, {column}={x:.1f} : "
                f"vmax={vmax:.3f} m/s ({3.6 * vmax:.2f} km/h)"
            )

def main():
    vals = get_values()
    dt = 0.001
    Tsim = 5.0
    S_grid = np.arange(0.5, 10.01, 0.5)
    T_grid = np.arange(1, 2.1, 0.5)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    fill_table(cur, "analysis", "s_brake", S_grid, compute_vmax_sbrake, vals, Tsim, dt)
    conn.commit()
    fill_table(cur, "analysis_time", "t_brake", T_grid, compute_vmax_tbrake, vals, Tsim, dt)
    conn.commit()

    conn.close()
    print("done")

if __name__ == "__main__":
    main()
