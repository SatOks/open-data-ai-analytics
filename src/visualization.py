"""
Модуль для візуалізації результатів аналізу даних
Створює графіки, діаграми та інтерактивні візуалізації
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Optional, Tuple, Dict
import warnings
warnings.filterwarnings('ignore')


def setup_plot_style(style: str = 'seaborn-v0_8'):
    """
    Налаштування стилю графіків
    
    Args:
        style: стиль matplotlib
    """
    try:
        plt.style.use(style)
    except:
        plt.style.use('default')
    
    sns.set_palette("husl")


def get_figures_path() -> Path:
    """
    Повертає шлях до папки для збереження графіків
    """
    root = Path(__file__).parent.parent
    figures_dir = root / "reports" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    return figures_dir


def plot_missing_values(df: pd.DataFrame, 
                       save: bool = False,
                       filename: str = 'missing_values.png') -> None:
    """
    Візуалізація пропущених значень
    
    Args:
        df: DataFrame для аналізу
        save: чи зберігати графік
        filename: назва файлу для збереження
    """
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=True)
    
    if len(missing) == 0:
        print("✓ Пропущених значень не знайдено")
        return
    
    missing_pct = (missing / len(df) * 100).round(2)
    
    fig, ax = plt.subplots(figsize=(10, max(6, len(missing) * 0.3)))
    bars = ax.barh(range(len(missing)), missing_pct.values)
    
    # Кольорове кодування
    colors = ['green' if x < 5 else 'orange' if x < 20 else 'red' 
              for x in missing_pct.values]
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    ax.set_yticks(range(len(missing)))
    ax.set_yticklabels(missing.index)
    ax.set_xlabel('Відсоток пропущених значень (%)')
    ax.set_title('Пропущені значення по стовпцях')
    ax.grid(axis='x', alpha=0.3)
    
    # Додаємо значення на графіку
    for i, v in enumerate(missing_pct.values):
        ax.text(v + 0.5, i, f'{v:.1f}%', va='center')
    
    plt.tight_layout()
    
    if save:
        filepath = get_figures_path() / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Збережено: {filepath}")
    
    plt.show()


def plot_distribution(df: pd.DataFrame, 
                     column: str,
                     bins: int = 30,
                     save: bool = False,
                     filename: str = None) -> None:
    """
    Візуалізація розподілу змінної
    
    Args:
        df: DataFrame
        column: назва стовпця
        bins: кількість bins для гістограми
        save: чи зберігати графік
        filename: назва файлу
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found")
    
    data = df[column].dropna()
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Гістограма
    axes[0].hist(data, bins=bins, edgecolor='black', alpha=0.7)
    axes[0].axvline(data.mean(), color='red', linestyle='--', 
                    linewidth=2, label=f'Mean: {data.mean():.2f}')
    axes[0].axvline(data.median(), color='green', linestyle='--', 
                    linewidth=2, label=f'Median: {data.median():.2f}')
    axes[0].set_xlabel(column)
    axes[0].set_ylabel('Frequency')
    axes[0].set_title('Histogram')
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    
    # Box plot
    axes[1].boxplot(data, vert=True)
    axes[1].set_ylabel(column)
    axes[1].set_title('Box Plot')
    axes[1].grid(alpha=0.3)
    
    # KDE plot
    data.plot(kind='kde', ax=axes[2], linewidth=2)
    axes[2].set_xlabel(column)
    axes[2].set_ylabel('Density')
    axes[2].set_title('Kernel Density Estimate')
    axes[2].grid(alpha=0.3)
    
    plt.suptitle(f'Distribution of {column}', fontsize=14, y=1.02)
    plt.tight_layout()
    
    if save:
        fname = filename or f'distribution_{column.replace(" ", "_")}.png'
        filepath = get_figures_path() / fname
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Збережено: {filepath}")
    
    plt.show()


