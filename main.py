"""
Here, we are in a real data case.

We want to know what speed the crane can reach in order to brake without tipping.

IMPORTANT PARAMETERS :

    the crane moves from the right to the left 

    - 0 : the zero here is the center of the crane, i.e at width / 2
    - x_cog : horizontal coordinate of the COG
    - z_cog : vertical coordinate of the COG
    - T : tipping point (front of the crane)
    - phi_model : is the  "added" angle rotation that we solve in rk4 ( ex from 85 deg to 89 deg -> phi_model = 4 deg) (phidd ---> we get phi)
    - phi_init : real angle on the drawing initially
    - phi_phys : final angle  after braking (we use it to check if a tipping happens or no)
    - IT = IG +mr**2 but we suppose that IG = 0
    - for the moments : clockwise -> positive
"""
import pandas as pd
import numpy as np
from parameters import get_values
from forces import make_F, rk4
from plotting import plot_phi, plot_scatter, plot_s_b_vs_vmax

vals = get_values()

x_cog = vals["x_cog"]
z_cog = vals["z_cog"]
width = vals["width"]
mass_total = vals["mass_total"]
g = vals["g"]
IT = vals["IT"]
radius = vals["radius"]

ans = str(input("\ndo you want to plot the graphs ? yes or no : "))
while ans != "yes" and ans != "no":
    ans = str(input("yes or no"))


run_mc = str(input(" \ndo you want to run the mc simulation ? yes or no : "))
while run_mc != "yes" and run_mc != "no":
    run_mc = str(input("yes or no"))


if run_mc == "yes": 

    from monte_carlo_sim import vmax_for_i_tbrake, quantiles_by_radius
    import time
    N = int(input("how many simulations for Monte Carlo "))
    t_mean = float(input("mean for the braking time : "))
    t_std = float(input("std between the values of the braking time : "))
    print("\n Monte carlo simulation  starts ... ", flush=True)
    t0 = time.time()


    df_list = []
    for j in range(len(radius)):
        df_j = vmax_for_i_tbrake(j, t_mean, t_std, N)
        df_list.append(df_j)

    df_all = pd.concat(df_list, ignore_index=True)
    summary = quantiles_by_radius(df_all).sort_values("radius")
    result = summary[["i", "radius", "N", "mean", "std", "q05", "q50", "q95"]].round(3)

    print(f"simulation done in {round(time.time()-t0, 2)} s")
    print("\n === Monte Carlo output in km / h by radius ===")
    print(result)


if ans == "yes":
    i = int(input("choose a line index (from 0 to 10): "))

    print("Radius:", radius[i])
    print("x_cog:", x_cog[i])
    print("z_cog:", z_cog[i])

    n = int(input("how many values of v0 to test : "))
    v0_list = []
    for _ in range(n):
        val = float(input("initial velocity in km/h (will convert it in m/s) : "))
        v0_list.append(val / 3.6)

    s_brake = float(input("Braking distance s_b (m): "))
    Tsim = 15.0
    dt = 0.001

    tipping_list = []
    phi_max_list = []
    v_list = []

    for v0 in v0_list:
        F = make_F(
            s_brake,
            IT[i],
            mass_total[i],
            v0,
            x_cog[i],
            z_cog[i],
            width,
            g
        )

        times, phi_deg, phi_model, dphi_model, t_tip = rk4(
            F,
            dt,
            Tsim,
            x_cog[i],
            z_cog[i],
            width
        )

        phi_max = float(np.max(phi_deg))

        v_list.append(v0)
        phi_max_list.append(phi_max)
        tipping_list.append(1 if t_tip is not None else 0)

        print(f"\n--- Initial velocity : {v0:.3f} m/s ({v0*3.6:.2f} km/h) ---")
        print("Max angle (deg):", phi_max)
        print("Tipping time :", t_tip)

        plot_phi(times, phi_deg)

        if t_tip is not None:
            print("tipping")
        else:
            if phi_deg[-1] < phi_deg[0]:
                print("system falls back : stable")
            else:
                print("moves forward but NO tipping")

    plot_scatter(v_list, phi_max_list, tipping_list)

    safe_speeds = [v_list[k] for k in range(len(v_list)) if tipping_list[k] == 0]

    print("\nsafe speeds for radius (in m/s) =", radius[i], ":", safe_speeds)

    path = "data/crane_vmax.sqlite"
    plot_s_b_vs_vmax(path, i = 0)


