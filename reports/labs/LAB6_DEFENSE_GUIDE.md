# 🎓 Лабораторна робота №6 — Повний гайд для захисту

## Тема: Моніторинг за допомогою Prometheus та Grafana

---

# 📚 ЧАСТИНА 1: ТЕОРЕТИЧНІ ОСНОВИ

## 1.1. Що таке моніторинг і навіщо він потрібен?

**Моніторинг** — це безперервне спостереження за системою на основі її показників для виявлення проблем та аналізу продуктивності.

### Що моніторимо:

```
┌─────────────────────────────────────────────────────────────┐
│              ЩО МОНІТОРИМО В DEVOPS                         │
├─────────────────────────────────────────────────────────────┤
│  ІНФРАСТРУКТУРА        │  ЗАСТОСУНОК           │  БІЗНЕС   │
│  ─────────────────     │  ─────────────────    │  ─────── │
│  • CPU usage           │  • Response time      │  • Users  │
│  • Memory usage        │  • Error rate         │  • Orders │
│  • Disk I/O            │  • Request count      │  • Revenue│
│  • Network traffic     │  • Queue depth        │  • SLA    │
│  • Container health    │  • DB connections     │           │
└─────────────────────────────────────────────────────────────┘
```

### Чому це важливо:

| Без моніторингу | З моніторингом |
|-----------------|----------------|
| Дізнаємося про проблему від користувачів | Алерт приходить за секунди |
| Не знаємо причину збою | Бачимо метрики до і після |
| Не можемо планувати масштабування | Тренди показують майбутні потреби |
| Post-mortem без даних | Детальна історія для аналізу |

---

## 1.2. Три рівні моніторингу в цій роботі

### Рівень 1: Стан VM (Node Exporter)

```
┌─────────────────────────────────────────┐
│          NODE EXPORTER                   │
│          (Linux метрики)                 │
├─────────────────────────────────────────┤
│  CPU:     node_cpu_seconds_total        │
│  RAM:     node_memory_MemAvailable_bytes│
│  Disk:    node_filesystem_avail_bytes   │
│  Network: node_network_receive_bytes    │
│  Uptime:  node_boot_time_seconds        │
└─────────────────────────────────────────┘
```

### Рівень 2: Стан контейнерів (cAdvisor)

```
┌─────────────────────────────────────────┐
│            CADVISOR                      │
│       (Container метрики)                │
├─────────────────────────────────────────┤
│  CPU:     container_cpu_usage_seconds   │
│  RAM:     container_memory_usage_bytes  │
│  Network: container_network_receive_bytes│
│  Labels:  name, image, id               │
└─────────────────────────────────────────┘
```

### Рівень 3: Стан застосунку (Custom /metrics)

```
┌─────────────────────────────────────────┐
│         APPLICATION METRICS              │
│         (Custom endpoint)                │
├─────────────────────────────────────────┤
│  web_app_up:              1 (gauge)     │
│  web_database_available:  1 (gauge)     │
│  web_figures_count:       8 (gauge)     │
│  web_reports_available:   1 (gauge)     │
└─────────────────────────────────────────┘
```

---

## 1.3. Prometheus — Система моніторингу

### Ключові концепції:

| Концепція | Опис |
|-----------|------|
| **Pull model** | Prometheus сам забирає метрики з targets |
| **Time series** | Дані зберігаються як часові ряди |
| **Labels** | Мітки для фільтрації та групування |
| **PromQL** | Мова запитів для аналізу метрик |
| **Scrape** | Процес збору метрик (кожні N секунд) |
| **Target** | Endpoint, з якого збираються метрики |

### Конфігурація prometheus.yml:

```yaml
# Глобальні налаштування
global:
  scrape_interval: 15s      # Як часто збирати
  evaluation_interval: 15s  # Як часто перевіряти правила

# Scrape jobs — звідки брати метрики
scrape_configs:
  - job_name: 'prometheus'      # Ім'я job'а
    static_configs:
      - targets: ['localhost:9090']  # Список targets
      
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
      
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
      
  - job_name: 'web-app'
    scrape_interval: 30s    # Можна перевизначити
    metrics_path: /metrics  # Шлях до метрик
    static_configs:
      - targets: ['web:8080']
```

### Типи метрик:

| Тип | Опис | Приклад |
|-----|------|---------|
| **Counter** | Тільки зростає | `http_requests_total` |
| **Gauge** | Зростає і зменшується | `temperature_celsius` |
| **Histogram** | Розподіл по бакетам | `request_duration_bucket` |
| **Summary** | Квантилі | `request_duration{quantile="0.99"}` |

