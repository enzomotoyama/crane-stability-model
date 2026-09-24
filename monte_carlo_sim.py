import numpy as np
import pandas as pd
from parameters import get_values
from create_database import compute_vmax_tbrake

SEED = 12345
RNG  = np.random.default_rng(SEED)

T_MIN = 0.5
T_MAX = 10.0

def sample_t_brake(mean, std, n, rng=RNG, tmin = T_MIN, tmax = T_MAX):
    if std <= 0:
        return np.full(n, float(np.clip(mean, tmin, tmax)))
    t = rng.normal(mean, std, size=n)
    return np.clip(t, tmin, tmax)


def vmax_for_i_tbrake(i, t_mean, t_std, N, Tsim = 15.0, dt= 0.004, eps = 1e-2):
    vals = get_values()

    t_draws = sample_t_brake(t_mean, t_std, N)

    v_max_ms = np.empty(N, dtype=float)

    for k, t_b in enumerate(t_draws):
        v_max_ms[k] = compute_vmax_tbrake(i, float(t_b), Tsim, dt, vals, eps=eps)

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


