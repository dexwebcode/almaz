# ФАЙЛ: interpolation.py
# КОМЕНТАРИЙ: Преднозначен для того, чтобы использовать интерполяцию через класс

# СТРУКТУРА(кратко):
#   Interpolate() -----> Класс для хранения интерполяции
#      get_cx() --------> Получение интерполяции Cx по значению V. 

# ================== ЗАПУСК в run.py ====================

# from euler.physics import Interpolate
# def main():
#     interp = Interpolate()
#     if interp.is_ready:
#         print("Запуск interpolation.py:\n"
#         print(interp.get_cx(180))
#     else:
#         print("Интерполятор не готов:", interp.error_message)
# 
# if __name__ == "__main__":
#     main()

# ========================================================

""" PYTHON МОДУЛИ """
from dataclasses import dataclass, field
from typing import Callable, Optional
import numpy as np
from scipy.interpolate import interp1d
from euler.data.loader import convert_xlsx_to_dict

""" ФАЙЛЫ ПРОЕКТА """
# ..


@dataclass
class Interpolate:
    cx_of_v: Optional[Callable[[np.ndarray], np.ndarray]] = field(default=None, init=False)
    is_ready: bool = field(default=False, init=False)
    error_message: str = field(default="", init=False)

    def __post_init__(self):
        try:
            data = convert_xlsx_to_dict()

            if data is False:
                raise RuntimeError("Не удалось загрузить файл с данными.")

            if data.empty:
                raise ValueError("Файл загружен, но он пустой.")

            required_cols = ["V", "Cx"]
            missing_cols = [col for col in required_cols if col not in data.columns]
            if missing_cols:
                raise ValueError(f"В файле отсутствуют колонки: {missing_cols}")

            v_vals = data["V"].to_numpy(dtype=float)
            cx_vals = data["Cx"].to_numpy(dtype=float)

            sort_idx = np.argsort(v_vals)
            v_sorted = v_vals[sort_idx]
            cx_sorted = cx_vals[sort_idx]

            # Защита от дубликатов скоростей
            if len(np.unique(v_sorted)) != len(v_sorted):
                _, unique_indices = np.unique(v_sorted, return_index=True)
                v_sorted = v_sorted[unique_indices]
                cx_sorted = cx_sorted[unique_indices]

            self.cx_of_v = interp1d(
                v_sorted,
                cx_sorted,
                kind="linear",
                bounds_error=False,
                fill_value=(cx_sorted[0], cx_sorted[-1]),
            )

            self.is_ready = True

        except Exception as e:
            self.error_message = str(e)
            self.is_ready = False
            print(f"Ошибка инициализации интерполяции: {e}")

    def get_cx(self, velocity: float) -> float:
        if not self.is_ready:
            raise RuntimeError(f"Интерполятор не готов. Причина: {self.error_message}")

        result = self.cx_of_v(velocity)
        return float(result) if isinstance(result, np.ndarray) else float(result)