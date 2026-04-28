# 🎓 Лабораторна робота №5 — Повний гайд для захисту

## Тема: Моніторинг за допомогою Prometheus та Grafana

---

# 📚 ЧАСТИНА 1: ТЕОРЕТИЧНІ ОСНОВИ

## 1.1. Що таке моніторинг і навіщо він потрібен?

**Моніторинг** — це безперервне спостереження за системою на основі метрик для виявлення проблем, аналізу продуктивності та планування масштабування.

### Три стовпи Observability:

```
┌─────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY                             │
├───────────────────┬───────────────────┬─────────────────────┤
│      METRICS      │      LOGS         │      TRACES         │
│                   │                   │                     │
│  Числові значення │  Текстові записи  │  Шлях запиту через  │
│  з часовими       │  подій у системі  │  розподілену        │
│  мітками          │                   │  систему            │
│                   │                   │                     │
│  Prometheus       │  ELK Stack        │  Jaeger             │
│  Grafana          │  Loki             │  Zipkin             │
│  InfluxDB         │  Fluentd          │  OpenTelemetry      │
└───────────────────┴───────────────────┴─────────────────────┘
```

### Чому моніторинг критичний для DevOps:

| Проблема | Як моніторинг допомагає |
|----------|-------------------------|
| Сервіс впав | Алерт приходить за секунди, а не коли клієнти скаржаться |
| Повільна відповідь | Графіки показують деградацію до того як стане критично |
| Закінчується диск | Прогнозування на основі трендів |
| Витік пам'яті | Видно зростаючий графік RAM |
| DDoS атака | Аномальний ріст запитів |

### Типи метрик:

```
┌─────────────────────────────────────────────────────────────┐
│                    ТИПИ МЕТРИК                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  COUNTER (Лічильник)                                        │
│  ─────────────────                                          │
│  • Тільки зростає (монотонно)                               │
│  • Приклад: http_requests_total = 42567                     │
│  • Використання: rate() для обчислення швидкості            │
│                                                              │
│  GAUGE (Показник)                                           │
│  ───────────────                                            │
│  • Може зростати і зменшуватися                             │
│  • Приклад: temperature_celsius = 23.5                      │
│  • Приклад: memory_usage_bytes = 1073741824                 │
│                                                              │
│  HISTOGRAM (Гістограма)                                     │
│  ─────────────────────                                      │
│  • Розподіл значень по бакетам (buckets)                    │
│  • Приклад: http_request_duration_seconds_bucket{le="0.5"}  │
│  • Використання: histogram_quantile() для перцентилів       │
│                                                              │
│  SUMMARY (Підсумок)                                         │
│  ─────────────────                                          │
│  • Заздалегідь обчислені квантилі                           │
│  • Приклад: http_request_duration_seconds{quantile="0.99"}  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 1.2. Prometheus — Система моніторингу

### Що таке Prometheus?

**Prometheus** — це open-source система моніторингу та alerting, створена в SoundCloud. Зараз є проєктом CNCF (Cloud Native Computing Foundation), як і Kubernetes.

### Ключові особливості Prometheus:

| Особливість | Опис |
|-------------|------|
| **Pull-based** | Prometheus сам "витягує" метрики з targets |
| **Time-series DB** | Зберігає дані як часові ряди |
| **PromQL** | Потужна мова запитів |
| **Service Discovery** | Автоматичне знаходження targets |
| **Alertmanager** | Окремий компонент для алертів |
| **Без залежностей** | Один бінарний файл, Go |

### Архітектура Prometheus:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PROMETHEUS ARCHITECTURE                          │
│                                                                      │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐ │
│  │  Target 1    │     │  Target 2    │     │  Target 3            │ │
│  │ node-exporter│     │  cadvisor    │     │  your-app /metrics   │ │
│  │   :9100      │     │   :8080      │     │      :8080           │ │
│  └──────┬───────┘     └──────┬───────┘     └──────────┬───────────┘ │
│         │                    │                        │              │
│         │    HTTP GET /metrics (pull)                 │              │
│         │                    │                        │              │
│         ▼                    ▼                        ▼              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    PROMETHEUS SERVER                           │ │
│  │  ┌─────────────┐  ┌─────────────────┐  ┌────────────────────┐ │ │
│  │  │  Retrieval  │  │  Time-series DB │  │    HTTP Server     │ │ │
│  │  │  (Scraper)  │─▶│    (TSDB)       │◀─│    (API + UI)      │ │ │
│  │  └─────────────┘  └─────────────────┘  └────────────────────┘ │ │
│  │                           │                       ▲            │ │
│  │                           ▼                       │            │ │
│  │                   ┌─────────────┐         ┌──────┴──────┐     │ │
│  │                   │  Rules      │         │  PromQL     │     │ │
│  │                   │  (Alerting) │         │  Queries    │     │ │
│  │                   └──────┬──────┘         └─────────────┘     │ │
│  └──────────────────────────┼─────────────────────────────────────┘ │
│                              │                                       │
│                              ▼                                       │
│                    ┌─────────────────┐       ┌─────────────────────┐│
│                    │  Alertmanager   │       │      GRAFANA        ││
│                    │  (Notifications)│       │   (Visualization)   ││
│                    └─────────────────┘       └─────────────────────┘│
│                              │                                       │
│                              ▼                                       │
│                    ┌─────────────────┐                              │
│                    │  Email/Slack/   │                              │
│                    │  PagerDuty      │                              │
│                    └─────────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
```

