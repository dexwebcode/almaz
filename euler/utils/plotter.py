# euler/utils/plotter.py
import plotly.graph_objects as go
import numpy as np

def plot_flight(results: np.ndarray) -> None:
    """
    Рисует траекторию: высота H от дальности X.
    
    Ожидаемый формат results: массив (N_steps, 14)
    Колонка 1 -> H (высота)
    Колонка 2 -> X (дальность)
    """
    if results.ndim != 2 or results.shape[1] < 3:
        raise ValueError("results должен быть 2D-массивом с минимум 3 колонками")

    H = results[:, 1]  # высота
    X = results[:, 2]  # дальность

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=X,
        y=H,
        mode='lines',          # линия
        name='Траектория',
        line=dict(color='#2E86AB', width=3)
    ))

    # Добавим стартовую и конечную точку для наглядности
    fig.add_trace(go.Scatter(
        x=[X[0]],
        y=[H[0]],
        mode='markers',
        marker=dict(size=10, color='green'),
        name='Старт'
    ))
    fig.add_trace(go.Scatter(
        x=[X[-1]],
        y=[H[-1]],
        mode='markers',
        marker=dict(size=10, color='red'),
        name='Падение'
    ))

    fig.update_layout(
        title='Траектория полёта: высота от дальности',
        xaxis_title='Дальность X, м',
        yaxis_title='Высота H, м',
        height=600,
        showlegend=True,
        hovermode='x unified'
    )

    fig.show()
