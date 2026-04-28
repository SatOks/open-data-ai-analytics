# Open Data AI Analytics

Проєкт для аналізу відкритих даних з використанням методів штучного інтелекту та машинного навчання.

## Про проєкт

Цей проєкт створено для комплексного аналізу даних WHO про тривалість життя. Використовуючи методи машинного навчання та статистичного аналізу, ми досліджуємо ключові фактори впливу на здоров'я населення та будуємо предиктивні моделі.

**Модулі проєкту:**
- 📥 **data_load** - завантаження та первинна обробка даних
- 🔍 **data_quality_analysis** - перевірка якості та цілісності даних
- 🔬 **data_research** - статистичний аналіз та ML моделювання
- 📊 **visualization** - візуалізація результатів дослідження

## Джерело даних

**Dataset:** Life Expectancy (WHO)  
**Посилання:** https://www.kaggle.com/datasets/kumarajarshi/life-expectancy-who/data

Датасет містить дані Всесвітньої організації охорони здоров'я про очікувану тривалість життя та різноманітні фактори здоров'я для 193 країн за період 2000-2015 років. Включає такі показники як:
- Очікувана тривалість життя
- Смертність дорослих та дітей
- Витрати на охорону здоров'я
- Рівень імунізації
- ВВП та освіта
- Поширеність захворювань (ВІЛ/СНІД, поліомієліт тощо)

## Дослідницькі питання та гіпотези

### 1. Вплив економічного розвитку на тривалість життя
**Питання:** Чи існує кореляція між ВВП країни та очікуваною тривалістю життя населення?  
**Гіпотеза:** Країни з вищим ВВП на душу населення мають вищу очікувану тривалість життя через кращий доступ до медичних послуг та якості життя.

### 2. Ефективність імунізації населення
**Питання:** Як рівень імунізації (проти поліомієліту, дифтерії, гепатиту B) впливає на смертність дітей віком до 5 років?  
**Гіпотеза:** Високий рівень імунізації населення значно знижує дитячу смертність та підвищує загальну тривалість життя.

