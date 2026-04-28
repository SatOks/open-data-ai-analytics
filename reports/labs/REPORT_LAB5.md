# Лабораторна робота №5

## Тема: Моніторинг за допомогою Prometheus та Grafana

**Дата виконання:** 28 квітня 2026 р.

---

## Мета роботи

Навчитися:
- організовувати базовий моніторинг розгорнутого застосунку
- збирати метрики з сервера, контейнерів і застосунку
- налаштовувати Prometheus для збору метрик
- використовувати Grafana для побудови дашбордів
- аналізувати стан інфраструктури й сервісів на основі метрик

---

## Виконані завдання

### 1. Створення стеку моніторингу

Створено директорію `monitoring/` з наступною структурою:

```
monitoring/
├── prometheus/
│   └── prometheus.yml              # Конфігурація Prometheus
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml      # Auto-provisioning Prometheus
│       └── dashboards/
│           ├── dashboards.yml      # Dashboard provisioning config
│           └── odaa-dashboard.json # Готовий дашборд
└── docker-compose.monitoring.yml   # Docker Compose для моніторингу
```

### 2. Сервіси моніторингу

| Сервіс | Версія | Призначення | Порт |
|--------|--------|-------------|------|
| Prometheus | v2.45.0 | Збір та зберігання метрик | 9090 |
| Grafana | v10.0.0 | Візуалізація та дашборди | 3000 |
| Node Exporter | v1.6.0 | Метрики Linux VM | 9100 (внутрішній) |
| cAdvisor | v0.47.0 | Метрики Docker контейнерів | 8080 (внутрішній) |

### 3. Конфігурація Prometheus

Файл `prometheus.yml` містить scrape_configs для збору метрик:

```yaml
scrape_configs:
  # Самомоніторинг Prometheus
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Метрики Linux VM
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # Метрики контейнерів
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  # Метрики веб-застосунку
  - job_name: 'web-app'
    static_configs:
      - targets: ['web:8080']
    metrics_path: /metrics
```

### 4. Метрики застосунку

До веб-сервісу (`services/web/app.py`) додано endpoint `/metrics`:

```python
@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    lines = [
        "# HELP web_app_up Application is up and running",
        "# TYPE web_app_up gauge",
        "web_app_up 1",
        
        "# HELP web_database_available Database file exists",
        "# TYPE web_database_available gauge",
        f"web_database_available {1 if SQLITE_PATH.exists() else 0}",
        
        "# HELP web_figures_count Number of generated figures",
        "# TYPE web_figures_count gauge",
        f"web_figures_count {len(_list_figures())}",
        
        # ... інші метрики
    ]
    return Response("\n".join(lines), mimetype="text/plain")
```

### 5. Grafana Provisioning

#### Datasource (автоматичне підключення Prometheus)

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

#### Dashboard

Створено готовий дашборд `odaa-dashboard.json` з панелями:

| Панель | Тип | PromQL запит |
|--------|-----|--------------|
| VM CPU Usage | Time Series | `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` |
| VM Memory Usage | Time Series | `(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100` |
| Running Containers | Stat | `count(container_memory_usage_bytes{name!=""})` |
| Web Service Status | Stat | `up{job="web-app"}` |
| VM Uptime | Stat | `node_time_seconds - node_boot_time_seconds` |
| Disk Usage | Gauge | `(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100` |
| Web Container Memory | Time Series | `container_memory_usage_bytes{name=~".*web.*"}` |
| Web Container CPU | Time Series | `rate(container_cpu_usage_seconds_total{name=~".*web.*"}[5m]) * 100` |
| All Containers Memory | Time Series | `container_memory_usage_bytes{name!=""}` |

---

## Архітектура моніторингу