---

## 1.4. PromQL — Мова запитів

### Базовий синтаксис:

```promql
# Проста метрика
up

# Фільтрація по label
up{job="prometheus"}

# Регулярний вираз
http_requests_total{method=~"GET|POST"}

# Діапазон часу
http_requests_total[5m]
```

### Основні функції:

| Функція | Призначення | Приклад |
|---------|-------------|---------|
| `rate()` | Швидкість counter/сек | `rate(http_requests_total[5m])` |
| `sum()` | Сума значень | `sum(up)` |
| `avg()` | Середнє | `avg(node_cpu_seconds_total)` |
| `count()` | Кількість серій | `count(up == 1)` |
| `max()/min()` | Екстремуми | `max(container_memory_usage_bytes)` |

### Корисні запити для цієї роботи:

```promql
# CPU usage %
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage %
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage %
(1 - (node_filesystem_avail_bytes{mountpoint="/"} / 
      node_filesystem_size_bytes{mountpoint="/"})) * 100

# VM Uptime (seconds)
node_time_seconds - node_boot_time_seconds

# Active services count
count(up == 1)

# Web app status
up{job="web-app"}
```

---

## 1.5. Grafana — Візуалізація

### Компоненти:

| Компонент | Призначення |
|-----------|-------------|
| **Data Source** | Підключення до Prometheus |
| **Dashboard** | Набір панелей |
| **Panel** | Окрема візуалізація |
| **Query** | PromQL запит для панелі |
| **Provisioning** | Автоматична конфігурація |

### Типи панелей:

| Тип | Використання |
|-----|--------------|
| Time series | Графіки з часом (CPU, Memory) |
| Stat | Одне число (Uptime, Status) |
| Gauge | Спідометр з порогами (Disk %) |
| Bar gauge | Горизонтальні барі |
| Table | Табличні дані |

### Provisioning Data Source:

```yaml
# grafana/provisioning/datasources/prometheus.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

---

## 1.6. Docker Compose для моніторингу

```yaml
# monitoring/docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus:v2.45.0
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=15d'

  grafana:
    image: grafana/grafana:10.0.0
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

  node-exporter:
    image: prom/node-exporter:v1.6.0
    container_name: node-exporter
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.49.1
    container_name: cadvisor
    privileged: true
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker:/var/lib/docker:ro

volumes:
  prometheus_data:
  grafana_data:
```

---

# 📚 ЧАСТИНА 2: ПРАКТИЧНА РЕАЛІЗАЦІЯ

## 2.1. Архітектура моніторингу

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AZURE VM (104.46.15.0)                            │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      DOCKER ENGINE                              │ │
│  │                                                                  │ │
│  │  ┌──────────────┐         ┌──────────────────────────────────┐ │ │
│  │  │  APP STACK   │         │       MONITORING STACK            │ │ │
│  │  │              │         │                                    │ │ │
│  │  │  data_load   │         │  PROMETHEUS (:9090)               │ │ │
│  │  │  data_quality│◀────────│    │                              │ │ │
│  │  │  data_research        │    │ scrape every 15s             │ │ │
│  │  │  visualization│        │    ▼                              │ │ │
│  │  │  WEB (:8080) │────────▶│  NODE-EXPORTER (:9100)           │ │ │
│  │  │   /metrics   │         │    • CPU, RAM, Disk               │ │ │
│  │  └──────────────┘         │                                    │ │ │
│  │                           │  CADVISOR (:8080)                  │ │ │
│  │                           │    • Container metrics             │ │ │
│  │                           │                                    │ │ │
│  │                           │  GRAFANA (:3000)                   │ │ │
│  │                           │    • Dashboards                    │ │ │
│  │                           │    • Prometheus data source        │ │ │
│  │                           └──────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ :8080, :9090, :3000
                              ▼
                     ┌─────────────────┐
                     │  USER BROWSER   │
                     └─────────────────┘
```

## 2.2. Файлова структура

```
monitoring/
├── prometheus/
│   └── prometheus.yml           # Scrape configuration
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml   # Auto-add Prometheus
│       └── dashboards/
│           ├── dashboards.yml   # Dashboard provider
│           └── odaa-dashboard.json  # Custom dashboard
└── docker-compose.monitoring.yml    # Services definition
```

## 2.3. Статус системи (поточний)

