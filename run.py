# ФАЙЛ: run.py
# КОМЕНТАРИЙ: Преднозначен для запуска проекта
# 
# ЗАПУСК --> python -m run

""" PYTHON МОДУЛИ """

""" ФАЙЛЫ ПРОЕКТА """
from euler.physics.euler import run_euler
from euler.utils import plot_flight

def main():
    # Начальные условия
    results = run_euler()

    # Отрисовка
    plot_flight(results)

if __name__ == "__main__":
    main()