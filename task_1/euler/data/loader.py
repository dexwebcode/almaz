
# ФАЙЛ: loader.py
# КОМЕНТАРИЙ: Преднозначен для того, чтобы объявлять функции для работы с файлами

# СТРУКТУРА(кратко):
#     convert_xlsx_to_dict() --------> Конвертация xlsx в список {}. 
# 
# ================== ЗАПУСК в run.py ====================

# from euler.data import convert_xlsx_to_dict
# def main():
#     print("Запуск loader.py:\n", convert_xlsx_to_dict())
# 
# if __name__ == "__main__":
#     main()

# ========================================================


import pandas as pd
from pathlib import Path

# Вычисляем путь к data.xlsx относительно текущего файла (loader.py)
BASE_DIR = Path(__file__).resolve().parent
XLSX_PATH = BASE_DIR / "data.xlsx"


# ================= Конвертация из xlsx в словрь. ================= #
def convert_xlsx_to_dict(file_path: Path | str | None = None) -> pd.DataFrame | bool:   
    # ВХОД:  XLSX_PATH
    # ВЫХОД: Массив  --> {}
    #        При ошибке --> False
    if file_path is None:
        file_path = XLSX_PATH
    
    try:
        data = pd.read_excel(file_path)
        return data
    except FileNotFoundError:
        print(f"Ошибка: файл не найден по пути: {file_path}")
        return False
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return False

