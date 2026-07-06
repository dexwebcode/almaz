# ФАЙЛ: covert_files
# СТРУКТУРА(кратко):
#     deg_to_rad() -----> Получение таблицы данных из exel.

""" ИМПОРТЫ """
import pandas as pd

# ================== Получение таблицы данных из exel. =================== #
def convert(INIT_EXEL_FILE: str):
    return pd.read_excel(INIT_EXEL_FILE)