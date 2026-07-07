# ФАЙЛ: run.py
# КОМЕНТАРИЙ: Преднозначен для запуска проекта
# 
# ЗАПУСК --> python -m run

""" PYTHON МОДУЛИ """
# ..

""" ФАЙЛЫ ПРОЕКТА """
from euler.physics import get_X

from euler.physics import Interpolate
def main():
    interpolator = Interpolate()
    print("Запуск get_X.py:\n", get_X(interpolator, 150, 1))

if __name__ == "__main__":
    main()