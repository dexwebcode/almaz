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


""" ФАЙЛЫ ПРОЕКТА """
from euler.config import (
    INITIAL_MASS,
    FUEL_CONSUMPION,
    RHO_AT_SEA_LEVEL,
    K,
    S
)

""" PYTHON МОДУЛИ """
import math

# =========== Вычисление массы в текущий момент времени. =========== #
def get_Mt(flow_time: float) -> float:
    # ВХОД:  Текущее время
    # ВЫХОД: Топливо кончилось --> False
    #        Топливо есть  --> float: 123.2

    M = INITIAL_MASS - FUEL_CONSUMPION * flow_time
    if M > 0:
        return INITIAL_MASS - FUEL_CONSUMPION * flow_time
    else:
        return False

# ================== Вычисление плотности воздуха. ================== #
def get_P(flow_height: float) -> float:
    # ВХОД:  Текущая высота
    # ВЫХОД: Плотность --> float: 123.2

    if flow_height >= 0:
        return RHO_AT_SEA_LEVEL * math.exp(- flow_height / 10000.0)
    else:
        return False

# == Вычисление лобового сопротивления с учетом плотности воздуха. == #
def get_X(Interpolator, V: float, flow_height: float) -> float:

    rho_0 = get_P(flow_height)

    Cx = Interpolator.get_cx(V)

    result = Cx * K * (rho_0 * V**2 / 2.0) * S
    return result