### Конфігурація Prometheus (prometheus.yml):

```yaml
# Глобальні налаштування
global:
  scrape_interval: 15s      # Як часто збирати метрики
  evaluation_interval: 15s  # Як часто перевіряти правила
  scrape_timeout: 10s       # Таймаут для scrape

# Конфігурація scrape jobs
scrape_configs:
  # Моніторинг самого Prometheus
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
    
  # Метрики Linux сервера
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    
  # Метрики Docker контейнерів
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
    
  # Метрики застосунку
  - job_name: 'web-app'
    scrape_interval: 30s  # Можна перевизначити
    static_configs:
      - targets: ['web:8080']
    metrics_path: /metrics  # За замовчуванням /metrics
```

### Labels (Мітки) в Prometheus:

```
# Метрика без міток
up = 1

# Метрика з мітками (labels)
http_requests_total{method="GET", endpoint="/api/users", status="200"} = 1524

# Мітки дозволяють:
# 1. Фільтрувати: http_requests_total{status="500"}
# 2. Групувати: sum by (method) (http_requests_total)
# 3. Агрегувати: sum(http_requests_total)
```

---

## 1.3. PromQL — Мова запитів Prometheus

### Базовий синтаксис:

```promql
# Проста метрика
up

# Фільтрація по мітці (exact match)
up{job="prometheus"}

# Регулярний вираз
http_requests_total{method=~"GET|POST"}

# Негативний фільтр
up{job!="prometheus"}

# Діапазон часу (range vector)
http_requests_total[5m]
```

### Функції PromQL:

| Функція | Опис | Приклад |
|---------|------|---------|
| `rate()` | Швидкість зміни counter за секунду | `rate(http_requests_total[5m])` |
| `irate()` | Миттєва швидкість (остання точка) | `irate(http_requests_total[5m])` |
| `increase()` | Абсолютне зростання counter | `increase(http_requests_total[1h])` |
| `sum()` | Сума всіх значень | `sum(up)` |
| `avg()` | Середнє значення | `avg(node_cpu_seconds_total)` |
| `max()` / `min()` | Максимум / Мінімум | `max(node_memory_MemTotal_bytes)` |
| `count()` | Кількість серій | `count(up == 1)` |
| `topk()` | Top K серій | `topk(5, http_requests_total)` |
| `histogram_quantile()` | Обчислення перцентилів | `histogram_quantile(0.95, rate(http_request_duration_bucket[5m]))` |

### Агрегація:

```promql
# Сума по всіх серіях
sum(http_requests_total)

# Сума, згрупована по method
sum by (method) (http_requests_total)

# Сума, виключаючи instance
sum without (instance) (http_requests_total)
```

### Корисні запити:

