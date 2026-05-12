# Лабораторна робота №6

## Тема: Моніторинг за допомогою Prometheus та Grafana

**Дата виконання:** 12 травня 2026 р.

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

### Частина 1. Оновлення хмарного середовища

#### Відкриті порти в Azure NSG:

| Порт | Призначення | NSG Rule |
|------|-------------|----------|
| 22 | SSH доступ | AllowSSH |
| 8080 | Web застосунок | AllowWeb |
| 3000 | Grafana Dashboard | AllowGrafana |
| 9090 | Prometheus UI | AllowPrometheus |

#### Конфігурація cloud-init для моніторингу:

```yaml
runcmd:
  # ... базове налаштування ...
  # Запуск моніторингу
  - cd /home/azureuser/app && docker compose -f monitoring/docker-compose.monitoring.yml up -d
```

### Частина 2. Розгортання сервісів моніторингу

#### Структура проєкту:

```
monitoring/
├── prometheus/
│   └── prometheus.yml          # Конфігурація scrape jobs
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml  # Auto-provisioning data source
│       └── dashboards/
│           ├── dashboards.yml  # Dashboard provider config
│           └── odaa-dashboard.json  # Custom dashboard
└── docker-compose.monitoring.yml   # Docker Compose для моніторингу
```

#### Запущені сервіси:

| Сервіс | Образ | Порт | Статус |
|--------|-------|------|--------|
| prometheus | prom/prometheus:v2.45.0 | 9090 | ✅ Up 2 weeks |
| grafana | grafana/grafana:10.0.0 | 3000 | ✅ Up 2 weeks |
| node-exporter | prom/node-exporter:v1.6.0 | 9100 (internal) | ✅ Up 2 weeks |
| cadvisor | gcr.io/cadvisor/cadvisor:v0.49.1 | 8080 (internal) | ✅ Up 2 weeks (healthy) |

### Частина 3. Налаштування Prometheus

#### prometheus.yml конфігурація:

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

#### Статус Targets (12 травня 2026):

| Job | Target | Health | Last Scrape |
|-----|--------|--------|-------------|
| prometheus | localhost:9090 | 🟢 UP | ~10ms |
| node-exporter | node-exporter:9100 | 🟢 UP | ~35ms |
| cadvisor | cadvisor:8080 | 🟢 UP | ~47ms |
| web-app | web:8080 | 🟢 UP | ~5ms |

### Частина 4. Налаштування Grafana

#### Data Source:

- **Name:** Prometheus
- **Type:** prometheus
- **URL:** http://prometheus:9090
- **Access:** proxy
- **Default:** Yes

#### Provisioning конфігурація:

```yaml
# grafana/provisioning/datasources/prometheus.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```

### Частина 5. Побудова дашборду

#### Dashboard: "Open Data AI Analytics Dashboard"

**Панелі на дашборді:**

| # | Панель | Тип | PromQL запит |
|---|--------|-----|--------------|
| 1 | VM CPU Usage (%) | Time series | `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` |
| 2 | VM Memory Usage (%) | Time series | `(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100` |
| 3 | Active Services | Stat | `count(up == 1)` |
| 4 | Web Service Status | Stat | `up{job="web-app"}` |
| 5 | VM Uptime | Stat | `node_time_seconds - node_boot_time_seconds` |
| 6 | Disk Usage | Gauge | `(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100` |
| 7 | Web Container Memory | Time series | `container_memory_usage_bytes{name=~".*web.*"}` |
| 8 | Web Container CPU | Time series | `rate(container_cpu_usage_seconds_total{name=~".*web.*"}[5m]) * 100` |
| 9 | All Containers Memory | Time series | `container_memory_usage_bytes{name!=""}` |

---

