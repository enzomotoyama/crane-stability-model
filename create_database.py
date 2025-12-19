import sqlite3
import numpy as np
from forces import make_F, rk4


def fetch_data():
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
    IT = mass_total*(a0*a0 + h0*h0)
    return {
        "x_cog": x_cog, # 0
        "z_cog": z_cog, # 1
        "radius": radius, # 2 
        "width": width, # 3 
        "mass_total": mass_total, # 4 
        "g": g, # 5
        "IT": IT # 6
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

    T_grid = np.arange(1, 2 + 1e-12, 0.5)

    conn = sqlite3.connect("crane_vmax.sqlite")
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
                (i, R, t_b, vmax, 3.6*vmax)
            )

            print(
                f"i={i}, R={R:.1f} m, t_b={t_b:.1f} s : "
                f"vmax={vmax:.3f} m/s ({3.6*vmax:.2f} km/h)"
            )

        conn.commit()

    conn.close()
    print("done")


if __name__ == "__main__":
    main()



"""
i=0, R=10.0 m, s_b=0.5 m : vmax=1.497 m/s (5.39 km/h)
i=0, R=10.0 m, s_b=1.0 m : vmax=1.706 m/s (6.14 km/h)
i=0, R=10.0 m, s_b=1.5 m : vmax=1.891 m/s (6.81 km/h)
i=0, R=10.0 m, s_b=2.0 m : vmax=2.060 m/s (7.42 km/h)
i=0, R=10.0 m, s_b=2.5 m : vmax=2.217 m/s (7.98 km/h)
i=0, R=10.0 m, s_b=3.0 m : vmax=2.363 m/s (8.51 km/h)
i=0, R=10.0 m, s_b=3.5 m : vmax=2.504 m/s (9.01 km/h)
i=0, R=10.0 m, s_b=4.0 m : vmax=2.637 m/s (9.49 km/h)
i=0, R=10.0 m, s_b=4.5 m : vmax=2.765 m/s (9.95 km/h)
i=0, R=10.0 m, s_b=5.0 m : vmax=2.888 m/s (10.40 km/h)
i=0, R=10.0 m, s_b=5.5 m : vmax=3.008 m/s (10.83 km/h)
i=0, R=10.0 m, s_b=6.0 m : vmax=3.124 m/s (11.25 km/h)
i=0, R=10.0 m, s_b=6.5 m : vmax=3.237 m/s (11.65 km/h)
i=0, R=10.0 m, s_b=7.0 m : vmax=3.348 m/s (12.05 km/h)
i=0, R=10.0 m, s_b=7.5 m : vmax=3.456 m/s (12.44 km/h)
i=0, R=10.0 m, s_b=8.0 m : vmax=3.563 m/s (12.83 km/h)
i=0, R=10.0 m, s_b=8.5 m : vmax=3.667 m/s (13.20 km/h)
i=0, R=10.0 m, s_b=9.0 m : vmax=3.771 m/s (13.57 km/h)
i=0, R=10.0 m, s_b=9.5 m : vmax=3.872 m/s (13.94 km/h)
i=0, R=10.0 m, s_b=10.0 m : vmax=3.972 m/s (14.30 km/h)
i=1, R=11.0 m, s_b=0.5 m : vmax=1.476 m/s (5.31 km/h)
i=1, R=11.0 m, s_b=1.0 m : vmax=1.689 m/s (6.08 km/h)
i=1, R=11.0 m, s_b=1.5 m : vmax=1.875 m/s (6.75 km/h)
i=1, R=11.0 m, s_b=2.0 m : vmax=2.046 m/s (7.37 km/h)
i=1, R=11.0 m, s_b=2.5 m : vmax=2.204 m/s (7.93 km/h)
i=1, R=11.0 m, s_b=3.0 m : vmax=2.353 m/s (8.47 km/h)
i=1, R=11.0 m, s_b=3.5 m : vmax=2.493 m/s (8.97 km/h)
i=1, R=11.0 m, s_b=4.0 m : vmax=2.627 m/s (9.46 km/h)
i=1, R=11.0 m, s_b=4.5 m : vmax=2.756 m/s (9.92 km/h)
i=1, R=11.0 m, s_b=5.0 m : vmax=2.879 m/s (10.37 km/h)
i=1, R=11.0 m, s_b=5.5 m : vmax=3.000 m/s (10.80 km/h)
i=1, R=11.0 m, s_b=6.0 m : vmax=3.117 m/s (11.22 km/h)
i=1, R=11.0 m, s_b=6.5 m : vmax=3.230 m/s (11.63 km/h)
i=1, R=11.0 m, s_b=7.0 m : vmax=3.341 m/s (12.03 km/h)
i=1, R=11.0 m, s_b=7.5 m : vmax=3.450 m/s (12.42 km/h)
i=1, R=11.0 m, s_b=8.0 m : vmax=3.556 m/s (12.80 km/h)
i=1, R=11.0 m, s_b=8.5 m : vmax=3.660 m/s (13.18 km/h)
i=1, R=11.0 m, s_b=9.0 m : vmax=3.764 m/s (13.55 km/h)
i=1, R=11.0 m, s_b=9.5 m : vmax=3.865 m/s (13.91 km/h)
i=1, R=11.0 m, s_b=10.0 m : vmax=3.965 m/s (14.28 km/h)
i=2, R=12.0 m, s_b=0.5 m : vmax=1.451 m/s (5.22 km/h)
i=2, R=12.0 m, s_b=1.0 m : vmax=1.665 m/s (5.99 km/h)
i=2, R=12.0 m, s_b=1.5 m : vmax=1.854 m/s (6.67 km/h)
i=2, R=12.0 m, s_b=2.0 m : vmax=2.026 m/s (7.29 km/h)
i=2, R=12.0 m, s_b=2.5 m : vmax=2.185 m/s (7.87 km/h)
i=2, R=12.0 m, s_b=3.0 m : vmax=2.334 m/s (8.40 km/h)
i=2, R=12.0 m, s_b=3.5 m : vmax=2.475 m/s (8.91 km/h)
i=2, R=12.0 m, s_b=4.0 m : vmax=2.610 m/s (9.40 km/h)
i=2, R=12.0 m, s_b=4.5 m : vmax=2.739 m/s (9.86 km/h)
i=2, R=12.0 m, s_b=5.0 m : vmax=2.863 m/s (10.31 km/h)
i=2, R=12.0 m, s_b=5.5 m : vmax=2.983 m/s (10.74 km/h)
i=2, R=12.0 m, s_b=6.0 m : vmax=3.100 m/s (11.16 km/h)
i=2, R=12.0 m, s_b=6.5 m : vmax=3.214 m/s (11.57 km/h)
i=2, R=12.0 m, s_b=7.0 m : vmax=3.324 m/s (11.97 km/h)
i=2, R=12.0 m, s_b=7.5 m : vmax=3.433 m/s (12.36 km/h)
i=2, R=12.0 m, s_b=8.0 m : vmax=3.540 m/s (12.74 km/h)
i=2, R=12.0 m, s_b=8.5 m : vmax=3.644 m/s (13.12 km/h)
i=2, R=12.0 m, s_b=9.0 m : vmax=3.747 m/s (13.49 km/h)
i=2, R=12.0 m, s_b=9.5 m : vmax=3.848 m/s (13.85 km/h)
i=2, R=12.0 m, s_b=10.0 m : vmax=3.948 m/s (14.21 km/h)
i=3, R=13.0 m, s_b=0.5 m : vmax=1.422 m/s (5.12 km/h)
i=3, R=13.0 m, s_b=1.0 m : vmax=1.639 m/s (5.90 km/h)
i=3, R=13.0 m, s_b=1.5 m : vmax=1.830 m/s (6.59 km/h)
i=3, R=13.0 m, s_b=2.0 m : vmax=2.002 m/s (7.21 km/h)
i=3, R=13.0 m, s_b=2.5 m : vmax=2.162 m/s (7.78 km/h)
i=3, R=13.0 m, s_b=3.0 m : vmax=2.312 m/s (8.32 km/h)
i=3, R=13.0 m, s_b=3.5 m : vmax=2.453 m/s (8.83 km/h)
i=3, R=13.0 m, s_b=4.0 m : vmax=2.588 m/s (9.32 km/h)
i=3, R=13.0 m, s_b=4.5 m : vmax=2.717 m/s (9.78 km/h)
i=3, R=13.0 m, s_b=5.0 m : vmax=2.841 m/s (10.23 km/h)
i=3, R=13.0 m, s_b=5.5 m : vmax=2.961 m/s (10.66 km/h)
i=3, R=13.0 m, s_b=6.0 m : vmax=3.078 m/s (11.08 km/h)
i=3, R=13.0 m, s_b=6.5 m : vmax=3.192 m/s (11.49 km/h)
i=3, R=13.0 m, s_b=7.0 m : vmax=3.303 m/s (11.89 km/h)
i=3, R=13.0 m, s_b=7.5 m : vmax=3.411 m/s (12.28 km/h)
i=3, R=13.0 m, s_b=8.0 m : vmax=3.518 m/s (12.66 km/h)
i=3, R=13.0 m, s_b=8.5 m : vmax=3.622 m/s (13.04 km/h)
i=3, R=13.0 m, s_b=9.0 m : vmax=3.724 m/s (13.41 km/h)
i=3, R=13.0 m, s_b=9.5 m : vmax=3.826 m/s (13.77 km/h)
i=3, R=13.0 m, s_b=10.0 m : vmax=3.925 m/s (14.13 km/h)
i=4, R=14.0 m, s_b=0.5 m : vmax=1.390 m/s (5.00 km/h)
i=4, R=14.0 m, s_b=1.0 m : vmax=1.609 m/s (5.79 km/h)
i=4, R=14.0 m, s_b=1.5 m : vmax=1.800 m/s (6.48 km/h)
i=4, R=14.0 m, s_b=2.0 m : vmax=1.974 m/s (7.11 km/h)
i=4, R=14.0 m, s_b=2.5 m : vmax=2.134 m/s (7.68 km/h)
i=4, R=14.0 m, s_b=3.0 m : vmax=2.284 m/s (8.22 km/h)
i=4, R=14.0 m, s_b=3.5 m : vmax=2.426 m/s (8.73 km/h)
i=4, R=14.0 m, s_b=4.0 m : vmax=2.560 m/s (9.22 km/h)
i=4, R=14.0 m, s_b=4.5 m : vmax=2.690 m/s (9.68 km/h)
i=4, R=14.0 m, s_b=5.0 m : vmax=2.814 m/s (10.13 km/h)
i=4, R=14.0 m, s_b=5.5 m : vmax=2.935 m/s (10.56 km/h)
i=4, R=14.0 m, s_b=6.0 m : vmax=3.051 m/s (10.98 km/h)
i=4, R=14.0 m, s_b=6.5 m : vmax=3.165 m/s (11.39 km/h)
i=4, R=14.0 m, s_b=7.0 m : vmax=3.275 m/s (11.79 km/h)
i=4, R=14.0 m, s_b=7.5 m : vmax=3.383 m/s (12.18 km/h)
i=4, R=14.0 m, s_b=8.0 m : vmax=3.489 m/s (12.56 km/h)
i=4, R=14.0 m, s_b=8.5 m : vmax=3.593 m/s (12.93 km/h)
i=4, R=14.0 m, s_b=9.0 m : vmax=3.695 m/s (13.30 km/h)
i=4, R=14.0 m, s_b=9.5 m : vmax=3.796 m/s (13.67 km/h)
i=4, R=14.0 m, s_b=10.0 m : vmax=3.894 m/s (14.02 km/h)
i=5, R=15.0 m, s_b=0.5 m : vmax=1.352 m/s (4.87 km/h)
i=5, R=15.0 m, s_b=1.0 m : vmax=1.572 m/s (5.66 km/h)
i=5, R=15.0 m, s_b=1.5 m : vmax=1.764 m/s (6.35 km/h)
i=5, R=15.0 m, s_b=2.0 m : vmax=1.938 m/s (6.98 km/h)
i=5, R=15.0 m, s_b=2.5 m : vmax=2.098 m/s (7.55 km/h)
i=5, R=15.0 m, s_b=3.0 m : vmax=2.248 m/s (8.09 km/h)
i=5, R=15.0 m, s_b=3.5 m : vmax=2.389 m/s (8.60 km/h)
i=5, R=15.0 m, s_b=4.0 m : vmax=2.524 m/s (9.09 km/h)
i=5, R=15.0 m, s_b=4.5 m : vmax=2.652 m/s (9.55 km/h)
i=5, R=15.0 m, s_b=5.0 m : vmax=2.776 m/s (9.99 km/h)
i=5, R=15.0 m, s_b=5.5 m : vmax=2.896 m/s (10.42 km/h)
i=5, R=15.0 m, s_b=6.0 m : vmax=3.012 m/s (10.84 km/h)
i=5, R=15.0 m, s_b=6.5 m : vmax=3.124 m/s (11.25 km/h)
i=5, R=15.0 m, s_b=7.0 m : vmax=3.234 m/s (11.64 km/h)
i=5, R=15.0 m, s_b=7.5 m : vmax=3.342 m/s (12.03 km/h)
i=5, R=15.0 m, s_b=8.0 m : vmax=3.447 m/s (12.41 km/h)
i=5, R=15.0 m, s_b=8.5 m : vmax=3.550 m/s (12.78 km/h)
i=5, R=15.0 m, s_b=9.0 m : vmax=3.652 m/s (13.15 km/h)
i=5, R=15.0 m, s_b=9.5 m : vmax=3.752 m/s (13.51 km/h)
i=5, R=15.0 m, s_b=10.0 m : vmax=3.849 m/s (13.86 km/h)
i=6, R=16.0 m, s_b=0.5 m : vmax=1.312 m/s (4.72 km/h)
i=6, R=16.0 m, s_b=1.0 m : vmax=1.534 m/s (5.52 km/h)
i=6, R=16.0 m, s_b=1.5 m : vmax=1.727 m/s (6.22 km/h)
i=6, R=16.0 m, s_b=2.0 m : vmax=1.900 m/s (6.84 km/h)
i=6, R=16.0 m, s_b=2.5 m : vmax=2.060 m/s (7.42 km/h)
i=6, R=16.0 m, s_b=3.0 m : vmax=2.209 m/s (7.95 km/h)
i=6, R=16.0 m, s_b=3.5 m : vmax=2.350 m/s (8.46 km/h)
i=6, R=16.0 m, s_b=4.0 m : vmax=2.484 m/s (8.94 km/h)
i=6, R=16.0 m, s_b=4.5 m : vmax=2.612 m/s (9.40 km/h)
i=6, R=16.0 m, s_b=5.0 m : vmax=2.736 m/s (9.85 km/h)
i=6, R=16.0 m, s_b=5.5 m : vmax=2.854 m/s (10.28 km/h)
i=6, R=16.0 m, s_b=6.0 m : vmax=2.970 m/s (10.69 km/h)
i=6, R=16.0 m, s_b=6.5 m : vmax=3.082 m/s (11.10 km/h)
i=6, R=16.0 m, s_b=7.0 m : vmax=3.192 m/s (11.49 km/h)
i=6, R=16.0 m, s_b=7.5 m : vmax=3.298 m/s (11.87 km/h)
i=6, R=16.0 m, s_b=8.0 m : vmax=3.403 m/s (12.25 km/h)
i=6, R=16.0 m, s_b=8.5 m : vmax=3.505 m/s (12.62 km/h)
i=6, R=16.0 m, s_b=9.0 m : vmax=3.607 m/s (12.98 km/h)
i=6, R=16.0 m, s_b=9.5 m : vmax=3.705 m/s (13.34 km/h)
i=6, R=16.0 m, s_b=10.0 m : vmax=3.802 m/s (13.69 km/h)
i=7, R=17.0 m, s_b=0.5 m : vmax=1.337 m/s (4.81 km/h)
i=7, R=17.0 m, s_b=1.0 m : vmax=1.563 m/s (5.63 km/h)
i=7, R=17.0 m, s_b=1.5 m : vmax=1.759 m/s (6.33 km/h)
i=7, R=17.0 m, s_b=2.0 m : vmax=1.936 m/s (6.97 km/h)
i=7, R=17.0 m, s_b=2.5 m : vmax=2.099 m/s (7.56 km/h)
i=7, R=17.0 m, s_b=3.0 m : vmax=2.251 m/s (8.10 km/h)
i=7, R=17.0 m, s_b=3.5 m : vmax=2.394 m/s (8.62 km/h)
i=7, R=17.0 m, s_b=4.0 m : vmax=2.530 m/s (9.11 km/h)
i=7, R=17.0 m, s_b=4.5 m : vmax=2.661 m/s (9.58 km/h)
i=7, R=17.0 m, s_b=5.0 m : vmax=2.786 m/s (10.03 km/h)
i=7, R=17.0 m, s_b=5.5 m : vmax=2.907 m/s (10.47 km/h)
i=7, R=17.0 m, s_b=6.0 m : vmax=3.024 m/s (10.89 km/h)
i=7, R=17.0 m, s_b=6.5 m : vmax=3.137 m/s (11.29 km/h)
i=7, R=17.0 m, s_b=7.0 m : vmax=3.248 m/s (11.69 km/h)
i=7, R=17.0 m, s_b=7.5 m : vmax=3.356 m/s (12.08 km/h)
i=7, R=17.0 m, s_b=8.0 m : vmax=3.462 m/s (12.46 km/h)
i=7, R=17.0 m, s_b=8.5 m : vmax=3.566 m/s (12.84 km/h)
i=7, R=17.0 m, s_b=9.0 m : vmax=3.668 m/s (13.20 km/h)
i=7, R=17.0 m, s_b=9.5 m : vmax=3.768 m/s (13.56 km/h)
i=7, R=17.0 m, s_b=10.0 m : vmax=3.866 m/s (13.92 km/h)
i=8, R=18.0 m, s_b=0.5 m : vmax=1.295 m/s (4.66 km/h)
i=8, R=18.0 m, s_b=1.0 m : vmax=1.522 m/s (5.48 km/h)
i=8, R=18.0 m, s_b=1.5 m : vmax=1.718 m/s (6.18 km/h)
i=8, R=18.0 m, s_b=2.0 m : vmax=1.894 m/s (6.82 km/h)
i=8, R=18.0 m, s_b=2.5 m : vmax=2.056 m/s (7.40 km/h)
i=8, R=18.0 m, s_b=3.0 m : vmax=2.207 m/s (7.95 km/h)
i=8, R=18.0 m, s_b=3.5 m : vmax=2.350 m/s (8.46 km/h)
i=8, R=18.0 m, s_b=4.0 m : vmax=2.485 m/s (8.95 km/h)
i=8, R=18.0 m, s_b=4.5 m : vmax=2.615 m/s (9.41 km/h)
i=8, R=18.0 m, s_b=5.0 m : vmax=2.739 m/s (9.86 km/h)
i=8, R=18.0 m, s_b=5.5 m : vmax=2.859 m/s (10.29 km/h)
i=8, R=18.0 m, s_b=6.0 m : vmax=2.975 m/s (10.71 km/h)
i=8, R=18.0 m, s_b=6.5 m : vmax=3.088 m/s (11.12 km/h)
i=8, R=18.0 m, s_b=7.0 m : vmax=3.198 m/s (11.51 km/h)
i=8, R=18.0 m, s_b=7.5 m : vmax=3.305 m/s (11.90 km/h)
i=8, R=18.0 m, s_b=8.0 m : vmax=3.410 m/s (12.28 km/h)
i=8, R=18.0 m, s_b=8.5 m : vmax=3.513 m/s (12.65 km/h)
i=8, R=18.0 m, s_b=9.0 m : vmax=3.614 m/s (13.01 km/h)
i=8, R=18.0 m, s_b=9.5 m : vmax=3.713 m/s (13.37 km/h)
i=8, R=18.0 m, s_b=10.0 m : vmax=3.810 m/s (13.72 km/h)
i=9, R=19.0 m, s_b=0.5 m : vmax=1.316 m/s (4.74 km/h)
i=9, R=19.0 m, s_b=1.0 m : vmax=1.546 m/s (5.56 km/h)
i=9, R=19.0 m, s_b=1.5 m : vmax=1.745 m/s (6.28 km/h)
i=9, R=19.0 m, s_b=2.0 m : vmax=1.925 m/s (6.93 km/h)
i=9, R=19.0 m, s_b=2.5 m : vmax=2.089 m/s (7.52 km/h)
i=9, R=19.0 m, s_b=3.0 m : vmax=2.243 m/s (8.07 km/h)
i=9, R=19.0 m, s_b=3.5 m : vmax=2.387 m/s (8.59 km/h)
i=9, R=19.0 m, s_b=4.0 m : vmax=2.525 m/s (9.09 km/h)
i=9, R=19.0 m, s_b=4.5 m : vmax=2.656 m/s (9.56 km/h)
i=9, R=19.0 m, s_b=5.0 m : vmax=2.782 m/s (10.01 km/h)
i=9, R=19.0 m, s_b=5.5 m : vmax=2.903 m/s (10.45 km/h)
i=9, R=19.0 m, s_b=6.0 m : vmax=3.021 m/s (10.88 km/h)
i=9, R=19.0 m, s_b=6.5 m : vmax=3.135 m/s (11.29 km/h)
i=9, R=19.0 m, s_b=7.0 m : vmax=3.246 m/s (11.69 km/h)
i=9, R=19.0 m, s_b=7.5 m : vmax=3.354 m/s (12.08 km/h)
i=9, R=19.0 m, s_b=8.0 m : vmax=3.461 m/s (12.46 km/h)
i=9, R=19.0 m, s_b=8.5 m : vmax=3.565 m/s (12.83 km/h)
i=9, R=19.0 m, s_b=9.0 m : vmax=3.667 m/s (13.20 km/h)
i=9, R=19.0 m, s_b=9.5 m : vmax=3.767 m/s (13.56 km/h)
i=9, R=19.0 m, s_b=10.0 m : vmax=3.864 m/s (13.91 km/h)
i=10, R=20.0 m, s_b=0.5 m : vmax=1.265 m/s (4.56 km/h)
i=10, R=20.0 m, s_b=1.0 m : vmax=1.496 m/s (5.38 km/h)
i=10, R=20.0 m, s_b=1.5 m : vmax=1.694 m/s (6.10 km/h)
i=10, R=20.0 m, s_b=2.0 m : vmax=1.872 m/s (6.74 km/h)
i=10, R=20.0 m, s_b=2.5 m : vmax=2.035 m/s (7.33 km/h)
i=10, R=20.0 m, s_b=3.0 m : vmax=2.187 m/s (7.87 km/h)
i=10, R=20.0 m, s_b=3.5 m : vmax=2.330 m/s (8.39 km/h)
i=10, R=20.0 m, s_b=4.0 m : vmax=2.466 m/s (8.88 km/h)
i=10, R=20.0 m, s_b=4.5 m : vmax=2.596 m/s (9.35 km/h)
i=10, R=20.0 m, s_b=5.0 m : vmax=2.721 m/s (9.79 km/h)
i=10, R=20.0 m, s_b=5.5 m : vmax=2.841 m/s (10.23 km/h)
i=10, R=20.0 m, s_b=6.0 m : vmax=2.957 m/s (10.65 km/h)
i=10, R=20.0 m, s_b=6.5 m : vmax=3.070 m/s (11.05 km/h)
i=10, R=20.0 m, s_b=7.0 m : vmax=3.180 m/s (11.45 km/h)
i=10, R=20.0 m, s_b=7.5 m : vmax=3.287 m/s (11.83 km/h)
i=10, R=20.0 m, s_b=8.0 m : vmax=3.391 m/s (12.21 km/h)
i=10, R=20.0 m, s_b=8.5 m : vmax=3.494 m/s (12.58 km/h)
i=10, R=20.0 m, s_b=9.0 m : vmax=3.595 m/s (12.94 km/h)
i=10, R=20.0 m, s_b=9.5 m : vmax=3.694 m/s (13.30 km/h)
i=10, R=20.0 m, s_b=10.0 m : vmax=3.789 m/s (13.64 km/h)



"""