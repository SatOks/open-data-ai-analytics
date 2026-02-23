# Figures

Ця папка містить збережені візуалізації результатів аналізу.

## Типи графіків

- `missing_values.png` - Візуалізація пропущених значень
- `distribution_*.png` - Розподіли змінних
- `correlation_matrix.png` - Матриця кореляції
- `scatter_*.png` - Scatter plots з регресійними лініями
- `feature_importance.png` - Важливість ознак моделі
- `model_predictions.png` - Прогнози моделі vs фактичні значення
- `grouped_*.png` - Порівняння по групах

## Генерація графіків

Графіки генеруються автоматично при запуску модуля `visualization.py` або відповідних ноутбуків.

```python
from src.visualization import plot_distribution

# Приклад
plot_distribution(df, 'Life expectancy ', save=True)
```

Всі графіки зберігаються в роздільній здатності 300 DPI для високої якості друку.
