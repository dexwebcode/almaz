# ФАЙЛ: EQUATIONS 
# СТРУКТУРА(кратко):
#   EQUATIONS():
#     deg_to_rad() ------------> Перевод в радианы.
#     derivative_mass_to_time() ------------> Вычисление зависимости массы от времени. 
#     derivative_fuel_to_time() ------------> Вычисление зависимости топлива от времени. 
#     derivative_velocity_to_density() -----> Вычисление зависимости скорости от плотности воздуха
#     derivative_velocity_to_time() --------> Вычисление зависимости скорости от времени.  
#     derivative_angle_tett_to_time() ------> Вычисление зависимости угла θ от времени
#     derivative_X_to_time() ---------------> Вычисление зависимости угла X от времени
#     derivative_Z_to_time() ---------------> Вычисление зависимости угла 𝑍 от времени
#     is_straight_flight() -----------------> Вычисление условия движения без рыскания
#     air_density_at_height() --------------> Вычисление плотности воздуха на высоте
 
""" ИМПОРТЫ """
from eiler.config.constants import (
    FUEL_CONSUMPION, INITIAL_MASS, END_TIME, G,
    COEF_K as K,  SQUARE as S, RHO_AT_SEA_LEVEL
)

from typing import Callable
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import pandas as pd


def convert(file_path: str) -> pd.DataFrame:
    return pd.read_excel(file_path)

