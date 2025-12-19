import matplotlib.pyplot as plt
import numpy as np
import sqlite3


def plot_phi(times, phi_phys):
    times = np.asarray(times)
    phi   = np.asarray(phi_phys)

    phi_plot = np.clip(phi, 0.0, 90.0)

    plt.figure(figsize=(8,5))
    plt.plot(times, phi_plot, label="phi (physical)")

    idx_tip = np.where(np.isclose(phi_plot, 90.0, atol=1e-6))[0]
    if idx_tip.size > 0:
        it = idx_tip[0]
        plt.plot(times[it], phi_plot[it], marker='o', markersize=6, label="tipping point")

    plt.axhline(90, color='red', linestyle='--', label="90° tipping")
    plt.xlabel("time (s)")
    plt.ylabel("phi (deg)")
    plt.title("Rotation angle over time")
    plt.grid(True)
    plt.legend()
    plt.show()

def plot_scatter(v_list, phi_max_list, tipping_list):
    plt.figure(figsize=(8,6))

    v = np.array(v_list, dtype=float)
    phi = np.array(phi_max_list, dtype=float)
    tip = np.array(tipping_list, dtype=int)

    # clip visuel dans [0, 90]
    phi = np.clip(phi, 0.0, 90.0)

    plt.scatter(v[tip == 1], phi[tip == 1], c="red", label="tipping")
    plt.scatter(v[tip == 0], phi[tip == 0], c="green", label="stable")

    plt.axhline(90, color="black", linestyle="--", label="tipping limit (90°)")
    plt.xlabel("initial velocity (m/s)")
    plt.ylabel("max angle (deg)")
    plt.title("Tipping vs initial speed")
    plt.grid(True)
    plt.legend()
    plt.show()


def plot_vmax_vs_radius(radius_list, vmax_list):
    plt.figure(figsize=(8,6))
    plt.plot(radius_list, vmax_list)
    plt.grid(True)
    plt.xlabel("radius (m)")
    plt.ylabel("max safe v0 (m/s)")
    plt.title("max safe v0 vs radius")
    plt.show()



def plot_s_b_vs_vmax(path, i = 0, smin = 0.5, smax = 5):
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT s_brake , vmax_kmh FROM analysis where i = ? AND s_brake BETWEEN ? AND ? ORDER BY s_brake ASC",
        (i,smin,smax)
    )
    rows = cursor.fetchall()
    connection.close()

    if not rows:
        raise ValueError("no rows found")

    s_b = np.array([r[0] for r in rows])
    vmax_kmh = np.array([r[1] for r in rows])

    plt.figure(figsize=(8,6))
    plt.plot(s_b,vmax_kmh)
    plt.grid(True)
    plt.xlabel("s_brake(m)")
    plt.ylabel("vmax (km/h)")
    plt.title("vmax vs s_brake")
    plt.show()  