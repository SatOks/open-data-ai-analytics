"""
Модуль для завантаження даних про очікувану тривалість життя (WHO)
"""

import os
import pandas as pd
from pathlib import Path


def get_project_root() -> Path:
    """
    Повертає кореневу директорію проєкту
    """
    return Path(__file__).parent.parent


def get_data_path(filename: str = "Life Expectancy Data.csv") -> Path:
    """
    Повертає шлях до файлу даних
    
    Args:
        filename: назва файлу з даними
        
    Returns:
        Path: шлях до файлу
    """
    root = get_project_root()
    data_dir = root / "data" / "raw"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / filename


def load_data(filepath: str = None) -> pd.DataFrame:
    """
    Завантажує дані про очікувану тривалість життя
    
    Args:
        filepath: шлях до CSV файлу (опціонально)
        
    Returns:
        pd.DataFrame: завантажені дані
        
    Raises:
        FileNotFoundError: якщо файл не знайдено
    """
    if filepath is None:
        filepath = get_data_path()
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Файл даних не знайдено: {filepath}\n"
            f"Будь ласка, завантажте датасет з:\n"
            f"https://www.kaggle.com/datasets/kumarajarshi/life-expectancy-who/data\n"
            f"і розмістіть у папці data/raw/"
        )
    
    print(f"Завантаження даних з {filepath}...")
    df = pd.read_csv(filepath)
    print(f"✓ Завантажено {len(df)} рядків та {len(df.columns)} стовпців")
    
    return df


def get_data_info(df: pd.DataFrame) -> dict:
    """
    Повертає базову інформацію про датасет
    
    Args:
        df: DataFrame з даними
        
    Returns:
        dict: словник з інформацією про дані
    """
    info = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "memory_usage": df.memory_usage(deep=True).sum() / 1024**2  # MB
    }
    
    return info


def download_from_kaggle(dataset_name: str = "kumarajarshi/life-expectancy-who"):
    """
    Завантажує датасет з Kaggle (потребує налаштованого Kaggle API)
    
    Args:
        dataset_name: назва датасету на Kaggle
    """
    try:
        import opendatasets as od
        
        data_dir = get_project_root() / "data" / "raw"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Завантаження датасету {dataset_name} з Kaggle...")
        od.download(f"https://www.kaggle.com/datasets/{dataset_name}/data", 
                   data_dir=str(data_dir))
        print("✓ Дані успішно завантажено!")
        
    except ImportError:
        print("Помилка: встановіть opendatasets: pip install opendatasets")
    except Exception as e:
        print(f"Помилка завантаження: {e}")
        print("Переконайтеся, що налаштовано Kaggle API credentials")


if __name__ == "__main__":
    # Приклад використання
    try:
        df = load_data()
        info = get_data_info(df)
        
        print("\n" + "="*50)
        print("ІНФОРМАЦІЯ ПРО ДАТАСЕТ")
        print("="*50)
        print(f"Розмір: {info['shape'][0]} рядків × {info['shape'][1]} стовпців")
        print(f"Використання пам'яті: {info['memory_usage']:.2f} MB")
        print(f"\nСтовпці: {', '.join(info['columns'][:5])}...")
        print(f"\nПерші 5 рядків:")
        print(df.head())
        
    except FileNotFoundError as e:
        print(f"\n{e}")
        print("\nСпроба завантажити з Kaggle...")
        download_from_kaggle()
