# ФАЙЛ: run.py
# КОМЕНТАРИЙ: Преднозначен для запуска проекта
# 
# ЗАПУСК --> python -m run

""" PYTHON МОДУЛИ """

""" ФАЙЛЫ ПРОЕКТА """
# run.py
# run.py
# run.py
# run.py
from task_1.euler.physics import solve_both_parallel
from task_1.euler.utils import plot_trajectory_combined

def main():
    res_e, steps_e, res_r, steps_r, t_e, t_r = solve_both_parallel()

    print(f"Эйлер: шагов={steps_e}, время={t_e:.4f} с")
    print(f"RK4:   шагов={steps_r}, время={t_r:.4f} с")

    plot_trajectory_combined(res_e, res_r, time_e=t_e, time_r=t_r)

if __name__ == "__main__":
    main()
