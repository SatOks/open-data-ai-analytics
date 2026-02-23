"""
Модуль для аналізу якості даних
Перевіряє цілісність, повноту та коректність даних
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


def check_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Аналіз пропущених значень у датасеті
    
    Args:
        df: DataFrame для аналізу
        
    Returns:
        DataFrame з інформацією про пропущені значення
    """
    missing = pd.DataFrame({
        'column': df.columns,
        'missing_count': df.isnull().sum().values,
        'missing_percentage': (df.isnull().sum().values / len(df) * 100).round(2)
    })
    
    missing = missing[missing['missing_count'] > 0].sort_values(
        'missing_percentage', ascending=False
    ).reset_index(drop=True)
    
    return missing


def check_duplicates(df: pd.DataFrame, subset: List[str] = None) -> Dict:
    """
    Перевірка наявності дублікатів
    
    Args:
        df: DataFrame для перевірки
        subset: список колонок для перевірки дублікатів
        
    Returns:
        Словник з інформацією про дублікати
    """
    duplicates = df.duplicated(subset=subset, keep=False)
    duplicate_rows = df[duplicates]
    
    return {
        'total_duplicates': duplicates.sum(),
        'duplicate_percentage': (duplicates.sum() / len(df) * 100).round(2),
        'duplicate_rows': duplicate_rows
    }


def detect_outliers_iqr(df: pd.DataFrame, column: str, 
                        multiplier: float = 1.5) -> Tuple[pd.Series, Dict]:
    """
    Виявлення викидів методом міжквартильного розмаху (IQR)
    
    Args:
        df: DataFrame
        column: назва стовпця для аналізу
        multiplier: множник для IQR (зазвичай 1.5 або 3.0)
        
    Returns:
        Кортеж: (булева серія з викидами, словник зі статистикою)
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
    
    stats = {
        'Q1': Q1,
        'Q3': Q3,
        'IQR': IQR,
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'outliers_count': outliers.sum(),
        'outliers_percentage': (outliers.sum() / len(df) * 100).round(2)
    }
    
    return outliers, stats


def detect_outliers_zscore(df: pd.DataFrame, column: str, 
                          threshold: float = 3.0) -> Tuple[pd.Series, Dict]:
    """
    Виявлення викидів методом Z-score
    
    Args:
        df: DataFrame
        column: назва стовпця для аналізу
        threshold: поріг Z-score (зазвичай 3.0)
        
    Returns:
        Кортеж: (булева серія з викидами, словник зі статистикою)
    """
    mean = df[column].mean()
    std = df[column].std()
    z_scores = np.abs((df[column] - mean) / std)
    
    outliers = z_scores > threshold
    
    stats = {
        'mean': mean,
        'std': std,
        'threshold': threshold,
        'outliers_count': outliers.sum(),
        'outliers_percentage': (outliers.sum() / len(df) * 100).round(2)
    }
    
    return outliers, stats


def check_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Перевірка типів даних та їх відповідності
    
    Args:
        df: DataFrame для аналізу
        
    Returns:
        DataFrame з інформацією про типи даних
    """
    type_info = pd.DataFrame({
        'column': df.columns,
        'dtype': df.dtypes.values,
        'non_null_count': df.count().values,
        'unique_values': [df[col].nunique() for col in df.columns]
    })
    
    return type_info


def generate_quality_report(df: pd.DataFrame) -> Dict:
    """
    Генерує повний звіт про якість даних
    
    Args:
        df: DataFrame для аналізу
        
    Returns:
        Словник з детальною інформацією про якість даних
    """
    report = {
        'basic_info': {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
        },
        'missing_values': check_missing_values(df),
        'duplicates': check_duplicates(df),
        'data_types': check_data_types(df)
    }
    
    # Аналіз числових стовпців
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    outliers_summary = {}
    
    for col in numeric_cols:
        if df[col].notna().sum() > 0:  # Якщо є непусті значення
            _, stats = detect_outliers_iqr(df.dropna(subset=[col]), col)
            outliers_summary[col] = stats
    
    report['outliers'] = outliers_summary
    
    return report


def print_quality_report(report: Dict):
    """
    Виводить звіт про якість даних у читабельному форматі
    
    Args:
        report: словник зі звітом
    """
    print("=" * 70)
    print("ЗВІТ ПРО ЯКІСТЬ ДАНИХ")
    print("=" * 70)
    
    # Базова інформація
    print("\n📊 БАЗОВА ІНФОРМАЦІЯ")
    print(f"  Всього рядків: {report['basic_info']['total_rows']:,}")
    print(f"  Всього стовпців: {report['basic_info']['total_columns']}")
    print(f"  Використання пам'яті: {report['basic_info']['memory_usage_mb']:.2f} MB")
    
    # Пропущені значення
    print("\n❌ ПРОПУЩЕНІ ЗНАЧЕННЯ")
    if len(report['missing_values']) > 0:
        print(report['missing_values'].to_string(index=False))
    else:
        print("  ✓ Пропущених значень не знайдено")
    
    # Дублікати
    print("\n🔄 ДУБЛІКАТИ")
    dup_count = report['duplicates']['total_duplicates']
    dup_pct = report['duplicates']['duplicate_percentage']
    if dup_count > 0:
        print(f"  Знайдено {dup_count} дублікатів ({dup_pct}%)")
    else:
        print("  ✓ Дублікатів не знайдено")
    
    # Викиди
    print("\n📈 ВИКИДИ (IQR METHOD)")
    outliers = report['outliers']
    if outliers:
        for col, stats in list(outliers.items())[:5]:  # Показати перші 5
            print(f"  {col}: {stats['outliers_count']} ({stats['outliers_percentage']}%)")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Приклад використання
    import sys
    sys.path.append('.')
    from data_load import load_data
    
    try:
        df = load_data()
        report = generate_quality_report(df)
        print_quality_report(report)
        
    except FileNotFoundError as e:
        print(f"Помилка: {e}")
