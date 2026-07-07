# euler/solver.py
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from euler.physics import Interpolate
from euler.physics import (
    get_Mt, get_P, get_X, get_dV_dt, get_theta, dx_dt, dH_dt, dz_dt
)
from euler.config import INITIAL_MASS, FUEL_CONSUMPION, h as H, theta as THETA, N_max as N
from euler.data import convert_xlsx_to_dict


def _get_initial_state():
    data_dict = convert_xlsx_to_dict()
    v0 = data_dict['V'][1]
    h0 = H
    x0 = 0.0
    z0 = 0.0
    theta0 = THETA
    # ВАЖНО: dt лучше вынести в config как отдельную константу, а не брать H
    dt = H  # <-- поменяй в config.py на DT = 0.1 и используй DT здесь
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


def run_rk4():
    v, h, x, z, theta, dt, N_max, mass = _get_initial_state()
    time_val = 0.0
    dt = dt
    interp = Interpolate()
    cx_func = interp.get_cx

    data = np.empty((N_max, 14), dtype=np.float64)
    steps_done = 0

    for i in range(N_max):
        # --- k1 ---
        rho_1 = get_P(h)
        cx_1 = cx_func(v)
        # drag_1 не нужен отдельно, если get_dV_dt сам его считает

        dv_dt_1 = get_dV_dt(interp, v, h, theta, time_val)
        dtheta_dt_1 = get_theta(v, theta)
        dx_dt_1 = dx_dt(v, theta)
        dh_dt_1 = dH_dt(v, theta)
        dz_dt_1 = dz_dt(v, theta)

        # --- k2 ---
        v_2 = v + dv_dt_1 * dt / 2.0
        h_2 = h + dh_dt_1 * dt / 2.0
        x_2 = x + dx_dt_1 * dt / 2.0
        z_2 = z + dz_dt_1 * dt / 2.0
        theta_2 = theta + dtheta_dt_1 * dt / 2.0
        time_2 = time_val + dt / 2.0

        dv_dt_2 = get_dV_dt(interp, v_2, h_2, theta_2, time_2)
        dtheta_dt_2 = get_theta(v_2, theta_2)
        dx_dt_2 = dx_dt(v_2, theta_2)
        dh_dt_2 = dH_dt(v_2, theta_2)
        dz_dt_2 = dz_dt(v_2, theta_2)

        # --- k3 ---
        v_3 = v + dv_dt_2 * dt / 2.0
        h_3 = h + dh_dt_2 * dt / 2.0
        x_3 = x + dx_dt_2 * dt / 2.0
        z_3 = z + dz_dt_2 * dt / 2.0
        theta_3 = theta + dtheta_dt_2 * dt / 2.0
        time_3 = time_val + dt / 2.0

        dv_dt_3 = get_dV_dt(interp, v_3, h_3, theta_3, time_3)
        dtheta_dt_3 = get_theta(v_3, theta_3)
        dx_dt_3 = dx_dt(v_3, theta_3)
        dh_dt_3 = dH_dt(v_3, theta_3)
        dz_dt_3 = dz_dt(v_3, theta_3)

        # --- k4 ---
        v_4 = v + dv_dt_3 * dt
        h_4 = h + dh_dt_3 * dt
        x_4 = x + dx_dt_3 * dt
        z_4 = z + dz_dt_3 * dt
        theta_4 = theta + dtheta_dt_3 * dt
        time_4 = time_val + dt

        dv_dt_4 = get_dV_dt(interp, v_4, h_4, theta_4, time_4)
        dtheta_dt_4 = get_theta(v_4, theta_4)
        dx_dt_4 = dx_dt(v_4, theta_4)
        dh_dt_4 = dH_dt(v_4, theta_4)
        dz_dt_4 = dz_dt(v_4, theta_4)

        # Средние по RK4
        dv_dt = (dv_dt_1 + 2*dv_dt_2 + 2*dv_dt_3 + dv_dt_4) / 6.0
        dtheta_dt = (dtheta_dt_1 + 2*dtheta_dt_2 + 2*dtheta_dt_3 + dtheta_dt_4) / 6.0
        dx_dt_val = (dx_dt_1 + 2*dx_dt_2 + 2*dx_dt_3 + dx_dt_4) / 6.0
        dh_dt_val = (dh_dt_1 + 2*dh_dt_2 + 2*dh_dt_3 + dh_dt_4) / 6.0
        dz_dt_val = (dz_dt_1 + 2*dz_dt_2 + 2*dz_dt_3 + dz_dt_4) / 6.0

        v_new = v + dv_dt * dt
        h_new = h + dh_dt_val * dt
        x_new = x + dx_dt_val * dt
        z_new = z + dz_dt_val * dt
        theta_new = theta + dtheta_dt * dt
        time_new = time_val + dt
        mass_new = get_Mt(time_new)

        # Остановка при касании земли
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

        rho_1 = get_P(h)
        cx_1 = cx_func(v)
        drag_1 = get_X(interp, v, h)

        data[i, :] = [
            v_new, h_new, x_new, z_new, theta_new, mass_new,
            cx_1, rho_1, drag_1,
            dv_dt, dtheta_dt, dx_dt_val, dh_dt_val, dz_dt_val
        ]

        v, h, x, z, theta, mass, time_val = v_new, h_new, x_new, z_new, theta_new, mass_new, time_new
        steps_done = i + 1

    return data[:steps_done], steps_done


def solve_both_parallel():
    """Запускает оба метода параллельно и возвращает (res_e, steps_e, res_r, steps_r, t_e, t_r)."""
    import time
    with ThreadPoolExecutor(max_workers=2) as executor:
        f_e = executor.submit(run_euler)
        f_r = executor.submit(run_rk4)

        t0_e = time.perf_counter()
        res_e, steps_e = f_e.result()
        t1_e = time.perf_counter()

        t0_r = time.perf_counter()
        res_r, steps_r = f_r.result()
        t1_r = time.perf_counter()

    t_e = t1_e - t0_e
    t_r = t1_r - t0_r
    return res_e, steps_e, res_r, steps_r, t_e, t_r