```promql
# === CPU ===
# Використання CPU у відсотках
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# === MEMORY ===
# Використання RAM у відсотках
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Використання RAM в GB
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / 1024^3

# === DISK ===
# Використання диска у відсотках
(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100

# === NETWORK ===
# Швидкість прийому даних (bytes/sec)
rate(node_network_receive_bytes_total[5m])

# === CONTAINERS ===
# Кількість запущених контейнерів
count(container_last_seen{name!=""})

# === UPTIME ===
# Час роботи сервера в секундах
node_time_seconds - node_boot_time_seconds

# === SERVICES ===
# Статус всіх targets
up
```

---

## 1.4. Exporters — Джерела метрик

### Що таке Exporter?

**Exporter** — це компонент, який збирає метрики з певної системи і надає їх у форматі Prometheus через HTTP endpoint `/metrics`.

### Основні Exporters:

```
┌─────────────────────────────────────────────────────────────┐
│                    PROMETHEUS EXPORTERS                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  NODE EXPORTER (Linux/Unix метрики)                         │
│  ─────────────────────────────────────                      │
│  • CPU, RAM, Disk, Network                                  │
│  • Порт: 9100                                               │
│  • Метрики: node_cpu_*, node_memory_*, node_filesystem_*    │
│                                                              │
│  CADVISOR (Container метрики)                               │
│  ───────────────────────────────                            │
│  • CPU, RAM, Network для кожного контейнера                 │
│  • Порт: 8080                                               │
│  • Метрики: container_cpu_*, container_memory_*             │
│                                                              │
│  MYSQLD EXPORTER (MySQL метрики)                            │
│  ─────────────────────────────────                          │
│  • Queries, Connections, InnoDB                             │
│  • Порт: 9104                                               │
│                                                              │
│  POSTGRES EXPORTER (PostgreSQL метрики)                     │
│  ──────────────────────────────────────                     │
│  • Connections, Transactions, Locks                         │
│  • Порт: 9187                                               │
│                                                              │
│  BLACKBOX EXPORTER (HTTP/TCP probes)                        │
│  ───────────────────────────────────                        │
│  • Перевірка доступності endpoints                          │
│  • Порт: 9115                                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Node Exporter — Детальніше:

```yaml
# Docker Compose конфігурація
node-exporter:
  image: prom/node-exporter:v1.6.0
  container_name: node-exporter
  command:
    - '--path.procfs=/host/proc'
    - '--path.rootfs=/rootfs'
    - '--path.sysfs=/host/sys'
  volumes:
    - /proc:/host/proc:ro
    - /sys:/host/sys:ro
    - /:/rootfs:ro
```

### cAdvisor — Container Advisor:

```yaml
# Docker Compose конфігурація
cadvisor:
  image: gcr.io/cadvisor/cadvisor:v0.49.1
  container_name: cadvisor
  privileged: true
  volumes:
    - /:/rootfs:ro
    - /var/run:/var/run:ro
    - /var/run/docker.sock:/var/run/docker.sock:ro
    - /sys:/sys:ro
    - /var/lib/docker:/var/lib/docker:ro
```

### Створення власних метрик у застосунку:

```python
# Flask додаток з метриками
from flask import Flask, Response
import time

app = Flask(__name__)

# Зберігаємо статистику
request_count = 0
start_time = time.time()

@app.route('/metrics')
def metrics():
    """Endpoint для Prometheus"""
    uptime = time.time() - start_time
    
    # Формат Prometheus
    metrics_text = f"""# HELP web_app_up Application status (1=up, 0=down)
# TYPE web_app_up gauge
web_app_up 1

# HELP web_app_requests_total Total HTTP requests
# TYPE web_app_requests_total counter
web_app_requests_total {request_count}

# HELP web_app_uptime_seconds Application uptime in seconds
# TYPE web_app_uptime_seconds gauge
web_app_uptime_seconds {uptime}
"""
    return Response(metrics_text, mimetype='text/plain')