| Сервіс | Container | Port | Health |
|--------|-----------|------|--------|
| Prometheus | prometheus | 9090 | 🟢 UP |
| Grafana | grafana | 3000 | 🟢 OK |
| Node Exporter | node-exporter | 9100 | 🟢 UP |
| cAdvisor | cadvisor | 8080 | 🟢 Healthy |
| Web App | app-web-1 | 8080 | 🟢 Healthy |

---

# 📚 ЧАСТИНА 3: ПИТАННЯ ДЛЯ ЗАХИСТУ

## 🔴 Базові питання (обов'язково знати)

### 1. Що таке моніторинг і навіщо він потрібен?
**Відповідь:** Моніторинг — це безперервне спостереження за системою на основі метрик (CPU, RAM, disk, response time). Потрібен для виявлення проблем до того, як вони стануть критичними, аналізу продуктивності та планування масштабування.

### 2. Що таке Prometheus і як він працює?
**Відповідь:** Prometheus — це система моніторингу з pull-моделлю. Він сам забирає (scrape) метрики з targets через HTTP кожні N секунд. Зберігає дані як time series. Використовує PromQL для запитів.

### 3. Що таке scrape_config в Prometheus?
**Відповідь:** scrape_config — це секція в prometheus.yml, де описуються jobs та targets для збору метрик. Кожен job має ім'я, список targets і може мати свій scrape_interval.

### 4. Які джерела метрик використані в роботі?
**Відповідь:**
- **prometheus** — метрики самого Prometheus
- **node-exporter** — метрики Linux VM (CPU, RAM, disk)
- **cadvisor** — метрики Docker контейнерів
- **web-app** — custom метрики застосунку через /metrics

### 5. Що таке Grafana і для чого вона використовується?
**Відповідь:** Grafana — це платформа візуалізації метрик. Підключається до Prometheus як data source. Дозволяє створювати dashboards з графіками, gauge, статистикою. Використовується для побудови дашбордів у цій роботі.

## 🟡 Середні питання

### 6. Що показує метрика `up` в Prometheus?
**Відповідь:** Метрика `up` показує статус target:
- `up{job="prometheus"} = 1` — target доступний, scrape успішний
- `up{job="prometheus"} = 0` — target недоступний
Це базова health check метрика.

### 7. Як написати PromQL запит для CPU usage?
**Відповідь:**
```promql
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```
Пояснення: беремо rate idle CPU за 5 хвилин, віднімаємо від 100% щоб отримати використання.

### 8. Що таке Node Exporter і які метрики він надає?
**Відповідь:** Node Exporter — це exporter для Linux/Unix метрик. Надає:
- CPU: `node_cpu_seconds_total`
- RAM: `node_memory_MemAvailable_bytes`
- Disk: `node_filesystem_avail_bytes`
- Network: `node_network_receive_bytes_total`
Монтує /proc, /sys для доступу до системних даних.

### 9. Що таке cAdvisor?
**Відповідь:** cAdvisor (Container Advisor) — це exporter від Google для метрик Docker контейнерів. Показує CPU, RAM, network для кожного контейнера окремо. Потребує доступу до Docker socket.

### 10. Як додати власні метрики до застосунку?
**Відповідь:**
1. Створити endpoint `/metrics` у застосунку
2. Виводити метрики у форматі Prometheus:
```
# HELP metric_name Description
# TYPE metric_name gauge
metric_name 123
```
3. Додати scrape job в prometheus.yml
4. Перевірити в Prometheus targets

## 🟢 Складні питання

### 11. Яка різниця між Counter та Gauge?
**Відповідь:**
- **Counter** — тільки зростає (http_requests_total). Скидається при перезапуску. Використовуємо rate() для обчислення швидкості.
- **Gauge** — зростає і зменшується (temperature, memory). Можна використовувати напряму без функцій.

