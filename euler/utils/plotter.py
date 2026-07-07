# euler/utils/plotter.py
import plotly.graph_objects as go
import numpy as np

def plot_trajectory_combined(res_e: np.ndarray, res_r: np.ndarray,
                             time_e: float = 0.0,
                             time_r: float = 0.0) -> None:
    """
    Рисует обе траектории на одних осях (один график) для прямого сравнения.
    res_e — данные Эйлера, res_r — данные RK4.
    Колонки: [..., X=2, H=1, ...]
    """
    X_e = res_e[:, 2]
    H_e = res_e[:, 1]

    X_r = res_r[:, 2]
    H_r = res_r[:, 1]

    fig = go.Figure()

    # Линия Эйлера
    fig.add_trace(go.Scatter(
        x=X_e, y=H_e,
        mode='lines',
        name=f'Эйлер (t={time_e:.4f} с)',
        line=dict(color='#2E86AB', width=3, dash='solid')
    ))

    # Линия RK4
    fig.add_trace(go.Scatter(
        x=X_r, y=H_r,
        mode='lines',
        name=f'Рунге-Кутта 4 (t={time_r:.4f} с)',
        line=dict(color='#A23B72', width=3, dash='dot')
    ))

    # Точка старта (общая для наглядности)
    fig.add_trace(go.Scatter(
        x=[X_e[0]], y=[H_e[0]],
        mode='markers',
        marker=dict(size=10, color='green', symbol='circle'),
        name='Старт',
        showlegend=True
    ))

    # Точки падения (отдельно для каждого метода)
    fig.add_trace(go.Scatter(
        x=[X_e[-1]], y=[H_e[-1]],
        mode='markers',
        marker=dict(size=10, color='#2E86AB', symbol='x'),
        name='Падение (Эйлер)',
        showlegend=True
    ))
    fig.add_trace(go.Scatter(
        x=[X_r[-1]], y=[H_r[-1]],
        mode='markers',
        marker=dict(size=10, color='#A23B72', symbol='x'),
        name='Падение (RK4)',
        showlegend=True
    ))

    max_x = max(X_e.max(), X_r.max())
    max_h = max(H_e.max(), H_r.max())

    fig.update_layout(
        title='Сравнение траекторий: Эйлер vs Рунге-Кутта 4',
        xaxis_title='Дальность X, м',
        yaxis_title='Высота H, м',
        height=600,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white',
        legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.8)')
    )

    fig.update_xaxes(range=[0, max_x * 1.05])
    fig.update_yaxes(range=[0, max_h * 1.1])

    fig.show()