```

---

## 1.5. Grafana — Візуалізація метрик

### Що таке Grafana?

**Grafana** — це open-source платформа для візуалізації, аналітики та моніторингу. Підтримує понад 50 data sources включаючи Prometheus, InfluxDB, Elasticsearch, MySQL.

### Компоненти Grafana:

```
┌─────────────────────────────────────────────────────────────┐
│                    GRAFANA COMPONENTS                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DATA SOURCES                                               │
│  ────────────                                               │
│  • Prometheus, InfluxDB, MySQL, PostgreSQL                  │
│  • Elasticsearch, Loki, CloudWatch                          │
│  • Конфігуруються в Administration → Data sources           │
│                                                              │
│  DASHBOARDS                                                 │
│  ──────────                                                 │
│  • Набір панелей (panels) для візуалізації                  │
│  • Можна імпортувати готові (grafana.com/dashboards)        │
│  • JSON формат для експорту/імпорту                         │
│                                                              │
│  PANELS                                                     │
│  ──────                                                     │
│  • Graph (time series)                                      │
│  • Stat (single value)                                      │
│  • Gauge (спідометр)                                        │
│  • Table                                                    │
│  • Heatmap, Bar chart, Pie chart                            │
│                                                              │
│  ALERTING                                                   │
│  ────────                                                   │
│  • Правила на основі запитів                                │
│  • Канали: Email, Slack, PagerDuty, Webhook                 │
│                                                              │
│  PROVISIONING                                               │
│  ────────────                                               │
│  • Автоматична конфігурація через YAML файли                │
│  • Data sources, Dashboards, Alert rules                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Provisioning — Автоматична конфігурація:

```
grafana/
├── provisioning/
│   ├── datasources/
│   │   └── prometheus.yml      # Data source конфігурація
│   └── dashboards/
│       ├── dashboards.yml      # Dashboard провайдер
│       └── my-dashboard.json   # JSON dashboard
```

### Provisioning Data Source (prometheus.yml):

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      httpMethod: POST
      prometheusType: Prometheus
      prometheusVersion: "2.45.0"
```

### Provisioning Dashboards (dashboards.yml):

```yaml
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /etc/grafana/provisioning/dashboards
```

### Типи панелей Grafana:

| Тип | Використання | Приклад |
|-----|--------------|---------|
| **Time series** | Графіки з часом | CPU usage over time |
| **Stat** | Одне велике число | Current memory % |
| **Gauge** | Спідометр з порогами | Disk usage |
| **Bar gauge** | Горизонтальні барі | Top 5 containers |
| **Table** | Табличні дані | All targets status |
| **Logs** | Логи (з Loki) | Application logs |
| **Heatmap** | Теплова карта | Request latency distribution |

---

# 📚 ЧАСТИНА 2: ПРАКТИЧНА РЕАЛІЗАЦІЯ

## 2.1. Архітектура моніторингу

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MONITORING ARCHITECTURE                           │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                       AZURE VM (Ubuntu 22.04)                       │ │
│  │                                                                      │ │
│  │  ┌─────────────────────┐        ┌─────────────────────────────────┐ │ │
│  │  │    APPLICATION      │        │         MONITORING STACK        │ │ │
│  │  │      STACK          │        │                                 │ │ │
│  │  │                     │        │  ┌─────────────────────────┐   │ │ │
│  │  │  ┌───────────────┐  │        │  │      PROMETHEUS         │   │ │ │
│  │  │  │   data_load   │  │        │  │      :9090              │   │ │ │
│  │  │  └───────────────┘  │        │  │                         │   │ │ │
│  │  │  ┌───────────────┐  │        │  │  • Scrapes every 15s    │   │ │ │
│  │  │  │ data_quality  │  │        │  │  • Stores 15 days       │   │ │ │
│  │  │  └───────────────┘  │◀──────▶│  │  • PromQL queries       │   │ │ │
│  │  │  ┌───────────────┐  │ scrape │  └───────────┬─────────────┘   │ │ │
│  │  │  │ data_research │  │        │              │                  │ │ │
│  │  │  └───────────────┘  │        │              │ query            │ │ │
│  │  │  ┌───────────────┐  │        │              ▼                  │ │ │
│  │  │  │ visualization │  │        │  ┌─────────────────────────┐   │ │ │
│  │  │  └───────────────┘  │        │  │       GRAFANA           │   │ │ │
│  │  │  ┌───────────────┐  │        │  │       :3000             │   │ │ │
│  │  │  │     WEB       │──┼────────┼─▶│                         │   │ │ │
│  │  │  │  :8080        │  │ /metrics │  │  • Dashboards          │   │ │ │
│  │  │  │  /metrics     │  │        │  │  • Alerting             │   │ │ │
│  │  │  └───────────────┘  │        │  │  • Provisioning         │   │ │ │
│  │  └─────────────────────┘        │  └─────────────────────────┘   │ │ │
│  │                                 │                                 │ │ │
│  │  ┌───────────────────────────┐  │  ┌─────────────────────────┐   │ │ │
│  │  │      NODE EXPORTER        │──┼─▶│                         │   │ │ │
│  │  │      :9100                │  │  │                         │   │ │ │
│  │  │  • CPU, RAM, Disk, Net    │  │  │                         │   │ │ │
│  │  └───────────────────────────┘  │  │                         │   │ │ │
│  │                                 │  │                         │   │ │ │
│  │  ┌───────────────────────────┐  │  │      PROMETHEUS         │   │ │ │
│  │  │        CADVISOR           │──┼─▶│      (continues         │   │ │ │
│  │  │        :8080              │  │  │       scraping)         │   │ │ │
│  │  │  • Container metrics      │  │  │                         │   │ │ │
│  │  └───────────────────────────┘  │  └─────────────────────────┘   │ │ │
│  │                                 │                                 │ │ │
│  └─────────────────────────────────┴─────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ :8080, :9090, :3000
                                      ▼
                             ┌─────────────────┐
                             │   USER BROWSER  │
                             └─────────────────┘
```