class EQUATIONS():
    def __init__(self, data: pd.DataFrame):
        # Сохраняем исходные данные
        self.data = data.copy()

        # Подготовка и сортировка для интерполяции
        v_vals = self.data["V"].to_numpy(dtype=float)
        cx_vals = self.data["Cx"].to_numpy(dtype=float)

        sort_idx = np.argsort(v_vals)
        self.v_sorted = v_vals[sort_idx]
        self.cx_sorted = cx_vals[sort_idx]

        # Создаём интерполятор один раз
        self.cx_of_v: Callable[[np.ndarray], np.ndarray] = interp1d(
            self.v_sorted,
            self.cx_sorted,
            bounds_error=False,
            fill_value=(self.cx_sorted[0], self.cx_sorted[-1]),
        )

        self.S = S
        self.K = K

    # ======================= Перевод в радианы. ====================== #
    @staticmethod
    def deg_to_rad(degrees) -> float:
        return degrees * math.pi / 180.0

    # =========== Вычисление зависимости массы от времени. ============ #
    @staticmethod
    def derivative_mass_to_time(FLOW_TIME: float) -> float:
        if FLOW_TIME > END_TIME:
            return INITIAL_MASS - FUEL_CONSUMPION * END_TIME
        else:
            return INITIAL_MASS - FUEL_CONSUMPION * FLOW_TIME

    # ========== Вычисление зависимости топлива от времени. =========== #
    @staticmethod
    def derivative_fuel_to_time(FLOW_TIME: float) -> float:
        if FLOW_TIME > END_TIME:
            return 0.0
        else:
            return FUEL_CONSUMPION * FLOW_TIME

    # ================= Вычисление плотности воздуха. ================= #
    def air_density_at_height(self, FLOW_HEIGH: float) -> float:
        return RHO_AT_SEA_LEVEL * math.exp(-FLOW_HEIGH / 10000.0)

    # ==== Вычисление лобового сопротивления от скорости воздуха и плотности атмосферы. ====== #
    def X(self, V: float, HEIGHT: float) -> float:
        rho_0 = self.air_density_at_height(HEIGHT)
        Cx = self.get_Cx_for_V(np.array([V]))[0]
        result = Cx * self.K * (rho_0 * V**2 / 2.0) * self.S
        return result

    def get_Cx_for_V(self, V_query: np.ndarray) -> np.ndarray:
        """Получить Cx через интерполяцию для заданных скоростей (массив или число)."""
        return self.cx_of_v(V_query)

    def simulate_euler(self, t_end, dt, V0, theta0_deg, psi0_deg, x0, H0, z0):
        n_steps = int(t_end / dt) + 1
        d = [0]*1000
        # Выделяем массивы под результаты
        t_arr = np.zeros(n_steps)
        V_arr = np.zeros(n_steps)
        theta_arr = np.zeros(n_steps)
        psi_arr = np.zeros(n_steps)
        x_arr = np.zeros(n_steps)
        H_arr = np.zeros(n_steps)
        z_arr = np.zeros(n_steps)

        # Конвертируем углы из градусов в радианы сразу при инициализации
        theta0 = self.deg_to_rad(theta0_deg)
        psi0 = self.deg_to_rad(psi0_deg)

        # Устанавливаем начальные условия в первые элементы массивов
        t_arr[0] = 0.0
        V_arr[0] = V0
        theta_arr[0] = theta0
        psi_arr[0] = psi0
        x_arr[0] = x0
        H_arr[0] = H0
        z_arr[0] = z0

        g = G

        for i in range(n_steps - 1):
            t = t_arr[i]

            # Текущие значения переменных (по одному числу на шаге)
            V = V_arr[i]
            theta = theta_arr[i]  # уже в радианах
            psi = psi_arr[i]     # уже в радианах
            x = x_arr[i]
            H = H_arr[i]
            z = z_arr[i]

            # --- РАСЧЕТ ПРОИЗВОДНЫХ (Правые части уравнений) ---

            rho = self.air_density_at_height(H)
            Cx = self.get_Cx_for_V(np.array([V]))[0]
            X_force = Cx * self.K * (rho * V**2 / 2.0) * self.S

            R_thrust = 4000.0  # замени на свою логику расчета тяги
            m = self.derivative_mass_to_time(t)

            dV_dt = (R_thrust - X_force - m * g * math.sin(theta)) / m

            if abs(V) < 1e-6:
                dTheta_dt = 0.0
            else:
                dTheta_dt = -g * math.cos(theta) / V

            dPsi_dt = 0.0

            dx_dt = V * math.cos(theta) * math.cos(psi)
            dH_dt = V * math.sin(theta)
            dz_dt = -V * math.cos(theta) * math.sin(psi)

            # Шаг Эйлера
            V_arr[i+1] = V + dV_dt * dt
            theta_arr[i+1] = theta + dTheta_dt * dt
            psi_arr[i+1] = psi + dPsi_dt * dt
            x_arr[i+1] = x + dx_dt * dt
            H_arr[i+1] = H + dH_dt * dt
            z_arr[i+1] = z + dz_dt * dt

            if H_arr[i] < 0:
                # Обрезаем массивы до текущего шага, чтобы не рисовать «под землёй»
                return {
                    'time': t_arr[:i+1],
                    'V': V_arr[:i+1],
                    'theta': theta_arr[:i+1],
                    'psi': psi_arr[:i+1],
                    'x': x_arr[:i+1],
                    'H': H_arr[:i+1],
                    'z': z_arr[:i+1]
                }

            t_arr[i+1] = t + dt

        return {
            'time': t_arr,
            'V': V_arr,
            'theta': theta_arr,
            'psi': psi_arr,
            'x': x_arr,
            'H': H_arr,
            'z': z_arr
        }


if __name__ == "__main__":
    data = convert("data.xlsx")
    print(data)
    sim = EQUATIONS(data)

    V0 = data['V'][1]
    theta0_deg = 30.0
    psi0_deg = 0.0 
    x0, H0, z0 = 0.0, 0.0, 0.0

    results = sim.simulate_euler(
        t_end=60.0, dt=0.01,
        V0=V0,
        theta0_deg=theta0_deg,
        psi0_deg=psi0_deg,
        x0=x0, H0=H0, z0=z0
    )

    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=results['time'], y=results['H'], mode='lines', name='Высота H(t)'))
    fig.update_layout(title='Траектория полета (Метод Эйлера)', xaxis_title='Время (с)', yaxis_title='Высота (м)')
    fig.show()