```
┌──────────────────────────────────────────────────────────────────┐
│                        Linux VM (Azure)                           │
│                                                                   │
│  ┌────────────────────┐     ┌──────────────────────────────────┐ │
│  │    Main Stack      │     │      Monitoring Stack            │ │
│  │                    │     │                                  │ │
│  │  ┌──────────────┐  │     │  ┌────────────┐                  │ │
│  │  │  data_load   │  │     │  │ Prometheus │◄──── :9090       │ │
│  │  └──────────────┘  │     │  │            │                  │ │
│  │  ┌──────────────┐  │     │  │  scrape    │                  │ │
│  │  │data_quality  │  │     │  └─────┬──────┘                  │ │
│  │  └──────────────┘  │     │        │                         │ │
│  │  ┌──────────────┐  │     │        ▼                         │ │
│  │  │data_research │  │     │  ┌────────────┐                  │ │
│  │  └──────────────┘  │     │  │  Grafana   │◄──── :3000       │ │
│  │  ┌──────────────┐  │     │  │            │                  │ │
│  │  │visualization │  │     │  │ Dashboard  │                  │ │
│  │  └──────────────┘  │     │  └────────────┘                  │ │
│  │  ┌──────────────┐  │     │                                  │ │
│  │  │     web      │──┼─────┼──► /metrics                      │ │
│  │  │    :8080     │  │     │                                  │ │
│  │  └──────────────┘  │     │  ┌─────────────┐                 │ │
│  │                    │     │  │node-exporter│──► VM metrics   │ │
│  │  analytics-network │     │  └─────────────┘                 │ │
│  └────────────────────┘     │  ┌─────────────┐                 │ │
│                             │  │  cAdvisor   │──► Container    │ │
│                             │  └─────────────┘     metrics     │ │
│                             │                                  │ │
│                             │  monitoring-network              │ │
│                             └──────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## Запуск моніторингу

### Локальний запуск

```bash
# 1. Запустити основний стек
docker compose up -d --build

# 2. Запустити моніторинг
docker compose -f monitoring/docker-compose.monitoring.yml up -d

# 3. Перевірити статус
docker compose ps
docker compose -f monitoring/docker-compose.monitoring.yml ps
```

### Доступ до сервісів

| Сервіс | URL | Credentials |
|--------|-----|-------------|
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | - |
| Prometheus Targets | http://localhost:9090/targets | - |
| Web App Metrics | http://localhost:8080/metrics | - |

---

## Результати

### Дашборд Grafana

Створено дашборд "Open Data AI Analytics Dashboard" з 9 панелями:

1. **VM CPU Usage (%)** - графік завантаження процесора
2. **VM Memory Usage (%)** - графік використання пам'яті
3. **Running Containers** - кількість запущених контейнерів
4. **Web Service Status** - статус веб-сервісу (UP/DOWN)
5. **VM Uptime** - час роботи системи
6. **Disk Usage** - gauge використання диску
7. **Web Container Memory Usage** - пам'ять веб-контейнера
8. **Web Container CPU Usage** - CPU веб-контейнера
9. **All Containers Memory Usage** - пам'ять всіх контейнерів

### Prometheus Targets

| Job | Target | Status |
|-----|--------|--------|
| prometheus | localhost:9090 | UP |
| node-exporter | node-exporter:9100 | UP |
| cadvisor | cadvisor:8080 | UP |
| web-app | web:8080 | UP |

---

## Приклади PromQL запитів

### Системні метрики

```promql
# CPU Usage (%)
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory Usage (%)
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk Usage (%)
(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100

# Network I/O
rate(node_network_receive_bytes_total[5m])
rate(node_network_transmit_bytes_total[5m])
```

### Контейнерні метрики

```promql
# Container Memory Usage (bytes)
container_memory_usage_bytes{name!=""}

# Container CPU Usage (%)
rate(container_cpu_usage_seconds_total{name!=""}[5m]) * 100

# Container Count
count(container_memory_usage_bytes{name!=""})
```

### Метрики застосунку

```promql
# Web service availability
up{job="web-app"}

# Database availability
web_database_available

# Generated figures count
web_figures_count
```

---

## Висновки

У ході виконання лабораторної роботи було:

1. **Розгорнуто стек моніторингу** — Prometheus, Grafana, Node Exporter, cAdvisor
2. **Налаштовано збір метрик** — з VM, контейнерів та веб-застосунку
3. **Створено дашборд** — візуалізація ключових показників системи
4. **Автоматизовано provisioning** — datasource та dashboards підключаються автоматично
5. **Додано метрики застосунку** — endpoint `/metrics` у веб-сервісі

### Переваги моніторингу:

- **Проактивність** — виявлення проблем до їх критичного рівня
- **Історія** — збереження метрик для аналізу трендів
- **Візуалізація** — наочне представлення стану системи
- **Alerting** — можливість налаштування сповіщень (Grafana Alerting)

---

## Труднощі та їх вирішення

1. **Docker мережі** — monitoring stack потребує доступу до web сервісу в іншій мережі. Вирішення: використання external network.

2. **Prometheus формат метрик** — endpoint `/metrics` має повертати текст у форматі Prometheus. Вирішення: створення правильного формату у Flask route.

3. **Grafana datasource** — потрібно підключити Prometheus при старті. Вирішення: provisioning через YAML файли.

4. **cAdvisor привілеї** — потребує доступу до Docker socket та системних директорій. Вирішення: монтування `/var/run`, `/sys`, `/var/lib/docker`.