def plot_correlation_matrix(df: pd.DataFrame,
                           figsize: Tuple[int, int] = (14, 12),
                           save: bool = False,
                           filename: str = 'correlation_matrix.png') -> None:
    """
    Візуалізація матриці кореляції
    
    Args:
        df: DataFrame
        figsize: розмір графіка
        save: чи зберігати графік
        filename: назва файлу
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr_matrix = df[numeric_cols].corr()
    
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', center=0,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
                vmin=-1, vmax=1, ax=ax)
    ax.set_title('Матриця кореляції', fontsize=16, pad=20)
    plt.tight_layout()
    
    if save:
        filepath = get_figures_path() / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Збережено: {filepath}")
    
    plt.show()


def plot_scatter_with_regression(df: pd.DataFrame,
                                 x_col: str,
                                 y_col: str,
                                 save: bool = False,
                                 filename: str = None) -> None:
    """
    Scatter plot з лінією регресії
    
    Args:
        df: DataFrame
        x_col: назва стовпця для осі X
        y_col: назва стовпця для осі Y
        save: чи зберігати графік
        filename: назва файлу
    """
    data = df[[x_col, y_col]].dropna()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(data[x_col], data[y_col], alpha=0.5, s=50)
    
    # Лінія тренду
    z = np.polyfit(data[x_col], data[y_col], 1)
    p = np.poly1d(z)
    ax.plot(data[x_col], p(data[x_col]), "r--", alpha=0.8, 
            linewidth=2, label='Trend line')
    
    # Кореляція
    correlation = data[x_col].corr(data[y_col])
    ax.text(0.05, 0.95, f'Correlation: {correlation:.3f}',
            transform=ax.transAxes, fontsize=12,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title(f'{y_col} vs {x_col}')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    
    if save:
        fname = filename or f'scatter_{x_col}_{y_col}'.replace(' ', '_') + '.png'
        filepath = get_figures_path() / fname
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Збережено: {filepath}")
    
    plt.show()


def plot_feature_importance(importance_dict: Dict[str, float],
                           top_n: int = 15,
                           save: bool = False,
                           filename: str = 'feature_importance.png') -> None:
    """
    Візуалізація важливості ознак
    
    Args:
        importance_dict: словник {feature: importance}
        top_n: кількість топ ознак
        save: чи зберігати графік
        filename: назва файлу
    """
    # Сортуємо за важливістю
    sorted_features = sorted(importance_dict.items(), 
                           key=lambda x: x[1], 
                           reverse=True)[:top_n]
    
    features, importance = zip(*sorted_features)
    
    fig, ax = plt.subplots(figsize=(10, max(6, top_n * 0.4)))
    bars = ax.barh(range(len(features)), importance)
    
    # Градієнтне забарвлення
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(features)))
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    ax.set_yticks(range(len(features)))
    ax.set_yticklabels(features)
    ax.set_xlabel('Importance')
    ax.set_title(f'Top {top_n} Feature Importance', fontsize=14)
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)
    
    # Додаємо значення
    for i, v in enumerate(importance):
        ax.text(v + max(importance) * 0.01, i, f'{v:.4f}', 
                va='center', fontsize=9)
    
    plt.tight_layout()
    
    if save:
        filepath = get_figures_path() / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Збережено: {filepath}")
    
    plt.show()


def plot_model_predictions(y_true: np.ndarray,
                          y_pred: np.ndarray,
                          title: str = 'Model Predictions',
                          save: bool = False,
                          filename: str = 'model_predictions.png') -> None:
    """
    Візуалізація фактичних vs передбачених значень
    
    Args:
        y_true: фактичні значення
        y_pred: передбачені значення
        title: заголовок графіка
        save: чи зберігати графік
        filename: назва файлу
    """
    from sklearn.metrics import r2_score, mean_squared_error
    
    r2 = r2_score(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Scatter plot
    axes[0].scatter(y_true, y_pred, alpha=0.5, s=50)
    axes[0].plot([y_true.min(), y_true.max()], 
                 [y_true.min(), y_true.max()], 
                 'r--', lw=2, label='Perfect prediction')
    axes[0].set_xlabel('Actual values')
    axes[0].set_ylabel('Predicted values')
    axes[0].set_title(f'{title}\nR² = {r2:.4f}, RMSE = {rmse:.4f}')
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    
    # Residuals
    residuals = y_true - y_pred
    axes[1].scatter(y_pred, residuals, alpha=0.5, s=50)
    axes[1].axhline(y=0, color='r', linestyle='--', lw=2)
    axes[1].set_xlabel('Predicted values')
    axes[1].set_ylabel('Residuals')
    axes[1].set_title('Residual Plot')
    axes[1].grid(alpha=0.3)
    
    plt.tight_layout()
    
    if save:
        filepath = get_figures_path() / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Збережено: {filepath}")
    
    plt.show()


def plot_grouped_comparison(df: pd.DataFrame,
                           group_col: str,
                           value_col: str,
                           top_n: int = 10,
                           save: bool = False,
                           filename: str = None) -> None:
    """
    Порівняння значень по групах
    
    Args:
        df: DataFrame
        group_col: колонка для групування
        value_col: колонка зі значеннями
        top_n: кількість топ груп
        save: чи зберігати графік
        filename: назва файлу
    """
    grouped = df.groupby(group_col)[value_col].mean().sort_values(ascending=False).head(top_n)
    
    fig, ax = plt.subplots(figsize=(10, max(6, top_n * 0.4)))
    bars = ax.barh(range(len(grouped)), grouped.values)
    
    # Кольори
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(grouped)))
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    ax.set_yticks(range(len(grouped)))
    ax.set_yticklabels(grouped.index)
    ax.set_xlabel(f'Average {value_col}')
    ax.set_title(f'Top {top_n} {group_col} by {value_col}')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)
    
    # Значення
    for i, v in enumerate(grouped.values):
        ax.text(v + max(grouped.values) * 0.01, i, f'{v:.2f}', 
                va='center', fontsize=9)
    
    plt.tight_layout()
    
    if save:
        fname = filename or f'grouped_{group_col}_{value_col}'.replace(' ', '_') + '.png'
        filepath = get_figures_path() / fname
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Збережено: {filepath}")
    
    plt.show()


if __name__ == "__main__":
    # Приклад використання
    import sys
    sys.path.append('.')
    from data_load import load_data
    
    try:
        setup_plot_style()
        df = load_data()
        
        print("Створення візуалізацій...")
        
        # Пропущені значення
        plot_missing_values(df, save=True)
        
        # Розподіл Life Expectancy
        plot_distribution(df, 'Life expectancy ', save=True)
        
        # Кореляційна матриця
        plot_correlation_matrix(df, save=True)
        
        print("\n✓ Візуалізації створено!")
        
    except Exception as e:
        print(f"Помилка: {e}")