## 2.2. Docker Compose для моніторингу

### monitoring/docker-compose.monitoring.yml:

```yaml
services:
  prometheus:
    image: prom/prometheus:v2.45.0
    container_name: prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=15d'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks:
      - monitoring-network
      - app-network

  grafana:
    image: grafana/grafana:10.0.0
    container_name: grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
    ports:
      - "3000:3000"
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
      - grafana_data:/var/lib/grafana
    networks:
      - monitoring-network
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:v1.6.0
    container_name: node-exporter
    restart: unless-stopped
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    networks:
      - monitoring-network

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.49.1
    container_name: cadvisor
    restart: unless-stopped
    privileged: true
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /sys:/sys:ro
      - /var/lib/docker:/var/lib/docker:ro
    networks:
      - monitoring-network

networks:
  monitoring-network:
    driver: bridge
  app-network:
    external: true

volumes:
  prometheus_data:
  grafana_data:
```

## 2.3. Prometheus конфігурація

### monitoring/prometheus/prometheus.yml:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'web-app'
    scrape_interval: 30s
    static_configs:
      - targets: ['web:8080']
    metrics_path: /metrics
```

## 2.4. Grafana Provisioning

### monitoring/grafana/provisioning/datasources/prometheus.yml:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```

## 2.5. Команди для демонстрації

```bash
# === PROMETHEUS ===

# Перевірка targets (всі повинні бути UP)
curl http://104.46.15.0:9090/api/v1/targets | python -m json.tool

# Виконання PromQL запиту
curl 'http://104.46.15.0:9090/api/v1/query?query=up'

# Перевірка готовності
curl http://104.46.15.0:9090/-/ready

# === GRAFANA ===

# Health check
curl http://104.46.15.0:3000/api/health

# Список data sources
curl -u admin:admin http://104.46.15.0:3000/api/datasources

# Список dashboards
curl -u admin:admin http://104.46.15.0:3000/api/search

# === SSH команди на VM ===

# Контейнери моніторингу
docker ps --filter "name=prometheus\|grafana\|node-exporter\|cadvisor"

# Логи Prometheus
docker logs prometheus --tail 20

# Логи Grafana
docker logs grafana --tail 20

# Метрики node-exporter
curl http://localhost:9100/metrics | head -30

# Метрики cadvisor
curl http://localhost:8080/metrics | grep container_memory | head -10

# Метрики застосунку
curl http://localhost:8080/metrics
```

---

# 📚 ЧАСТИНА 3: ПИТАННЯ ДЛЯ ЗАХИСТУ

## 🔴 Базові питання (обов'язково знати)

