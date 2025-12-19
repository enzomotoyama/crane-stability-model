import numpy as np
import pandas as pd
from create_database import fetch_data
from forces import make_F, rk4

SEED = 12345
RNG  = np.random.default_rng(SEED)

T_MIN = 0.5
T_MAX = 10.0

def sample_t_brake(mean, std, n, rng=RNG, tmin = T_MIN, tmax = T_MAX):
    if std <= 0:
        return np.full(n, float(np.clip(mean, tmin, tmax)))
    t = rng.normal(mean, std, size=n)
    return np.clip(t, tmin, tmax)


def find_vmax(i, t_brake, vals, v_test, Tsim= 15.0, dt = 1e-3):
    for v0 in reversed(v_test):
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

        if t_tip is None:
            return v0

    return v_test[0]


def vmax_for_i_tbrake(i, t_mean, t_std, N, Tsim = 15.0, dt= 0.004):
    vals = fetch_data()

    t_draws = sample_t_brake(t_mean, t_std, N)

    v_test = np.arange(0.5, 5.0, 0.5)

    v_max_ms = np.empty(N, dtype=float)

    for k, t_b in enumerate(t_draws):
        v_max_ms[k] = find_vmax(i, float(t_b), vals, v_test, Tsim, dt)

    return pd.DataFrame({
        "i": i,
        "radius": float(vals["radius"][i]),
        "t_brake": t_draws,
        "vmax_ms": v_max_ms,
        "vmax_kmh": 3.6 * v_max_ms
    })


def quantiles_by_radius(df: pd.DataFrame):
    g = df.groupby(["i", "radius"])["vmax_kmh"]
    columns = g.agg(N="size", mean="mean", std="std")
    quantiles = g.quantile([0.05, 0.50, 0.95]).unstack(level=-1).rename(columns={0.05: "q05", 0.50: "q50", 0.95: "q95"})
    return columns.join(quantiles).reset_index()