## Архітектура моніторингу

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AZURE VM (104.46.15.0)                            │
│                        Ubuntu 22.04 LTS                                  │
│                        Standard_D2s_v3                                   │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                         DOCKER ENGINE                               │ │
│  │                                                                      │ │
│  │  ┌─────────────────────┐     ┌──────────────────────────────────┐  │ │
│  │  │   APPLICATION       │     │      MONITORING STACK             │  │ │
│  │  │      STACK          │     │                                   │  │ │
│  │  │                     │     │  ┌────────────────────────────┐  │  │ │
│  │  │  ┌───────────────┐  │     │  │     PROMETHEUS :9090       │  │  │ │
│  │  │  │   data_load   │  │     │  │  • scrape_interval: 15s    │  │  │ │
│  │  │  └───────────────┘  │     │  │  • retention: 15d          │  │  │ │
│  │  │  ┌───────────────┐  │     │  │  • 4 active targets        │  │  │ │
│  │  │  │ data_quality  │  │     │  └────────────┬───────────────┘  │  │ │
│  │  │  └───────────────┘  │     │               │                   │  │ │
│  │  │  ┌───────────────┐  │     │               │ PromQL            │  │ │
│  │  │  │ data_research │  │     │               ▼                   │  │ │
│  │  │  └───────────────┘  │     │  ┌────────────────────────────┐  │  │ │
│  │  │  ┌───────────────┐  │     │  │      GRAFANA :3000         │  │  │ │
│  │  │  │ visualization │  │     │  │  • Prometheus datasource   │  │  │ │
│  │  │  └───────────────┘  │     │  │  • Custom dashboard        │  │  │ │
│  │  │  ┌───────────────┐  │     │  │  • 9 panels                │  │  │ │
│  │  │  │     WEB       │◀─┼──┐  │  └────────────────────────────┘  │  │ │
│  │  │  │    :8080      │  │  │  │                                   │  │ │
│  │  │  │   /metrics    │──┼──┼──┼─────► scrape every 30s           │  │ │
│  │  │  └───────────────┘  │  │  │                                   │  │ │
│  │  └─────────────────────┘  │  │  ┌────────────────────────────┐  │  │ │
│  │                           │  │  │   NODE EXPORTER :9100      │  │  │ │
│  │                           │  └──│  • CPU, RAM, Disk, Network │  │  │ │
│  │                           │     │  • scrape every 15s        │  │  │ │
│  │                           │     └────────────────────────────┘  │  │ │
│  │                           │                                      │  │ │
│  │                           │     ┌────────────────────────────┐  │  │ │
│  │                           └─────│      CADVISOR :8080        │  │  │ │
│  │                                 │  • Container metrics       │  │  │ │
│  │                                 │  • scrape every 15s        │  │  │ │
│  │                                 └────────────────────────────┘  │  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## URL доступу

| Сервіс | URL | Credentials |
|--------|-----|-------------|
| Web Application | http://104.46.15.0:8080 | - |
| Prometheus | http://104.46.15.0:9090 | - |
| Grafana | http://104.46.15.0:3000 | admin / admin |
| SSH | ssh azureuser@104.46.15.0 | SSH key |

---

## Метрики застосунку

### Endpoint /metrics (Web Service):

```
# HELP web_app_up Application status (1=up, 0=down)
# TYPE web_app_up gauge
web_app_up 1

# HELP web_database_available Database connection status
# TYPE web_database_available gauge
web_database_available 1

# HELP web_figures_count Number of generated figures
# TYPE web_figures_count gauge
web_figures_count 8

# HELP web_reports_available Number of available reports
# TYPE web_reports_available gauge
web_reports_available 1
```

---

## Джерела метрик

### 1. Node Exporter (Стан VM)

| Категорія | Метрики |
|-----------|---------|
| CPU | `node_cpu_seconds_total`, `node_load1`, `node_load5` |
| Memory | `node_memory_MemTotal_bytes`, `node_memory_MemAvailable_bytes` |
| Disk | `node_filesystem_size_bytes`, `node_filesystem_avail_bytes` |
| Network | `node_network_receive_bytes_total`, `node_network_transmit_bytes_total` |
| System | `node_time_seconds`, `node_boot_time_seconds` |

### 2. cAdvisor (Стан контейнерів)

| Категорія | Метрики |
|-----------|---------|
| CPU | `container_cpu_usage_seconds_total`, `container_cpu_system_seconds_total` |
| Memory | `container_memory_usage_bytes`, `container_memory_working_set_bytes` |
| Network | `container_network_receive_bytes_total`, `container_network_transmit_bytes_total` |
| Filesystem | `container_fs_usage_bytes`, `container_fs_limit_bytes` |

### 3. Web Application (Стан застосунку)