### 3. Прогнозування тривалості життя на основі багатофакторного аналізу
**Питання:** Чи можна створити точну модель машинного навчання для прогнозування очікуваної тривалості життя на основі економічних та медичних показників?  
**Гіпотеза:** Комбінація факторів (ВВП, рівень освіти, витрати на охорону здоров'я, алкоголь, ІМТ) дозволить створити регресійну модель з високою точністю прогнозування.

## Структура проєкту

```
open-data-ai-analytics/
├── labs/               # Матеріали до лабораторних
│   └── tasks/          # Вихідні умови Lab1/Lab2
├── data/               # Дані для аналізу
├── notebooks/          # Jupyter notebooks для експериментів
├── src/                # Вихідний код модулів
├── reports/            # Звіти та візуалізації
│   ├── labs/           # Звіти до лабораторних робіт
│   └── figures/        # Графіки та зображення
├── README.md           # Опис проєкту
└── .gitignore          # Файли для ігнорування Git
```

## Лабораторні звіти

- Лабораторна 1: `reports/labs/REPORT_LAB1_VISUAL.md`
- Лабораторна 2: `reports/labs/REPORT_LAB2.md`
- Лабораторна 3: `reports/labs/REPORT_LAB3.md`

## Lab 3: Docker Workspace

У межах третьої лабораторної проєкт контейнеризовано на окремі сервіси:

- `data_load` - читає CSV та завантажує дані у SQLite.
- `data_quality_analysis` - виконує перевірки якості та формує `quality_report.json`.
- `data_research` - виконує дослідження та формує `research_report.json`.
- `visualization` - генерує графіки у PNG.
- `web` - Flask-інтерфейс для перегляду результатів у браузері.

### Контейнерна структура

- `compose.yaml` - оркестрація всіх сервісів.
- `services/*/Dockerfile` - окремий Dockerfile для кожного сервісу.
- `runtime/db/life_expectancy.db` - SQLite база даних.
- `runtime/results/*.json` - результати аналізу та дослідження.
- `runtime/results/figures/*.png` - згенеровані візуалізації.

### Швидкий запуск

1. Переконайтесь, що CSV доступний за шляхом `data/raw/Life Expectancy Data.csv`.
2. За потреби створіть `.env` на основі `.env.example`.
3. Запустіть стек:

```bash
docker compose up --build
```

4. Відкрийте веб-інтерфейс: `http://localhost:8080`.

### Порти та мережа

- Веб-сервіс: `8080` (налаштовується через `WEB_PORT`).
- Docker network: `analytics-network`.

### Корисні команди

```bash
docker compose ps
docker compose logs -f web
docker compose down
```

## Lab 4: Azure Deployment (Infrastructure as Code)

У межах четвертої лабораторної проєкт розгортається у хмарі Microsoft Azure за допомогою Azure CLI та cloud-init.

### Архітектура

- **Azure Resource Group** - логічна група всіх ресурсів
- **Azure Virtual Network** - віртуальна мережа з підмережею
- **Azure Network Security Group** - правила фаєрволу (SSH, Web, Grafana, Prometheus)
- **Azure Public IP** - статична публічна IP-адреса
- **Azure Linux VM** - Ubuntu 22.04 LTS з Docker

### Компоненти

```
infra/
├── cloud-init.yaml       # Автоматична конфігурація VM
├── azure-deploy.ps1      # PowerShell скрипт розгортання
├── azure-destroy.ps1     # PowerShell скрипт видалення
├── azure-deploy.sh       # Bash скрипт розгортання
└── azure-destroy.sh      # Bash скрипт видалення
```

### Швидкий старт (Azure CLI)

1. Увійдіть у Azure:
   ```powershell
   az login
   ```

2. Запустіть скрипт розгортання:
   ```powershell
   cd infra
   .\azure-deploy.ps1 -ResourceGroup "odaa-rg" -Location "eastus"
   ```

3. Зачекайте 5-10 хвилин, поки cloud-init налаштує VM.

4. Перевірте доступність:
   ```powershell
   curl http://<PUBLIC_IP>:8080/health
   ```

### Відкриті порти

| Порт | Сервіс |
|------|--------|
| 22   | SSH |
| 8080 | Web Application |
| 3000 | Grafana |
| 9090 | Prometheus |

### Видалення ресурсів

```powershell
cd infra
.\azure-destroy.ps1 -ResourceGroup "odaa-rg"
```

## Lab 5: Monitoring (Prometheus + Grafana)

У межах п'ятої лабораторної додано стек моніторингу для спостереження за станом системи.

### Компоненти моніторингу

- **Prometheus** - збір та зберігання метрик
- **Grafana** - візуалізація та дашборди
- **Node Exporter** - метрики Linux VM (CPU, RAM, диск)
- **cAdvisor** - метрики Docker контейнерів

### Структура моніторингу

```
monitoring/
├── prometheus/
│   └── prometheus.yml              # Конфігурація Prometheus
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml      # Автоконфіг Prometheus datasource
│       └── dashboards/
│           ├── dashboards.yml      # Провізіонінг дашбордів
│           └── odaa-dashboard.json # Готовий дашборд
└── docker-compose.monitoring.yml   # Сервіси моніторингу
```

### Локальний запуск моніторингу

1. Спочатку запустіть основний стек:
   ```bash
   docker compose up -d --build
   ```

2. Потім запустіть моніторинг:
   ```bash
   docker compose -f monitoring/docker-compose.monitoring.yml up -d
   ```

### Доступ до сервісів

| Сервіс | URL | Логін |
|--------|-----|-------|
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | - |

### Метрики

Prometheus збирає метрики з:
- **prometheus** - самомоніторинг
- **node-exporter** - CPU, RAM, диск, мережа VM
- **cadvisor** - CPU, RAM контейнерів
- **web-app** - метрики застосунку (`/metrics`)

### Дашборд

Готовий дашборд "Open Data AI Analytics Dashboard" включає:
- 📈 CPU Usage (VM)
- 💾 Memory Usage (VM)
- 📊 Running Containers Count
- 🟢 Web Service Status
- ⏱️ VM Uptime
- 💿 Disk Usage
- 🐳 Container Memory/CPU (per service)

### Корисні PromQL запити

```promql
# CPU Usage (%)
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory Usage (%)
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Running Containers
count(container_memory_usage_bytes{name!=""})
```
