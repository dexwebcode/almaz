# euler.py
import numpy as np
from euler.physics import Interpolate
from euler.physics import (
    get_Mt, get_P, get_X, get_dV_dt, get_theta, dx_dt, dH_dt, dz_dt
)
from euler.config import INITIAL_MASS, FUEL_CONSUMPION, h as H, theta as THETA, N_max as N
from euler.data import convert_xlsx_to_dict

def run_euler():
    data = convert_xlsx_to_dict()
    # Инициализация интерполятора (один раз!)
    interp = Interpolate()
    cx_func = interp.get_cx

    # Начальное состояние
    v, h, x, z, theta, dt, N_max = (convert_xlsx_to_dict())['V'][1], H, 0, 0, THETA, H,  N
    mass = INITIAL_MASS
    time = 0.0

    # Предварительно выделяем память: 14 колонок
    data = np.empty((N_max, 14), dtype=np.float64)

    for i in range(N_max):
        # --- ОДИН РАЗ считаем промежуточные величины ---
        rho = get_P(h)
        cx = cx_func(v)
        drag = get_X(interp, v, h)

        # Производные
        dv_dt = get_dV_dt(interp, v, h, theta, time)
        dtheta_dt = get_theta(v, theta)
        dx_dt_val = dx_dt(v, theta)
        dh_dt_val = dH_dt(v, theta)
        dz_dt_val = dz_dt(v, theta)

        # Пробный шаг Эйлера
        v_new = v + dv_dt * dt
        h_new = h + dh_dt_val * dt
        x_new = x + dx_dt_val * dt
        z_new = z + dz_dt_val * dt
        theta_new = theta + dtheta_dt * dt
        time_new = time + dt
        mass_new = get_Mt(time_new)
        # === ПРОВЕРКА НА КАСАНИЕ ЗЕМЛИ ===
        if h_new <= 0:
            # Если следующий шаг уходит под землю, делаем линейную интерполяцию,
            # чтобы найти момент, когда высота ровно 0.
            if dh_dt_val == 0:
                # Если вертикальная скорость нулевая, просто берём текущий шаг
                h_final = h
                x_final = x
                z_final = z
                v_final = v
                theta_final = theta
                mass_final = mass
            else:
                # dt_touch: сколько времени нужно, чтобы высота стала 0
                dt_touch = -h / dh_dt_val
                if dt_touch < 0 or dt_touch > dt:
                    # На всякий случай ограничиваем диапазоном [0, dt]
                    dt_touch = max(0.0, min(dt, dt_touch))

                h_final = h + dh_dt_val * dt_touch
                x_final = x + dx_dt_val * dt_touch
                z_final = z + dz_dt_val * dt_touch
                v_final = v + dv_dt * dt_touch
                theta_final = theta + dtheta_dt * dt_touch
                mass_final = mass - FUEL_CONSUMPION * dt_touch

                # Принудительно ставим высоту ровно 0 (защита от ошибок округления)
                h_final = 0.0

            # Записываем финальную точку касания
            # Пересчитаем cx/rho/drag для финального состояния (опционально)
            rho_final = get_P(h_final)
            cx_final = cx_func(v_final)
            drag_final = get_X(interp, v_final, h_final)

            data[i, :] = [
                v_final, h_final, x_final, z_final, theta_final, mass_final,
                cx_final, rho_final, drag_final,
                0.0, 0.0, dx_dt_val, dh_dt_val, dz_dt_val  # производные тут условные
            ]
            steps_done = i + 1
            break

        # Если всё нормально (не коснулись земли) — записываем обычный шаг
        data[i, :] = [
            v_new, h_new, x_new, z_new, theta_new, mass_new,
            cx, rho, drag,
            dv_dt, dtheta_dt, dx_dt_val, dh_dt_val, dz_dt_val
        ]

        # Обновляем состояние
        v, h, x, z, theta, mass, time = v_new, h_new, x_new, z_new, theta_new, mass_new, time_new

    final_data = data[:steps_done]
    return final_data
