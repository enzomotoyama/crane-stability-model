"""
Generates the README figures in figures/ :
    - braking_trajectory.png : tipping angle during braking, stable vs tipping case
    - monte_carlo.png        : distribution of vmax over random braking times

Reuses the simulation code as is (no change to the physics).
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parameters import get_values
from forces import make_F, rk4
from create_database import compute_vmax_tbrake
from monte_carlo_sim import sample_t_brake, T_MIN, T_MAX

SEED = 12345
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")

ISO_LIMIT_KMH = 1.1
TIP_ANGLE_DEG = 90.0

# braking trajectory
I_TRAJ = 0              # radius = 10 m
T_BRAKE_TRAJ = 1.5      # s
SPEEDS_KMH = [5.0, 7.0] # one below, one above vmax for this configuration

# Monte Carlo
I_MC = 5                # radius = 15 m
N_MC = 400
T_MEAN, T_STD = 1.5, 0.3
TSIM_MC, DT_MC, EPS_MC = 15.0, 0.004, 1e-2

plt.rcParams.update({
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def trajectory(vals, i, v0, t_brake, Tsim=15.0, dt=1e-3):
    # same effective braking distance as create_database.tipping_time
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
    times, phi_deg, _, _, t_tip = rk4(F, dt, Tsim, vals["x_cog"][i], vals["z_cog"][i], vals["width"])
    return times, phi_deg, t_tip


def plot_braking_trajectory(vals, path):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    styles = [("0.35", "-"), ("black", "--")]

    for (color, ls), kmh in zip(styles, SPEEDS_KMH):
        times, phi_deg, t_tip = trajectory(vals, I_TRAJ, kmh / 3.6, T_BRAKE_TRAJ)
        label = f"v0 = {kmh:.0f} km/h ({'tips' if t_tip is not None else 'stable'})"
        ax.plot(times, phi_deg, color=color, ls=ls, lw=1.8, label=label)
        if t_tip is not None:
            ax.plot(t_tip, TIP_ANGLE_DEG, marker="o", ms=7, mfc="white", mec="black", mew=1.5, zorder=3)
            ax.annotate(f"tipping at t = {t_tip:.2f} s", xy=(t_tip, TIP_ANGLE_DEG),
                        xytext=(t_tip + 0.4, TIP_ANGLE_DEG - 1.6),
                        arrowprops=dict(arrowstyle="->", color="black", lw=0.8))

    ax.axhline(TIP_ANGLE_DEG, color="black", ls=":", lw=1.2)
    ax.text(0.02, TIP_ANGLE_DEG + 0.25, "tipping angle (COG above the front edge, 90°)",
            transform=ax.get_yaxis_transform(), va="bottom", fontsize=9)

    ax.set_xlabel("time (s)")
    ax.set_ylabel("angle of the edge-to-COG line with the ground (deg)")
    ax.set_ylim(top=TIP_ANGLE_DEG + 1.5)
    ax.set_title(f"Emergency braking, radius R = {vals['radius'][I_TRAJ]:.0f} m, braking time {T_BRAKE_TRAJ} s")
    ax.legend(loc="lower left", frameon=False)
    ax.grid(True, color="0.9", lw=0.6)

    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_monte_carlo(vals, path):
    rng = np.random.default_rng(SEED)
    t_draws = sample_t_brake(T_MEAN, T_STD, N_MC, rng=rng, tmin=T_MIN, tmax=T_MAX)
    vmax_kmh = 3.6 * np.array([
        compute_vmax_tbrake(I_MC, float(t_b), TSIM_MC, DT_MC, vals, eps=EPS_MC) for t_b in t_draws
    ])
    median = float(np.median(vmax_kmh))

    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.hist(vmax_kmh, bins=25, color="0.8", edgecolor="black", lw=0.6, hatch="//")

    ax.axvline(median, color="black", ls="--", lw=1.4)
    ax.axvline(ISO_LIMIT_KMH, color="black", ls=":", lw=1.4)
    ymax = ax.get_ylim()[1] * 1.12
    ax.set_ylim(top=ymax)
    ax.text(median, ymax * 0.97, f"  median = {median:.2f} km/h", va="top", ha="left", fontsize=9)
    ax.text(ISO_LIMIT_KMH, ymax * 0.97, f"  ISO 4305 limit\n  = {ISO_LIMIT_KMH} km/h", va="top", ha="left", fontsize=9)

    ax.set_xlim(0, np.ceil(vmax_kmh.max()) + 0.5)
    ax.set_xlabel("maximum safe travel speed vmax (km/h)")
    ax.set_ylabel("number of simulations")
    ax.set_title(f"Monte Carlo, R = {vals['radius'][I_MC]:.0f} m, N = {N_MC}, "
                 f"braking time ~ N({T_MEAN} s, {T_STD} s)")
    ax.grid(True, axis="y", color="0.9", lw=0.6)

    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return vmax_kmh


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    vals = get_values()

    plot_braking_trajectory(vals, os.path.join(OUT_DIR, "braking_trajectory.png"))
    print("figures/braking_trajectory.png done")

    vmax_kmh = plot_monte_carlo(vals, os.path.join(OUT_DIR, "monte_carlo.png"))
    q05, q50, q95 = np.quantile(vmax_kmh, [0.05, 0.50, 0.95])
    print(f"figures/monte_carlo.png done : q05={q05:.2f}, median={q50:.2f}, q95={q95:.2f} km/h")

if __name__ == "__main__":
    main()