### 12. Що таке Grafana Provisioning?
**Відповідь:** Provisioning — це автоматична конфігурація Grafana через YAML файли при старті. Дозволяє:
- Додати data sources (datasources/*.yml)
- Імпортувати dashboards (dashboards/*.yml + JSON)
Файли монтуються в `/etc/grafana/provisioning/`

### 13. Як працює функція rate() в PromQL?
**Відповідь:** `rate()` обчислює середню швидкість зміни counter за секунду:
- Бере значення за вказаний range (наприклад [5m])
- Обчислює різницю першого і останнього значення
- Ділить на кількість секунд
- Результат: events per second

### 14. Чому потрібен privileged режим для cAdvisor?
**Відповідь:** cAdvisor потребує privileged для:
- Доступу до /dev/kmsg
- Читання cgroups
- Доступу до Docker socket
Без privileged він не зможе отримати всі метрики контейнерів.

### 15. Як реалізувати alerting у цій системі?
**Відповідь:** Два шляхи:
1. **Prometheus Alertmanager** — alert rules в prometheus.yml, окремий сервіс для notifications
2. **Grafana Alerting** — правила на панелях dashboard, канали (Email, Slack)

---

# 📚 ЧАСТИНА 4: ДЕМОНСТРАЦІЯ НА ЗАХИСТІ

## Чек-лист демонстрації:

### 1. Показати запущені контейнери (2 хв)

```bash
ssh azureuser@104.46.15.0 "docker ps --format 'table {{.Names}}\t{{.Status}}'"
```

Очікуваний результат:
```
NAMES           STATUS
cadvisor        Up 2 weeks (healthy)
grafana         Up 2 weeks
prometheus      Up 2 weeks
node-exporter   Up 2 weeks
app-web-1       Up 2 weeks (healthy)
```

### 2. Prometheus Targets (3 хв)

1. Відкрити http://104.46.15.0:9090
2. Перейти Status → Targets
3. Показати всі 4 targets зелені (UP):
   - prometheus
   - node-exporter
   - cadvisor
   - web-app

### 3. Prometheus Graph (3 хв)

Виконати запити:
```promql
# Всі targets UP
up

# CPU usage
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

### 4. Grafana Dashboard (5 хв)

1. Відкрити http://104.46.15.0:3000
2. Увійти: admin / admin
3. Перейти Dashboards → Open Data AI Analytics Dashboard
4. Показати панелі:
   - VM CPU Usage (%) — графік
   - VM Memory Usage (%) — графік
   - Active Services — число (4)
   - VM Uptime — час
   - Disk Usage — gauge (17%)

### 5. Grafana Data Source (2 хв)

1. Administration → Data sources
2. Показати Prometheus data source
3. Натиснути "Test" — повинно бути зелене

### 6. Application Metrics (2 хв)

```bash
curl http://104.46.15.0:8080/metrics
```

Показати custom метрики:
```
web_app_up 1
web_database_available 1
web_figures_count 8
```

### 7. Файли конфігурації (3 хв)

Показати у VS Code:
- `monitoring/prometheus/prometheus.yml`
- `monitoring/docker-compose.monitoring.yml`
- `monitoring/grafana/provisioning/datasources/prometheus.yml`

---

# 📚 ЧАСТИНА 5: ГЛОСАРІЙ

| Термін | Визначення |
|--------|------------|
| **Prometheus** | Time-series DB для метрик з pull-моделлю |
| **Grafana** | Платформа візуалізації метрик |
| **PromQL** | Мова запитів Prometheus |
| **Scrape** | Процес збору метрик з target |
| **Target** | Endpoint для збору метрик |
| **Job** | Логічна група targets в Prometheus |
| **Exporter** | Компонент, що експортує метрики |
| **Node Exporter** | Exporter для Linux метрик |
| **cAdvisor** | Exporter для Docker контейнерів |
| **Counter** | Метрика, що тільки зростає |
| **Gauge** | Метрика, що може зростати і зменшуватися |
| **Label** | Мітка для фільтрації метрик |
| **Time Series** | Послідовність значень з часовими мітками |
| **Dashboard** | Набір панелей візуалізації |
| **Panel** | Окрема візуалізація на dashboard |
| **Provisioning** | Автоматична конфігурація через файли |
| **Data Source** | Джерело даних у Grafana |
| **rate()** | PromQL функція для швидкості counter |

---

# 📚 ЧАСТИНА 6: ШВИДКА ШПАРГАЛКА

## URLs для перевірки:

| Сервіс | URL |
|--------|-----|
| Web App | http://104.46.15.0:8080 |
| App Metrics | http://104.46.15.0:8080/metrics |
| Prometheus | http://104.46.15.0:9090 |
| Prometheus Targets | http://104.46.15.0:9090/targets |
| Grafana | http://104.46.15.0:3000 (admin/admin) |

## Ключові PromQL запити:

```promql
up                                    # Статус targets
count(up == 1)                        # Кількість UP
node_memory_MemTotal_bytes            # Total RAM
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)  # CPU %
```

## Ключові файли:

```
monitoring/prometheus/prometheus.yml  # Scrape config
monitoring/docker-compose.monitoring.yml  # Services
monitoring/grafana/provisioning/...   # Auto-config
services/web/app.py                   # /metrics endpoint
```

---

**Дата створення:** 12 травня 2026
**Автор:** GitHub Copilot для Лабораторної роботи №6