### 1. Що таке Prometheus і яка його роль?
**Відповідь:** Prometheus — це open-source система моніторингу, яка збирає метрики з targets за допомогою HTTP pull. Зберігає дані як time series (часові ряди). Використовує власну мову запитів PromQL. Є основою для збору метрик у нашому проєкті.

### 2. Що таке Grafana і для чого вона потрібна?
**Відповідь:** Grafana — це платформа для візуалізації метрик. Підключається до різних data sources (Prometheus, InfluxDB, MySQL). Дозволяє створювати інтерактивні dashboards з графіками, gauge, статистикою. Також підтримує alerting.

### 3. Що таке scrape interval?
**Відповідь:** Scrape interval — це інтервал, з яким Prometheus збирає метрики з targets. За замовчуванням 15 секунд. Можна змінити глобально або для конкретного job. Менший інтервал = більше даних = більше місця на диску.

### 4. Що показує метрика `up`?
**Відповідь:** Метрика `up` показує статус target:
- `up{job="prometheus"} = 1` — target доступний, scrape успішний
- `up{job="prometheus"} = 0` — target недоступний, помилка scrape
Це базова метрика для перевірки здоров'я сервісів.

### 5. Яка різниця між Counter та Gauge?
**Відповідь:**
- **Counter** — тільки зростає (http_requests_total). Для обчислення rate використовуємо `rate()` або `increase()`
- **Gauge** — може зростати і зменшуватися (temperature, memory_usage). Можна використовувати напряму.

## 🟡 Середні питання

### 6. Для чого потрібен Node Exporter?
**Відповідь:** Node Exporter збирає метрики операційної системи Linux:
- CPU: `node_cpu_seconds_total`
- RAM: `node_memory_MemAvailable_bytes`
- Disk: `node_filesystem_avail_bytes`
- Network: `node_network_receive_bytes_total`
Він монтує /proc, /sys для доступу до системних метрик.

### 7. Для чого потрібен cAdvisor?
**Відповідь:** cAdvisor (Container Advisor) збирає метрики Docker контейнерів:
- CPU per container: `container_cpu_usage_seconds_total`
- Memory per container: `container_memory_usage_bytes`
- Network per container: `container_network_receive_bytes_total`
Потребує доступу до Docker socket.

### 8. Що таке PromQL і наведіть приклад запиту?
**Відповідь:** PromQL — це мова запитів Prometheus. Приклади:
```promql
# CPU usage %
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage %
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Request rate per second
rate(http_requests_total[5m])
```

### 9. Як перевірити що Prometheus правильно збирає метрики?
**Відповідь:**
1. Відкрити http://IP:9090/targets — всі targets повинні бути UP (зелені)
2. У Graph виконати запит `up` — всі значення = 1
3. Перевірити конкретну метрику, наприклад `node_memory_MemTotal_bytes`

### 10. Що таке Grafana Provisioning?
**Відповідь:** Provisioning — це автоматична конфігурація Grafana через YAML файли. Дозволяє при запуску контейнера автоматично налаштувати:
- Data sources (prometheus.yml)
- Dashboards (dashboards.yml + JSON файли)
Файли монтуються в `/etc/grafana/provisioning/`

## 🟢 Складні питання

### 11. Поясніть функцію rate() в PromQL
**Відповідь:** `rate()` обчислює середню швидкість зміни counter за секунду:
```promql
rate(http_requests_total[5m])
```
- Бере значення за останні 5 хвилин
- Обчислює різницю між першим і останнім
- Ділить на кількість секунд
- Результат: requests per second

Важливо: rate() працює ТІЛЬКИ з counters, не з gauges!

### 12. Яка різниця між rate() та irate()?
**Відповідь:**
- `rate()` — середня швидкість за весь range (5m). Згладжує піки
- `irate()` — миттєва швидкість (2 останні точки). Показує піки

Для alerting краще rate() (менше false positives), для детального аналізу — irate().

### 13. Як Prometheus знаходить targets?
**Відповідь:** Є кілька способів:
1. **static_configs** — вручну вказані targets в prometheus.yml
2. **file_sd_configs** — targets з JSON/YAML файлів
3. **kubernetes_sd_configs** — автоматичне виявлення в K8s
4. **consul_sd_configs** — через Consul service discovery
5. **dns_sd_configs** — через DNS SRV records

