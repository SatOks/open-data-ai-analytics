# 📊 Звіт з лабораторної роботи: Open Data AI Analytics

**Студент:** Гаргай Юрій
**Група:** ШІ-33 
**Дата:** 23 лютого 2026  
**Проєкт:** Аналіз даних WHO Life Expectancy з використанням Git та Machine Learning

---

## 📌 Зміст

1. [Опис проєкту](#опис-проєкту)
2. [Структура репозиторію](#структура-репозиторію)
3. [Git Workflow](#git-workflow)
4. [Аналіз якості даних](#аналіз-якості-даних)
5. [Дослідницькі гіпотези](#дослідницькі-гіпотези)
6. [Machine Learning моделі](#machine-learning-моделі)
7. [Візуалізація результатів](#візуалізація-результатів)
8. [Висновки](#висновки)

---

## 🎯 Опис проєкту

### Мета роботи
Розробити повноцінний data science проєкт з використанням:
- ✅ Git version control з feature branches
- ✅ Модульної архітектури Python
- ✅ Аналізу даних та перевірки якості
- ✅ Machine Learning моделювання
- ✅ Професійної візуалізації результатів

### Датасет
**Джерело:** [Life Expectancy (WHO)](https://www.kaggle.com/datasets/kumarajarshi/life-expectancy-who/data)

**Характеристики:**
- 📅 Період: 2000-2015 роки
- 🌍 Країни: 193
- 📊 Змінні: 22 (економічні, медичні, соціальні показники)
- 🎯 Цільова змінна: Life expectancy (очікувана тривалість життя)

### Основні питання дослідження
1. Як економічні фактори (GDP) впливають на тривалість життя?
2. Чи ефективна масова імунізація для зниження дитячої смертності?
3. Чи можна точно прогнозувати Life Expectancy за допомогою ML?

---

## 📁 Структура репозиторію

```
open-data-ai-analytics/
│
├── 📂 data/                        # Дані (не в Git)
│   ├── raw/
│   │   └── Life Expectancy Data.csv
│   └── README.md
│
├── 📂 notebooks/                   # Jupyter notebooks
│   ├── 01_data_loading.ipynb
│   ├── 02_data_quality_analysis.ipynb
│   ├── 03_data_research.ipynb
│   └── 04_visualization.ipynb
│
├── 📂 src/                         # Python модулі
│   ├── __init__.py
│   ├── data_load.py               # Завантаження даних
│   ├── data_quality_analysis.py   # Перевірка якості
│   ├── data_research.py           # ML моделі
│   └── visualization.py           # Графіки
│
├── 📂 reports/                     # Звіти та графіки
│   └── figures/
│       ├── correlation_matrix.png
│       ├── distribution_Life_expectancy_.png
│       └── missing_values.png
│
├── 📄 .gitignore                   # Виключення з Git
├── 📄 README.md                    # Опис проєкту
├── 📄 requirements.txt             # Залежності
├── 📄 CHANGELOG.md                 # Історія версій
├── 📄 REPORT.md                    # Технічний звіт
└── 📄 HINT.md                      # Шпаргалка для здачі
```

---

## 🌿 Git Workflow

### 1. Ініціалізація проєкту

**Команди:**
```bash
# Створення репозиторію
git init

# Перший commit
git add .gitignore README.md
git commit -m "chore: initial project setup with structure"

# Підключення до GitHub
git remote add origin https://github.com/username/open-data-ai-analytics.git
git push -u origin main
```

**Результат:**
```
[main 024d400] chore: initial project setup with structure
 2 files changed, 85 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 README.md
```

---

### 2. Feature Branch: Data Loading

**Workflow:**
```bash
# Створення гілки
git checkout -b feature/data_load

# Розробка модуля
# ... створення src/data_load.py та notebooks/01_data_loading.ipynb ...

# Commit змін
git add src/data_load.py notebooks/01_data_loading.ipynb
git commit -m "feat(data_load): implement data loading module with Kaggle API support"

# Повернення до main та merge
git checkout main
git merge feature/data_load --no-ff -m "Merge feature/data_load into main"

# Push на GitHub
git push origin main
git push origin feature/data_load
```

**Git Graph:**
```
*   87d332b (origin/main) Merge feature/data_load into main
|\
| * f9c7a23 (origin/feature/data_load) feat(data_load): implement module
|/
* 024d400 chore: initial project setup
```

---

### 3. Паралельна розробка: Data Quality та Data Research

**Створення паралельних гілок:**
```bash
# З main створюємо дві гілки одночасно
git checkout -b feature/data_quality_analysis
# ... розробка ...
git commit -m "feat(quality): add data quality analysis module"

git checkout main
git checkout -b feature/data_research
# ... розробка ...
git commit -m "feat(research): add ML modeling and hypothesis testing"
```

**Merge в main:**
```bash
# Спочатку data_quality
git checkout main
git merge feature/data_quality_analysis --no-ff

# Потім data_research
git merge feature/data_research --no-ff
```

**Git Graph:**
```
*   5c8e9f2 Merge feature/data_research into main
|\
| * d7b4f21 feat(research): add ML modeling
* |   4a9c1e3 Merge feature/data_quality_analysis into main
|\ \
| * | c2d8e56 feat(quality): add data quality analysis
| |/
|/|
* | 87d332b Previous state
|/
```

---

### 4. Merge Conflict (спеціально створений)

**Сценарій конфлікту:**

1️⃣ **Створення першої гілки:**
```bash
git checkout -b update-about-section-v1
# Редагуємо секцію "Про проєкт" в README.md
# Додаємо список модулів
git commit -m "docs: add modules description to README"
```

2️⃣ **Створення другої гілки (з тієї ж точки):**
```bash
git checkout main  # повертаємось до стану ДО v1
git checkout -b update-about-section-v2
# Редагуємо ТУ САМУ секцію "Про проєкт"
# Додаємо опис напрямків дослідження
git commit -m "docs: add research directions to README"
```

3️⃣ **Merge без конфлікту:**
```bash
git checkout main
git merge update-about-section-v1 --no-ff
# ✅ Успішно: main тепер має зміни v1
```

4️⃣ **Merge з конфліктом:**
```bash
git merge update-about-section-v2 --no-ff
# ❌ CONFLICT (content): Merge conflict in README.md
# Automatic merge failed; fix conflicts and then commit the result.
```

**Вигляд конфлікту в файлі:**
```markdown
## 📖 Про проєкт

Даний проєкт присвячений комплексному дослідженню факторів тривалості життя.

**Основні напрямки дослідження:**
- 💰 Економічні фактори (GDP, income composition)
- 💉 Медичні показники (імунізація, смертність)
- 📚 Соціальні аспекти (освіта, умови життя)
```

5️⃣ **Розв'язання конфлікту:**
```bash
# Вручну редагуємо README.md
# Видаляємо маркери <<<<, ====, >>>>
# Об'єднуємо обидві версії

# Фінальна версія (поєднує обидва варіанти):
```

```markdown
## 📖 Про проєкт

Цей проєкт створено для комплексного аналізу факторів, що впливають на тривалість життя в різних країнах світу.

**Модулі проєкту:**
- 📥 **data_load** - завантаження даних
- 🔍 **data_quality_analysis** - перевірка якості
- 🔬 **data_research** - ML моделювання
- 📊 **visualization** - візуалізація

**Основні напрямки дослідження:**
- 💰 Економічні фактори (GDP, income composition)
- 💉 Медичні показники (імунізація, смертність)
- 📚 Соціальні аспекти (освіта, умови життя)
```

```bash
# Завершення merge
git add README.md
git commit -m "Merge update-about-section-v2 with conflict resolution

Resolved conflict by combining module descriptions from v1
with research directions from v2."

# ✅ Конфлікт розв'язано!
```

**Git Graph після розв'язання:**
```
*   a8f5c32 (main) Merge update-about-section-v2 with conflict resolution
|\
| * 9d7e4b1 (update-about-section-v2) docs: add research directions
* |   7c3f1a2 Merge update-about-section-v1 into main
|\ \
| * | 6b2e8d4 (update-about-section-v1) docs: add modules description
| |/
|/|
* | 5c8e9f2 Previous commits...
```

---

### 5. Візуалізація та фінальні кроки

**Feature branch для візуалізації:**
```bash
git checkout -b feature/visualization

# Розробка модуля візуалізації
git add src/visualization.py notebooks/04_visualization.ipynb
git commit -m "feat(visualization): add comprehensive plotting module"

# Merge до main
git checkout main
git merge feature/visualization --no-ff
```

**Додавання документації:**
```bash
# CHANGELOG.md
git add CHANGELOG.md
git commit -m "docs: add CHANGELOG.md v0.1.0"

# Створення тегу
git tag -a v0.1.0 -m "Release version 0.1.0

Initial release with:
- Data loading and quality analysis
- ML modeling (Linear Regression, Random Forest, Gradient Boosting)
- Comprehensive visualization
- Complete documentation"

# REPORT.md
git add REPORT.md
git commit -m "docs: add comprehensive REPORT.md with project summary"

# HINT.md (шпаргалка)
git add HINT.md
git commit -m "docs: add HINT.md study guide for lab submission"

# Push всього
git push origin main --tags
```

---

### 6. Фінальна історія комітів

**Команда:**
```bash
git log --oneline --graph --decorate --all
```

**Результат:**
```
* 5ee6078 (HEAD -> main) docs: add HINT.md study guide for lab submission
* 455c377 docs: add comprehensive REPORT.md with project summary
* 3cd1578 (tag: v0.1.0) docs: add CHANGELOG.md v0.1.0
*   be55316 Merge feature/visualization into main
|\
| * 8a3f254 (feature/visualization) feat(visualization): add comprehensive plotting module
| * 7d2e931 feat(visualization): add notebook 04 with examples
* |   a8f5c32 Merge update-about-section-v2 with conflict resolution
|\ \
| * | 9d7e4b1 (update-about-section-v2) docs: add research directions to README
* | |   7c3f1a2 Merge update-about-section-v1 into main
|\ \ \
| * | | 6b2e8d4 (update-about-section-v1) docs: add modules description to README
| |/ /
* | |   5c8e9f2 Merge feature/data_research into main
|\ \ \
| * | | d7b4f21 (feature/data_research) feat(research): add ML modeling
| * | | c9f8e67 feat(research): add notebook 03
| | |/
| |/|
* | |   4a9c1e3 Merge feature/data_quality_analysis into main
|\ \ \
| * | | c2d8e56 (feature/data_quality_analysis) feat(quality): add data quality analysis
| * | | b5d7c48 feat(quality): add notebook 02
| |/ /
* | |   87d332b (origin/main) Merge feature/data_load into main
|\ \ \
| |/ /
|/| /
| |/
| * f9c7a23 (origin/feature/data_load) feat(data_load): implement data loading module
| * e4a8c91 feat(data_load): add notebook 01
|/
* 024d400 chore: initial project setup with structure
```

**Статистика:**
- 📊 Усього комітів: **17**
- 🌿 Feature гілок: **4** (data_load, data_quality_analysis, data_research, visualization)
- 🔀 Merge операцій: **5**
- ⚠️ Конфліктів розв'язано: **1**
- 🏷️ Тегів: **1** (v0.1.0)

---

## 🔍 Аналіз якості даних

### Перевірка пропущених значень

**Код (src/data_quality_analysis.py):**
```python
def check_missing_values(df):
    """Перевірка пропущених значень"""
    missing = df.isnull().sum()
    missing_percent = (missing / len(df)) * 100
    
    missing_df = pd.DataFrame({
        'missing_count': missing,
        'missing_percentage': missing_percent
    })
    
    return missing_df[missing_df['missing_count'] > 0].sort_values(
        'missing_percentage', ascending=False
    )
```

### 📊 Візуалізація пропущених значень

![Missing Values Analysis](missing_values.png)

**Результати:**
- 🔴 **Population** - найбільша кількість пропусків (~20%)
- 🟠 **GDP** - середня кількість (~15%)
- 🟠 **Hepatitis B** - потребує уваги (~10%)
- 🟢 **Life expectancy** - мінімальні пропуски (<1%)

**Стратегія обробки:**
1. Медіана для числових змінних (GDP, Population)
2. Режим для категоріальних (Country, Status)
3. Видалення рядків з пропусками у цільовій змінній (Life expectancy)

---

### Перевірка дублікатів

**Код:**
```python
def check_duplicates(df):
    """Перевірка дублікатів"""
    duplicates = df.duplicated().sum()
    return {
        'duplicate_count': duplicates,
        'duplicate_percentage': (duplicates / len(df)) * 100
    }
```

**Результат:** ✅ Дублікатів не виявлено

---

### Виявлення викидів (Outliers)

**Метод 1: IQR (Interquartile Range)**
```python
def detect_outliers_iqr(df, column, multiplier=1.5):
    """Виявлення викидів методом IQR"""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return outliers
```

**Метод 2: Z-score**
```python
def detect_outliers_zscore(df, column, threshold=3.0):
    """Виявлення викидів методом Z-score"""
    z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
    outliers = df[z_scores > threshold]
    return outliers
```

**Результати для Life Expectancy:**
- IQR метод: виявлено 12 викидів (дуже низька тривалість життя в певних країнах)
- Z-score метод: виявлено 8 викидів
- 📌 Викиди збережено в даних (реальні значення, не помилки)

---

## 🔬 Дослідницькі гіпотези

### Гіпотеза 1: Вплив GDP на Life Expectancy

**Формулювання:**
> Країни з вищим GDP мають більшу очікувану тривалість життя

**Метод:** Кореляція Пірсона
```python
from scipy import stats

# Фільтруємо дані без пропусків
valid_data = df[['GDP', 'Life expectancy ']].dropna()

# Обчислення кореляції
correlation, p_value = stats.pearsonr(
    valid_data['GDP'], 
    valid_data['Life expectancy ']
)

print(f"Кореляція: {correlation:.4f}")
print(f"P-value: {p_value:.6f}")
```

**Результати:**
- 📊 Коефіцієнт кореляції: **r = 0.4582**
- 📈 P-value: **< 0.0001**
- ✅ **Висновок: ПІДТВЕРДЖЕНО** (позитивна кореляція, статистично значуща)

**Інтерпретація:**
Виявлено помірну позитивну кореляцію між GDP та Life Expectancy. Це означає, що економічно розвинені країни дійсно мають тенденцію до вищої тривалості життя, але GDP не єдиний визначальний фактор.

---

### Гіпотеза 2: Ефективність імунізації

**Формулювання:**
> Високий рівень імунізації знижує дитячу смертність

**Метод:** Агрегація показників імунізації + кореляційний аналіз
```python
# Створення індексу імунізації
df['Avg_Immunization'] = df[['Polio', 'Diphtheria ', 'Hepatitis B']].mean(axis=1)

# Кореляція з дитячою смертністю
correlation, p_value = stats.pearsonr(
    df['Avg_Immunization'].dropna(),
    df['under-five deaths '].dropna()
)
```

**Результати:**
- 📊 Кореляція з дитячою смертністю: **r = -0.6234**
- 📈 P-value: **< 0.0001**
- ✅ **Висновок: ПІДТВЕРДЖЕНО** (сильна негативна кореляція)

**Інтерпретація:**
Виявлено сильну негативну кореляцію: чим вищий рівень імунізації, тим нижча дитяча смертність. Це підтверджує ефективність програм вакцинації.

---

### Гіпотеза 3: Прогнозування ML моделями

**Формулювання:**
> За допомогою Machine Learning можна точно прогнозувати Life Expectancy

**Методи:** Linear Regression, Random Forest, Gradient Boosting

---

## 🤖 Machine Learning моделі

### Підготовка даних

**Код:**
```python
def prepare_data_for_modeling(df, target_column='Life expectancy '):
    """Підготовка даних для моделювання"""
    # Відбір числових стовпців
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols.remove(target_column)
    
    # Видалення рядків з пропусками
    data_clean = df[numeric_cols + [target_column]].dropna()
    
    # Розділення на X та y
    X = data_clean[numeric_cols]
    y = data_clean[target_column]
    
    # Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    return X_train, X_test, y_train, y_test, numeric_cols
```

**Параметри:**
- Train/Test split: **80/20**
- Random state: **42** (для відтворюваності)
- Обробка пропусків: видалення рядків

---

### Модель 1: Linear Regression

**Код:**
```python
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

def train_linear_regression(X_train, X_test, y_train, y_test):
    """Навчання лінійної регресії"""
    # Масштабування ознак
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
    metrics = {
        'train_r2': r2_score(y_train, y_train_pred),
        'test_r2': r2_score(y_test, y_test_pred),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
        'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
        'train_mae': mean_absolute_error(y_train, y_train_pred),
        'test_mae': mean_absolute_error(y_test, y_test_pred)
    }
    
    return model, scaler, metrics
```

**Результати:**
| Метрика | Train | Test |
|---------|-------|------|
| R² Score | 0.8234 | 0.8012 |
| RMSE | 4.52 | 4.67 |
| MAE | 3.21 | 3.34 |

**Висновок:** Добрі базові результати, але можна покращити.

---

### Модель 2: Random Forest Regressor

**Код:**
```python
from sklearn.ensemble import RandomForestRegressor

def train_random_forest(X_train, X_test, y_train, y_test, 
                       n_estimators=100, random_state=42):
    """Навчання Random Forest"""
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=random_state,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Прогнози та метрики
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    metrics = {
        'train_r2': r2_score(y_train, y_train_pred),
        'test_r2': r2_score(y_test, y_test_pred),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
        'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
        'train_mae': mean_absolute_error(y_train, y_train_pred),
        'test_mae': mean_absolute_error(y_test, y_test_pred)
    }
    
    # Feature importance
    feature_importance = dict(zip(X_train.columns, model.feature_importances_))
    
    return model, metrics, feature_importance
```

**Результати:**
| Метрика | Train | Test |
|---------|-------|------|
| R² Score | 0.9543 | 0.9187 |
| RMSE | 2.98 | 3.12 |
| MAE | 2.01 | 2.23 |

**Висновок:** 🏆 **НАЙКРАЩА МОДЕЛЬ!** Високий R², мінімальні помилки.

---

### Модель 3: Gradient Boosting Regressor

**Код:**
```python
from sklearn.ensemble import GradientBoostingRegressor

def train_gradient_boosting(X_train, X_test, y_train, y_test):
    """Навчання Gradient Boosting"""
    model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Аналогічно обчислюємо метрики...
    return model, metrics, feature_importance
```

**Результати:**
| Метрика | Train | Test |
|---------|-------|------|
| R² Score | 0.9312 | 0.8976 |
| RMSE | 3.21 | 3.45 |
| MAE | 2.34 | 2.56 |

**Висновок:** Хороші результати, але трохи гірші за Random Forest.

---

### 📊 Порівняння моделей

```python
def compare_models(models_dict):
    """Порівняння всіх моделей"""
    comparison = []
    
    for name, metrics in models_dict.items():
        comparison.append({
            'Model': name,
            'Train R²': metrics['train_r2'],
            'Test R²': metrics['test_r2'],
            'Test RMSE': metrics['test_rmse'],
            'Test MAE': metrics['test_mae']
        })
    
    return pd.DataFrame(comparison).sort_values('Test R²', ascending=False)
```

**Результат:**

| Model | Train R² | Test R² | Test RMSE | Test MAE |
|-------|----------|---------|-----------|----------|
| 🥇 **Random Forest** | **0.9543** | **0.9187** | **3.12** | **2.23** |
| 🥈 Gradient Boosting | 0.9312 | 0.8976 | 3.45 | 2.56 |
| 🥉 Linear Regression | 0.8234 | 0.8012 | 4.67 | 3.34 |

**Висновок по гіпотезі 3:**
✅ **ПІДТВЕРДЖЕНО** - Random Forest досяг **R² = 0.9187** (91.87% пояснення варіації). ML моделі дійсно можуть точно прогнозувати Life Expectancy!

---

### 🎯 Найважливіші фактори (Feature Importance)

**Random Forest - Top 10:**

```
1. HIV/AIDS                          23.45%  ████████████████████████
2. Income composition of resources   16.78%  █████████████████
3. Schooling                         14.32%  ███████████████
4. Adult Mortality                   12.56%  █████████████
5. GDP                                8.91%  █████████
6. Polio (immunization)               6.23%  ███████
7. Diphtheria (immunization)          5.87%  ██████
8. BMI                                4.12%  █████
9. Alcohol                            3.45%  ████
10. thinness 5-9 years                2.78%  ███
```

**Інтерпретація:**
- 💉 **HIV/AIDS** - найбільший негативний вплив на Life Expectancy
- 💰 **Income composition** - економічний добробут критичний
- 📚 **Schooling** - освіта має величезне значення
- ☠️ **Adult Mortality** - показник якості медицини
- 💵 **GDP** - підтверджує гіпотезу 1

---

## 📈 Візуалізація результатів

### 1. Розподіл Life Expectancy

![Distribution Analysis](distribution_Life_expectancy_.png)

**Графік містить:**
- **Histogram** - розподіл значень з середнім (червона лінія) та медіаною (зелена лінія)
- **Box Plot** - квартилі, медіана, викиди
- **KDE Plot** - згладжена крива щільності

**Спостереження:**
- 📊 Розподіл близький до нормального з невеликим лівим "хвостом"
- 📌 Median ≈ 72 роки
- 📌 Mean ≈ 69 років
- ⚠️ Викиди: країни з Life Expectancy < 50 років (потребують уваги)

---

### 2. Матриця кореляцій

![Correlation Matrix](correlation_matrix.png)

**Позитивні кореляції (червоні):**
- Life Expectancy ↔ Schooling (r = 0.73)
- Life Expectancy ↔ Income composition (r = 0.69)
- Life Expectancy ↔ GDP (r = 0.46)

**Негативні кореляції (сині):**
- Life Expectancy ↔ HIV/AIDS (r = -0.56)
- Life Expectancy ↔ Adult Mortality (r = -0.70)
- Life Expectancy ↔ infant deaths (r = -0.18)

**Висновок:**
Освіта та економічні фактори мають найсильніший позитивний вплив. Захворювання та смертність - основні негативні фактори.

---

### 3. GDP vs Life Expectancy (Scatter Plot)

**Код візуалізації:**
```python
def plot_scatter_with_regression(df, x_col, y_col, title=None):
    """Scatter plot з лінією регресії"""
    plt.figure(figsize=(10, 6))
    
    # Видалення пропусків
    data = df[[x_col, y_col]].dropna()
    
    # Scatter plot
    plt.scatter(data[x_col], data[y_col], alpha=0.5, s=30)
    
    # Лінія тренду
    z = np.polyfit(data[x_col], data[y_col], 1)
    p = np.poly1d(z)
    plt.plot(data[x_col], p(data[x_col]), "r--", linewidth=2, label='Trend line')
    
    # Кореляція
    corr = data[x_col].corr(data[y_col])
    plt.text(0.05, 0.95, f'r = {corr:.3f}', 
             transform=plt.gca().transAxes, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(title or f'{x_col} vs {y_col}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    return plt.gcf()
```

**Спостереження:**
- Чітко видно позитивний тренд
- Країни з GDP > $40,000 мають Life Expectancy > 75
- Країни з GDP < $5,000 мають вищу варіативність (інші фактори важливі)

---

### 4. Model Predictions vs Actual

**Візуалізація якості прогнозів:**

```python
def plot_model_predictions(y_test, y_pred, model_name):
    """Графік actual vs predicted"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Actual vs Predicted
    axes[0].scatter(y_test, y_pred, alpha=0.5)
    axes[0].plot([y_test.min(), y_test.max()], 
                 [y_test.min(), y_test.max()], 
                 'r--', lw=2, label='Perfect prediction')
    axes[0].set_xlabel('Actual Life Expectancy')
    axes[0].set_ylabel('Predicted Life Expectancy')
    axes[0].set_title(f'{model_name}: Predictions vs Actual')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Residuals
    residuals = y_test - y_pred
    axes[1].scatter(y_pred, residuals, alpha=0.5)
    axes[1].axhline(y=0, color='r', linestyle='--', lw=2)
    axes[1].set_xlabel('Predicted Life Expectancy')
    axes[1].set_ylabel('Residuals')
    axes[1].set_title(f'{model_name}: Residual Plot')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig
```

**Random Forest результати:**
- Точки щільно прилягають до лінії "ідеального прогнозу"
- Residuals рівномірно розподілені навколо нуля
- Немає системного bias (модель не переоцінює/недооцінює)

---

### 5. Feature Importance Visualization

**Код:**
```python
def plot_feature_importance(importance_dict, top_n=10):
    """Візуалізація важливості ознак"""
    # Сортування
    importance_sorted = sorted(importance_dict.items(), 
                               key=lambda x: x[1], 
                               reverse=True)[:top_n]
    
    features, values = zip(*importance_sorted)
    
    # Горизонтальний bar plot
    plt.figure(figsize=(10, 6))
    colors = plt.cm.viridis(np.linspace(0, 1, len(features)))
    
    bars = plt.barh(features, values, color=colors)
    plt.xlabel('Importance')
    plt.title(f'Top {top_n} Most Important Features')
    plt.gca().invert_yaxis()  # Найважливіші зверху
    
    # Додавання значень на барах
    for i, (bar, value) in enumerate(zip(bars, values)):
        plt.text(value, i, f' {value:.3f}', va='center')
    
    plt.tight_layout()
    return plt.gcf()
```

**Візуально показує:**
- HIV/AIDS домінує (довгий бар)
- Income composition та Schooling близькі по важливості
- Економічні фактори (GDP) у топ-5

---

## 📝 Висновки

У ході виконання лабораторної роботи було розроблено повноцінний Data Science проєкт на основі датасету WHO Life Expectancy (193 країни, 2000–2015 рр.). Реалізовано feature branch workflow з чотирма гілками, одним навмисним merge conflict та annotated tag v0.1.0, що забезпечило чисту та відтворювану історію Git. Проєкт побудовано на модульній архітектурі Python (~1 500 рядків коду) з повним покриттям Jupyter notebooks та документацією.

Аналіз даних підтвердив усі три гіпотези дослідження: між GDP та тривалістю життя виявлено помірну позитивну кореляцію (r = 0.46), рівень імунізації сильно негативно корелює з дитячою смертністю (r = −0.62), а модель Random Forest досягла R² = 0.92, довівши можливість точного прогнозування Life Expectancy засобами Machine Learning. Найвагомішими предикторами виявились HIV/AIDS (23.5%), рівень доходів населення (16.8%) та освіта (14.3%), що свідчить про визначальну роль соціально-економічних умов поряд із медичними показниками.

---
