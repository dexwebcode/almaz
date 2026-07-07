# ФАЙЛ: equations.py 
# КОМЕНТАРИЙ: Преднозначен для хранения формул 
# СТРУКТУРА(кратко):
#     get_Mt() --------> Вычисление массы в текущий момент времени. 
#     get_P() ---------> Вычисление плотности воздуха.
#     get_X() ---------> Вычисление лобового сопротивления с учетом плотности воздуха.

# ================== ЗАПУСК в run.py ====================

# from euler.physics import get_X

# from euler.physics import Interpolate
# def main():
#     interpolator = Interpolate()
#     print("Запуск get_X.py:\n", get_X(interpolator, 150, 1))

# if __name__ == "__main__":
#     main()

# ========================================================
import numpy as np

""" ФАЙЛЫ ПРОЕКТА """
from task_1.euler.config import (
    INITIAL_MASS,
    FUEL_CONSUMPION,
    RHO_AT_SEA_LEVEL,
    K,S,THRUST,
    G, M, dPsi_dt
)

""" PYTHON МОДУЛИ """
import math

# =========== Вычисление массы в текущий момент времени. =========== #
def get_Mt(flow_time: float) -> float:
    # ВХОД:  Текущее время
    # ВЫХОД: Топливо кончилось --> False
    #        Топливо есть  --> float: 123.2

    m = INITIAL_MASS - FUEL_CONSUMPION * flow_time
    return max(0.0, m)

# ================== Вычисление плотности воздуха. ================== #
def get_P(flow_height: float) -> float:
    # ВХОД:  Текущая высота
    # ВЫХОД: Плотность --> float: 123.2

    if flow_height < 0:
        return 0.0
    return RHO_AT_SEA_LEVEL * math.exp(-flow_height / 10000.0)

# == Вычисление лобового сопротивления с учетом плотности воздуха. == #
def get_X(Interpolator, V: float, flow_height: float) -> float:

    rho_0 = get_P(flow_height)
    Cx = Interpolator.get_cx(V)
    return Cx * K * (rho_0 * V**2 / 2.0) * S

# ======= Вычисление остальных простых функций по dt. ============= #

def get_dV_dt(Interpolator, V: float, flow_height: float, \
              theta:float, time:float):
    mass = get_Mt(time)
    if mass < 1e-6:
        # Если массы почти нет, ускорение не считаем (или считаем только от сопротивления)
        return 0.0

    drag = get_X(Interpolator, V, flow_height)
    numerator = THRUST - drag - mass * G * math.sin(theta)
    return numerator / mass

def get_theta(V: float, theta:float):
    if abs(V) < 1e-6:
        return 0.0
    return -G * math.cos(theta) / V

def dx_dt(V: float, theta:float):
    return V * math.cos(theta) * math.cos(np.radians(dPsi_dt))

def dH_dt(V: float, theta:float):
    return V * math.sin(theta)

def dz_dt(V: float, theta:float):
    return -V * math.cos(theta) * math.sin(np.radians(dPsi_dt))

# ================================================================== #