У нашому проєкті використовуємо static_configs.

### 14. Як додати власні метрики до застосунку?
**Відповідь:**
1. Створити endpoint `/metrics` у застосунку
2. Виводити метрики у форматі Prometheus:
```
# HELP metric_name Description
# TYPE metric_name gauge
metric_name{label="value"} 123.45
```
3. Додати scrape job в prometheus.yml
4. Перевірити в Prometheus targets

### 15. Як налаштувати alerting у цій системі?
**Відповідь:**
1. **Prometheus Alertmanager** — додати alertmanager сервіс
2. Створити alert rules в prometheus.yml:
```yaml
rule_files:
  - /etc/prometheus/alerts.yml
```
3. Налаштувати receivers в alertmanager.yml (Email, Slack)
4. **Grafana Alerting** — альтернатива, налаштовується в UI

---

# 📚 ЧАСТИНА 4: ДЕМОНСТРАЦІЯ НА ЗАХИСТІ

## Чек-лист демонстрації:

### 1. Prometheus (5 хв)
- [ ] http://IP:9090 — відкрити UI
- [ ] Status → Targets — показати всі 4 targets UP
- [ ] Graph → виконати запит `up`
- [ ] Graph → виконати `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` — CPU%
- [ ] Graph → виконати `(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100` — RAM%

### 2. Grafana (5 хв)
- [ ] http://IP:3000 — відкрити UI (admin/admin)
- [ ] Показати Data Source → Prometheus
- [ ] Відкрити Dashboard з панелями
- [ ] Показати CPU графік
- [ ] Показати VM Uptime

### 3. Термінал (3 хв)
- [ ] `docker ps` — показати контейнери моніторингу
- [ ] `curl http://localhost:9100/metrics | head` — метрики node-exporter
- [ ] `curl http://localhost:8080/metrics` — метрики застосунку

### 4. Файли (2 хв)
- [ ] `monitoring/prometheus/prometheus.yml` — конфігурація
- [ ] `monitoring/docker-compose.monitoring.yml` — сервіси

---

# 📚 ЧАСТИНА 5: ГЛОСАРІЙ

| Термін | Визначення |
|--------|------------|
| **Prometheus** | Time-series database для метрик з pull-моделлю |
| **Grafana** | Платформа візуалізації та аналітики |
| **PromQL** | Мова запитів Prometheus |
| **Scrape** | Процес збору метрик з target |
| **Target** | Endpoint, з якого Prometheus збирає метрики |
| **Exporter** | Компонент, що експортує метрики у форматі Prometheus |
| **Node Exporter** | Exporter для Linux системних метрик |
| **cAdvisor** | Container Advisor — метрики Docker контейнерів |
| **Counter** | Метрика, що тільки зростає |
| **Gauge** | Метрика, що може зростати і зменшуватися |
| **Histogram** | Метрика з розподілом по бакетам |
| **Label** | Мітка для фільтрації та групування метрик |
| **Time Series** | Послідовність значень з часовими мітками |
| **Dashboard** | Набір панелей для візуалізації |
| **Provisioning** | Автоматична конфігурація через файли |
| **Alertmanager** | Компонент Prometheus для alerting |
| **rate()** | PromQL функція для обчислення швидкості counter |
| **Data Source** | Джерело даних у Grafana |

---

# 📚 ЧАСТИНА 6: КОРИСНІ ПОСИЛАННЯ

| Ресурс | URL |
|--------|-----|
| Prometheus Documentation | https://prometheus.io/docs/ |
| PromQL Cheat Sheet | https://promlabs.com/promql-cheat-sheet/ |
| Grafana Documentation | https://grafana.com/docs/ |
| Grafana Dashboards | https://grafana.com/grafana/dashboards/ |
| Node Exporter | https://github.com/prometheus/node_exporter |
| cAdvisor | https://github.com/google/cadvisor |
| Awesome Prometheus | https://github.com/roaldnefs/awesome-prometheus |

---

**Дата створення:** 29 квітня 2026
**Автор:** GitHub Copilot для Лабораторної роботи №5
