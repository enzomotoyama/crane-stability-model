import numpy as np

def a_phi(phi, x_cog, z_cog, width):
    a0 = width / 2.0 - x_cog
    h0 = z_cog
    r = np.hypot(a0, h0)
    return r * np.cos(phi)

def h_phi(phi, x_cog, z_cog, width):
    a0 = width / 2.0 - x_cog
    h0 = z_cog
    r = np.hypot(a0, h0)
    return r * np.sin(phi)

def brake_force(t, m, v0, s_brake):
    F0 = 0.5 * m * v0**2 / s_brake
    a = F0 / m
    t_brake = v0 / a
    if t < t_brake:
        return F0
    return 0.0

def make_F(s_brake, IT, m, v0, x_cog, z_cog, width, g):
    a0 = width / 2.0 - x_cog
    h0 = z_cog
    r = np.hypot(a0, h0)

    def F(t, y):
        phi, dphi = y
        Fb_t = brake_force(t, m, v0, s_brake)
        ddphi = np.cos(phi) * r * (Fb_t * np.tan(phi) - m * g) / IT
        return np.array([dphi, ddphi], dtype=float)

    return F

def itRK4(F, dt, t, y):
    k1 = dt * F(t, y)
    k2 = dt * F(t + dt / 2.0, y + k1 / 2.0)
    k3 = dt * F(t + dt / 2.0, y + k2 / 2.0)
    k4 = dt * F(t + dt, y + k3)
    return y + (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0

def rk4(F, dt, Tsim, x_cog, z_cog, width):
    a0 = width / 2.0 - x_cog
    h0 = z_cog
    phi0 = np.arctan2(h0, a0)

    times = []
    phi_deg = []
    phi_list = []
    dphi_list = []

    t = 0.0
    y = np.array([phi0, 0.0], dtype=float)
    t_tip = None

    while t <= Tsim:
        phi, dphi = y
        a_cur = a_phi(phi, x_cog, z_cog, width)
        h_cur = h_phi(phi, x_cog, z_cog, width)

        times.append(t)
        phi_deg.append(np.degrees(np.arctan2(h_cur, a_cur)))
        phi_list.append(phi)
        dphi_list.append(dphi)

   
        if a_cur <= 0.0:
            t_tip = t
            break

        y_next = itRK4(F, dt, t, y)
        a_next = a_phi(y_next[0], x_cog, z_cog, width)

        if (a_cur > 0.0) and (a_next <= 0.0):
            alpha = a_cur / (a_cur - a_next + 1e-15)
            t_tip = t + alpha * dt
            phi_tip = y[0] + alpha * (y_next[0] - y[0])

            times.append(t_tip)
            phi_deg.append(90.0)
            phi_list.append(phi_tip)
            dphi_list.append(y[1] + alpha * (y_next[1] - y[1]))

            break

        if phi_deg[-1] < 80 :
            break

        y = y_next
        t += dt

    return (
        np.array(times),
        np.array(phi_deg),
        np.array(phi_list),
        np.array(dphi_list),
        t_tip
    )