| Метрика | Тип | Опис |
|---------|-----|------|
| `web_app_up` | gauge | Статус застосунку (1=up) |
| `web_database_available` | gauge | Доступність БД |
| `web_figures_count` | gauge | Кількість графіків |
| `web_reports_available` | gauge | Кількість звітів |

---

## Демонстрація роботи

### Перевірка Prometheus Targets:

```bash
# На VM через SSH
curl -s 'http://localhost:9090/api/v1/targets' | jq '.data.activeTargets[].health'
# Результат: "up", "up", "up", "up"
```

### Перевірка Grafana:

```bash
curl -s http://104.46.15.0:3000/api/health
# {"commit":"81d85ce802","database":"ok","version":"10.0.0"}
```

### Перевірка Web Application:

```bash
curl -s http://104.46.15.0:8080/health
# {"status":"ok"}

curl -s http://104.46.15.0:8080/metrics
# web_app_up 1
# web_database_available 1
# ...
```

---

## Результати

### Створені файли:

| Файл | Призначення |
|------|-------------|
| `monitoring/docker-compose.monitoring.yml` | Docker Compose для стеку моніторингу |
| `monitoring/prometheus/prometheus.yml` | Конфігурація Prometheus scrape jobs |
| `monitoring/grafana/provisioning/datasources/prometheus.yml` | Auto-provisioning data source |
| `monitoring/grafana/provisioning/dashboards/dashboards.yml` | Dashboard provider |
| `monitoring/grafana/provisioning/dashboards/odaa-dashboard.json` | Custom dashboard JSON |
| `services/web/app.py` | Оновлено з endpoint /metrics |

### Метрики моніторингу:

- **Scrape interval:** 15 секунд (global), 30 секунд (web-app)
- **Data retention:** 15 днів
- **Active targets:** 4 (всі UP)
- **Dashboard panels:** 9

---

## Труднощі та їх вирішення

### 1. cAdvisor не бачив Docker контейнери

**Проблема:** cAdvisor показував тільки системні процеси, не Docker контейнери.

**Причина:** Несумісність з overlayfs storage driver на Azure VM.

**Вирішення:** 
- Оновлено версію cAdvisor до v0.49.1
- Додано volume mount для Docker socket: `/var/run/docker.sock:/var/run/docker.sock:ro`
- Змінено шлях cgroup: `/sys/fs/cgroup:/cgroup:ro`

### 2. Grafana Data Source не відображався

**Проблема:** Provisioned data source не з'являвся в UI.

**Причина:** Grafana 10.0 змінила структуру меню.

**Вирішення:** Перезапуск контейнера + навігація через Administration → Data sources.

### 3. Dashboard показував "No data"

**Проблема:** Всі панелі показували "No data" після імпорту.

**Причина:** Невідповідність UID data source в JSON.

**Вирішення:** Замінено `"uid": "prometheus"` на фактичний UID `"uid": "PBFA97CFB590B2093"`.

---

## Спостереження за результатами моніторингу

### За 2 тижні роботи системи:

1. **CPU Usage:** Середнє ~5-10%, піки до 30% при обробці даних
2. **Memory Usage:** Стабільно ~65-70% (достатньо для всіх сервісів)
3. **Disk Usage:** ~17%, повільне зростання через логи Docker
4. **VM Uptime:** 2+ тижні безперервної роботи
5. **All services:** Стабільно UP, без збоїв

### Рекомендації:

- Налаштувати log rotation для Docker
- Додати alerting на критичні метрики (CPU > 90%, Disk > 80%)
- Розглянути Loki для централізованого збору логів

---

## Висновки

У ході виконання лабораторної роботи було:

1. **Розгорнуто стек моніторингу** — Prometheus + Grafana + Node Exporter + cAdvisor
2. **Налаштовано збір метрик** — 4 targets з різних джерел (VM, контейнери, застосунок)
3. **Створено custom dashboard** — 9 панелей для візуалізації ключових метрик
4. **Додано endpoint /metrics** — застосунок експортує власні бізнес-метрики
5. **Забезпечено observability** — можливість в реальному часі бачити стан системи

Моніторинг критично важливий для DevOps, оскільки дозволяє:
- Вчасно виявляти проблеми до того, як вони стануть критичними
- Аналізувати тренди та планувати масштабування
- Проводити post-mortem аналіз інцидентів
- Демонструвати SLA метрики

---

**Дата створення звіту:** 12 травня 2026
