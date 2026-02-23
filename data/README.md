# Data Directory

Ця папка містить дані для аналізу проєкту.

## Структура

- `raw/` - сирі дані (не комітяться в Git через .gitignore)
- `processed/` - оброблені дані після попередньої обробки

## Джерело даних

**Dataset:** Life Expectancy (WHO)  
**Kaggle:** https://www.kaggle.com/datasets/kumarajarshi/life-expectancy-who/data

## Інструкція з завантаження

### Варіант 1: Ручне завантаження з Kaggle

1. Перейдіть на сторінку датасету: https://www.kaggle.com/datasets/kumarajarshi/life-expectancy-who/data
2. Натисніть кнопку "Download" (потрібен акаунт Kaggle)
3. Розпакуйте архів і помістіть файл `Life Expectancy Data.csv` у папку `data/raw/`

### Варіант 2: Використання Kaggle API

```bash
# Встановіть залежності
pip install -r requirements.txt

# Налаштуйте Kaggle API credentials (kaggle.json)
# Докладніше: https://www.kaggle.com/docs/api

# Запустіть скрипт завантаження
python src/data_load.py
```

### Варіант 3: Використання модуля data_load

```python
from src.data_load import download_from_kaggle, load_data

# Завантаження з Kaggle
download_from_kaggle()

# Завантаження у pandas DataFrame
df = load_data()
```
