"""
Модуль для дослідження даних та побудови моделей
Включає статистичний аналіз, перевірку гіпотез та ML моделі
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')


def prepare_data_for_modeling(df: pd.DataFrame, 
                               target: str = 'Life expectancy ',
                               test_size: float = 0.2,
                               random_state: int = 42) -> Tuple:
    """
    Підготовка даних для моделювання
    
    Args:
        df: вхідний DataFrame
        target: цільова змінна
        test_size: розмір тестової вибірки
        random_state: random seed
        
    Returns:
        Кортеж: (X_train, X_test, y_train, y_test, feature_names)
    """
    # Копіюємо дані
    data = df.copy()
    
    # Видаляємо рядки з пропущеним target
    if target in data.columns:
        data = data.dropna(subset=[target])
    else:
        raise ValueError(f"Target column '{target}' not found in DataFrame")
    
    # Вибираємо тільки числові стовпці
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    
    # Видаляємо target зі списку features
    if target in numeric_cols:
        numeric_cols.remove(target)
    
    # Заповнюємо пропущені значення медіаною
    for col in numeric_cols:
        if data[col].isnull().sum() > 0:
            data[col].fillna(data[col].median(), inplace=True)
    
    X = data[numeric_cols]
    y = data[target]
    
    # Розділення на train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    return X_train, X_test, y_train, y_test, numeric_cols


def train_linear_regression(X_train, y_train, X_test, y_test) -> Dict:
    """
    Навчання лінійної регресії
    
    Args:
        X_train, y_train: тренувальні дані
        X_test, y_test: тестові дані
        
    Returns:
        Словник з моделлю та метриками
    """
    # Нормалізація
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Навчання моделі
    model = LinearRegression()
    model.fit(X_train_scaled, y_train)
    
    # Прогнози
    y_train_pred = model.predict(X_train_scaled)
    y_test_pred = model.predict(X_test_scaled)
    
    # Метрики
    results = {
        'model': model,
        'scaler': scaler,
        'train_metrics': {
            'r2': r2_score(y_train, y_train_pred),
            'rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'mae': mean_absolute_error(y_train, y_train_pred)
        },
        'test_metrics': {
            'r2': r2_score(y_test, y_test_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
            'mae': mean_absolute_error(y_test, y_test_pred)
        },
        'predictions': {
            'y_train_pred': y_train_pred,
            'y_test_pred': y_test_pred
        }
    }
    
    return results


def train_random_forest(X_train, y_train, X_test, y_test, 
                        n_estimators: int = 100,
                        max_depth: Optional[int] = None,
                        random_state: int = 42) -> Dict:
    """
    Навчання Random Forest
    
    Args:
        X_train, y_train: тренувальні дані
        X_test, y_test: тестові дані
        n_estimators: кількість дерев
        max_depth: максимальна глибина дерева
        random_state: random seed
        
    Returns:
        Словник з моделлю та метриками
    """
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Прогнози
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Метрики
    results = {
        'model': model,
        'train_metrics': {
            'r2': r2_score(y_train, y_train_pred),
            'rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'mae': mean_absolute_error(y_train, y_train_pred)
        },
        'test_metrics': {
            'r2': r2_score(y_test, y_test_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
            'mae': mean_absolute_error(y_test, y_test_pred)
        },
        'predictions': {
            'y_train_pred': y_train_pred,
            'y_test_pred': y_test_pred
        },
        'feature_importance': dict(zip(X_train.columns, model.feature_importances_))
    }
    
    return results


def train_gradient_boosting(X_train, y_train, X_test, y_test,
                            n_estimators: int = 100,
                            learning_rate: float = 0.1,
                            max_depth: int = 3,
                            random_state: int = 42) -> Dict:
    """
    Навчання Gradient Boosting
    
    Args:
        X_train, y_train: тренувальні дані
        X_test, y_test: тестові дані
        n_estimators: кількість ітерацій
        learning_rate: швидкість навчання
        max_depth: максимальна глибина дерева
        random_state: random seed
        
    Returns:
        Словник з моделлю та метриками
    """
    model = GradientBoostingRegressor(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        random_state=random_state
    )
    
    model.fit(X_train, y_train)
    
    # Прогнози
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Метрики
    results = {
        'model': model,
        'train_metrics': {
            'r2': r2_score(y_train, y_train_pred),
            'rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'mae': mean_absolute_error(y_train, y_train_pred)
        },
        'test_metrics': {
            'r2': r2_score(y_test, y_test_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
            'mae': mean_absolute_error(y_test, y_test_pred)
        },
        'predictions': {
            'y_train_pred': y_train_pred,
            'y_test_pred': y_test_pred
        },
        'feature_importance': dict(zip(X_train.columns, model.feature_importances_))
    }
    
    return results


def compare_models(results_dict: Dict[str, Dict]) -> pd.DataFrame:
    """
    Порівняння результатів різних моделей
    
    Args:
        results_dict: словник з результатами моделей
        
    Returns:
        DataFrame з порівняльними метриками
    """
    comparison = []
    
    for model_name, results in results_dict.items():
        comparison.append({
            'Model': model_name,
            'Train R²': results['train_metrics']['r2'],
            'Test R²': results['test_metrics']['r2'],
            'Train RMSE': results['train_metrics']['rmse'],
            'Test RMSE': results['test_metrics']['rmse'],
            'Train MAE': results['train_metrics']['mae'],
            'Test MAE': results['test_metrics']['mae']
        })
    
    return pd.DataFrame(comparison).round(4)


def get_feature_importance(results: Dict, top_n: int = 10) -> pd.DataFrame:
    """
    Отримати найважливіші ознаки для моделей на основі дерев
    
    Args:
        results: результати моделі
        top_n: кількість найважливіших ознак
        
    Returns:
        DataFrame з важливістю ознак
    """
    if 'feature_importance' not in results:
        return None
    
    importance_df = pd.DataFrame(
        list(results['feature_importance'].items()),
        columns=['Feature', 'Importance']
    )
    
    importance_df = importance_df.sort_values('Importance', ascending=False).head(top_n)
    return importance_df.reset_index(drop=True)


def calculate_correlation_with_target(df: pd.DataFrame, 
                                      target: str = 'Life expectancy ',
                                      top_n: int = 10) -> pd.DataFrame:
    """
    Розрахунок кореляції змінних з цільовою змінною
    
    Args:
        df: DataFrame
        target: назва цільової змінної
        top_n: кількість топ корельованих змінних
        
    Returns:
        DataFrame з кореляціями
    """
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlations = df[numeric_cols].corr()[target].drop(target).sort_values(
        ascending=False, key=abs
    )
    
    result = pd.DataFrame({
        'Feature': correlations.index,
        'Correlation': correlations.values
    }).head(top_n).reset_index(drop=True)
    
    return result


if __name__ == "__main__":
    # Приклад використання
    import sys
    sys.path.append('.')
    from data_load import load_data
    
    try:
        print("Завантаження даних...")
        df = load_data()
        
        print("\nПідготовка даних для моделювання...")
        X_train, X_test, y_train, y_test, features = prepare_data_for_modeling(df)
        
        print(f"Train set: {X_train.shape}")
        print(f"Test set: {X_test.shape}")
        
        print("\nНавчання моделей...")
        lr_results = train_linear_regression(X_train, y_train, X_test, y_test)
        rf_results = train_random_forest(X_train, y_train, X_test, y_test)
        
        print("\nПорівняння моделей:")
        comparison = compare_models({
            'Linear Regression': lr_results,
            'Random Forest': rf_results
        })
        print(comparison)
        
    except Exception as e:
        print(f"Помилка: {e}")
