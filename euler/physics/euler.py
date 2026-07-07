# euler/physics/euler.py
import numpy as np
import time
from euler.physics import Interpolate
from euler.physics import (
    get_Mt, get_P, get_X, get_dV_dt, get_theta, dx_dt, dH_dt, dz_dt
)
from euler.config import INITIAL_MASS, FUEL_CONSUMPION, h as H, theta as THETA, N_max as N
from euler.data import convert_xlsx_to_dict


def _get_initial_state():
    """Выносит инициализацию начальных условий из run_euler/run_rk4."""
    data_dict = convert_xlsx_to_dict()
    v0 = data_dict['V'][1]          # как у тебя в коде
    h0 = H
    x0 = 0.0
    z0 = 0.0
    theta0 = THETA
    dt = H                         # у тебя тут странно: dt = H (высота), лучше вынести отдельно в config
    N_max = N
    mass0 = INITIAL_MASS
    return v0, h0, x0, z0, theta0, dt, N_max, mass0


def run_euler():
    v, h, x, z, theta, dt, N_max, mass = _get_initial_state()
    time_val = 0.0

    interp = Interpolate()
    cx_func = interp.get_cx

    data = np.empty((N_max, 14), dtype=np.float64)
    steps_done = 0

    for i in range(N_max):
        rho = get_P(h)
        cx = cx_func(v)
        drag = get_X(interp, v, h)

        dv_dt = get_dV_dt(interp, v, h, theta, time_val)
        dtheta_dt = get_theta(v, theta)
        dx_dt_val = dx_dt(v, theta)
        dh_dt_val = dH_dt(v, theta)
        dz_dt_val = dz_dt(v, theta)

        v_new = v + dv_dt * dt
        h_new = h + dh_dt_val * dt
        x_new = x + dx_dt_val * dt
        z_new = z + dz_dt_val * dt
        theta_new = theta + dtheta_dt * dt
        time_new = time_val + dt
        mass_new = get_Mt(time_new)

        if h_new <= 0:
            if dh_dt_val == 0:
                h_final, x_final, z_final = h, x, z
                v_final, theta_final, mass_final = v, theta, mass
            else:
                dt_touch = -h / dh_dt_val
                dt_touch = max(0.0, min(dt, dt_touch))

                h_final = h + dh_dt_val * dt_touch
                x_final = x + dx_dt_val * dt_touch
                z_final = z + dz_dt_val * dt_touch
                v_final = v + dv_dt * dt_touch
                theta_final = theta + dtheta_dt * dt_touch
                mass_final = mass - FUEL_CONSUMPION * dt_touch
                h_final = 0.0

            rho_final = get_P(h_final)
            cx_final = cx_func(v_final)
            drag_final = get_X(interp, v_final, h_final)

            data[i, :] = [
                v_final, h_final, x_final, z_final, theta_final, mass_final,
                cx_final, rho_final, drag_final,
                0.0, 0.0, dx_dt_val, dh_dt_val, dz_dt_val
            ]
            steps_done = i + 1
            break

        data[i, :] = [
            v_new, h_new, x_new, z_new, theta_new, mass_new,
            cx, rho, drag,
            dv_dt, dtheta_dt, dx_dt_val, dh_dt_val, dz_dt_val
        ]

        v, h, x, z, theta, mass, time_val = v_new, h_new, x_new, z_new, theta_new, mass_new, time_new
        steps_done = i + 1

    return data[:steps_done], steps_done