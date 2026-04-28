# 🎓 Лабораторна робота №4 — Повний гайд для захисту

## Тема: Інфраструктура як код. Розгортання Docker-проєкту в Microsoft Azure

---

# 📚 ЧАСТИНА 1: ТЕОРЕТИЧНІ ОСНОВИ

## 1.1. Що таке Infrastructure as Code (IaC)?

**Infrastructure as Code** — це підхід до управління та провізіонінгу інфраструктури через машиночитаний код замість ручних процесів.

### Ключові принципи IaC:

| Принцип | Опис |
|---------|------|
| **Декларативність** | Описуємо *що* хочемо отримати, а не *як* це зробити |
| **Ідемпотентність** | Повторне застосування дає той самий результат |
| **Версіонування** | Код зберігається в Git, можна відстежити зміни |
| **Відтворюваність** | Можна створити ідентичне середовище будь-коли |
| **Автоматизація** | Мінімум ручних дій, менше помилок |

### Переваги IaC:

```
┌─────────────────────────────────────────────────────────────┐
│                    ПЕРЕВАГИ IaC                              │
├─────────────────────────────────────────────────────────────┤
│  ✓ Швидкість розгортання (хвилини замість днів)             │
│  ✓ Консистентність середовищ (dev = staging = prod)         │
│  ✓ Документація = код (self-documenting infrastructure)     │
│  ✓ Аудит змін через Git history                             │
│  ✓ Легке масштабування та клонування                        │
│  ✓ Disaster Recovery — швидке відновлення                   │
│  ✓ Cost Management — видалення непотрібних ресурсів         │
└─────────────────────────────────────────────────────────────┘
```

### Порівняння інструментів IaC:

| Інструмент | Тип | Мова | Хмари | Особливість |
|------------|-----|------|-------|-------------|
| **Terraform** | Декларативний | HCL | Multi-cloud | Найпопулярніший, state management |
| **Azure CLI** | Імперативний | Bash/PS | Azure | Простий, вбудований в Azure |
| **ARM Templates** | Декларативний | JSON | Azure | Нативний для Azure |
| **Bicep** | Декларативний | DSL | Azure | Спрощений ARM |
| **Ansible** | Декларативний | YAML | Multi-cloud | Configuration management |
| **Pulumi** | Декларативний | Python/JS/Go | Multi-cloud | Справжні мови програмування |

---

## 1.2. Microsoft Azure — Основні концепції

### Ієрархія ресурсів Azure:

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Account                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   Subscription                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              Resource Group                      │  │  │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────────────┐  │  │  │
│  │  │  │   VM    │  │  VNet   │  │  Storage Account│  │  │  │
│  │  │  └─────────┘  └─────────┘  └─────────────────┘  │  │  │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────────────┐  │  │  │
│  │  │  │   NSG   │  │ Public IP│ │  Network Interface│ │  │  │
│  │  │  └─────────┘  └─────────┘  └─────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Основні сервіси Azure для цієї роботи:

| Сервіс | Призначення | Команда створення |
|--------|-------------|-------------------|
| **Resource Group** | Логічний контейнер для ресурсів | `az group create` |
| **Virtual Network (VNet)** | Ізольована мережа в Azure | `az network vnet create` |
| **Subnet** | Сегмент мережі всередині VNet | `az network vnet subnet create` |
| **Network Security Group (NSG)** | Фаєрвол для VM | `az network nsg create` |
| **Public IP** | Зовнішня IP-адреса | `az network public-ip create` |
| **Network Interface (NIC)** | Мережевий адаптер VM | `az network nic create` |
| **Virtual Machine (VM)** | Віртуальний сервер | `az vm create` |

### Network Security Group (NSG) — Правила:

```
┌─────────────────────────────────────────────────────────────┐
│               Network Security Group Rules                   │
├─────────────────────────────────────────────────────────────┤
│  Priority │ Name           │ Port  │ Direction │ Action     │
├───────────┼────────────────┼───────┼───────────┼────────────┤
│    100    │ AllowSSH       │  22   │  Inbound  │   Allow    │
│    200    │ AllowWeb       │ 8080  │  Inbound  │   Allow    │
│    300    │ AllowGrafana   │ 3000  │  Inbound  │   Allow    │
│    400    │ AllowPrometheus│ 9090  │  Inbound  │   Allow    │
│   65000   │ DenyAllInbound │  *    │  Inbound  │   Deny     │
└─────────────────────────────────────────────────────────────┘
```

---

## 1.3. Azure CLI — Основні команди

### Автентифікація:

```bash
# Вхід в Azure (відкриває браузер)
az login

# Перевірка поточного акаунту
az account show

# Список підписок
az account list --output table

# Вибір підписки
az account set --subscription "Subscription Name"
```

### Робота з Resource Groups:

```bash
# Створення
az group create --name odaa-rg --location northeurope

# Список груп
az group list --output table

# Видалення (каскадне — видаляє всі ресурси!)
az group delete --name odaa-rg --yes --no-wait
```

### Робота з Virtual Machines:

```bash
# Створення VM
az vm create \
  --resource-group odaa-rg \
  --name odaa-vm \
  --image Ubuntu2204 \
  --size Standard_D2s_v3 \
  --admin-username azureuser \
  --generate-ssh-keys \
  --custom-data cloud-init.yaml

# Список VM
az vm list --output table

# Стан VM
az vm show --name odaa-vm -g odaa-rg --query "provisioningState"

# Публічна IP
az vm show --name odaa-vm -g odaa-rg --show-details --query "publicIps"

# Перезапуск VM
az vm restart --name odaa-vm -g odaa-rg

# Видалення VM
az vm delete --name odaa-vm -g odaa-rg --yes
```

---

## 1.4. Cloud-init — Автоматизація конфігурації VM

### Що таке cloud-init?

**Cloud-init** — це індустріальний стандарт для автоматичної ініціалізації cloud instances. Він виконується при **першому запуску** VM і дозволяє:

- Оновлювати пакети
- Встановлювати програми
- Створювати файли та директорії
- Запускати команди
- Налаштовувати користувачів

### Структура cloud-init.yaml:

```yaml
#cloud-config
# Перший рядок ОБОВ'ЯЗКОВИЙ - визначає формат файлу

# Оновлення системи
package_update: true
package_upgrade: true

# Встановлення пакетів
packages:
  - docker.io
  - docker-compose-v2
  - git

# Виконання команд при першому запуску
runcmd:
  - systemctl enable docker
  - systemctl start docker
  - usermod -aG docker azureuser
  - git clone https://github.com/user/repo.git /home/azureuser/app
  - cd /home/azureuser/app && docker compose up -d

# Створення файлів
write_files:
  - path: /home/azureuser/.docker/config.json
    content: |
      {"detachKeys": "ctrl-p,ctrl-q"}
    owner: azureuser:azureuser
```

### Перевірка статусу cloud-init:

```bash
# Статус виконання
cloud-init status

# Детальні логи
sudo cat /var/log/cloud-init-output.log

# Перевірка помилок
sudo cloud-init analyze blame
```

### Стадії cloud-init:

```
┌─────────────────────────────────────────────────────────────┐
│                  Cloud-init Stages                           │
├─────────────────────────────────────────────────────────────┤
│  1. local    │ Мережа ще не налаштована                     │
│  2. network  │ Мережа готова, метадані отримані             │
│  3. config   │ Конфігурація модулів                         │
│  4. final    │ Виконання runcmd, встановлення пакетів       │
└─────────────────────────────────────────────────────────────┘
```

---

## 1.5. SSH — Secure Shell

### Що таке SSH?

**SSH (Secure Shell)** — це криптографічний мережевий протокол для безпечного віддаленого доступу до серверів.

### Генерація SSH ключів:

```bash
# Генерація пари ключів (якщо ще немає)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Або RSA (більш сумісний)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Ключі зберігаються:
# Приватний: ~/.ssh/id_ed25519 (НІКОЛИ не передавати!)
# Публічний: ~/.ssh/id_ed25519.pub (можна передавати)
```

### Підключення до VM:

```bash
# Базове підключення
ssh azureuser@104.46.15.0

# З вказанням ключа
ssh -i ~/.ssh/id_rsa azureuser@104.46.15.0

# Виконання команди без входу
ssh azureuser@104.46.15.0 "docker ps"

# Копіювання файлів на сервер
scp local_file.txt azureuser@104.46.15.0:/home/azureuser/

# Копіювання директорії
scp -r local_folder/ azureuser@104.46.15.0:/home/azureuser/
```

---

# 📚 ЧАСТИНА 2: ПРАКТИЧНА РЕАЛІЗАЦІЯ

## 2.1. Архітектура рішення

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AZURE CLOUD                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                Resource Group: odaa-rg                         │  │
│  │                                                                │  │
│  │  ┌─────────────────────────────────────────────────────────┐  │  │
│  │  │              Virtual Network: odaa-vnet                  │  │  │
│  │  │              Address Space: 10.0.0.0/16                  │  │  │
│  │  │  ┌───────────────────────────────────────────────────┐  │  │  │
│  │  │  │            Subnet: 10.0.1.0/24                     │  │  │  │
│  │  │  │  ┌─────────────────────────────────────────────┐  │  │  │  │
│  │  │  │  │         Linux VM: odaa-vm                    │  │  │  │  │
│  │  │  │  │         Ubuntu 22.04 LTS                     │  │  │  │  │
│  │  │  │  │         Standard_D2s_v3 (2 vCPU, 8 GB RAM)   │  │  │  │  │
│  │  │  │  │                                              │  │  │  │  │
│  │  │  │  │  ┌────────────────────────────────────────┐  │  │  │  │  │
│  │  │  │  │  │        Docker Engine                   │  │  │  │  │  │
│  │  │  │  │  │                                        │  │  │  │  │  │
│  │  │  │  │  │  ┌──────────────────────────────────┐  │  │  │  │  │  │
│  │  │  │  │  │  │    Application Stack              │  │  │  │  │  │  │
│  │  │  │  │  │  │  • data_load                      │  │  │  │  │  │  │
│  │  │  │  │  │  │  • data_quality_analysis          │  │  │  │  │  │  │
│  │  │  │  │  │  │  • data_research                  │  │  │  │  │  │  │
│  │  │  │  │  │  │  • visualization                  │  │  │  │  │  │  │
│  │  │  │  │  │  │  • web (Flask) ──────────► :8080  │  │  │  │  │  │  │
│  │  │  │  │  │  └──────────────────────────────────┘  │  │  │  │  │  │
│  │  │  │  │  │                                        │  │  │  │  │  │
│  │  │  │  │  │  ┌──────────────────────────────────┐  │  │  │  │  │  │
│  │  │  │  │  │  │    Monitoring Stack               │  │  │  │  │  │  │
│  │  │  │  │  │  │  • prometheus ────────────► :9090 │  │  │  │  │  │  │
│  │  │  │  │  │  │  • grafana ───────────────► :3000 │  │  │  │  │  │  │
│  │  │  │  │  │  │  • node-exporter                  │  │  │  │  │  │  │
│  │  │  │  │  │  │  • cadvisor                       │  │  │  │  │  │  │
│  │  │  │  │  │  └──────────────────────────────────┘  │  │  │  │  │  │
│  │  │  │  │  └────────────────────────────────────────┘  │  │  │  │  │
│  │  │  │  └─────────────────────────────────────────────┘  │  │  │  │
│  │  │  └───────────────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────┘  │  │
│  │                                                                │  │
│  │  ┌─────────────────┐    ┌────────────────────────────────┐   │  │
│  │  │   Public IP     │    │   Network Security Group       │   │  │
│  │  │  104.46.15.0    │    │   • SSH (22)                   │   │  │
│  │  │  (Static)       │    │   • Web (8080)                 │   │  │
│  │  └─────────────────┘    │   • Grafana (3000)             │   │  │
│  │                          │   • Prometheus (9090)          │   │  │
│  │                          └────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS/HTTP
                                    ▼
                        ┌───────────────────┐
                        │   User Browser    │
                        │   Your Laptop     │
                        └───────────────────┘
```

## 2.2. Файли проєкту

### infra/azure-deploy.ps1 (PowerShell)

```powershell
# Скрипт розгортання інфраструктури в Azure
param(
    [string]$ResourceGroup = "odaa-rg",
    [string]$Location = "northeurope",
    [string]$VMSize = "Standard_D2s_v3"
)

# 1. Створення Resource Group
az group create --name $ResourceGroup --location $Location

# 2. Створення Virtual Network
az network vnet create `
    --resource-group $ResourceGroup `
    --name odaa-vnet `
    --address-prefix 10.0.0.0/16 `
    --subnet-name odaa-subnet `
    --subnet-prefix 10.0.1.0/24

# 3. Створення NSG
az network nsg create --resource-group $ResourceGroup --name odaa-nsg

# 4. Правила NSG
az network nsg rule create -g $ResourceGroup --nsg-name odaa-nsg `
    -n AllowSSH --priority 100 --destination-port-ranges 22
az network nsg rule create -g $ResourceGroup --nsg-name odaa-nsg `
    -n AllowWeb --priority 200 --destination-port-ranges 8080
az network nsg rule create -g $ResourceGroup --nsg-name odaa-nsg `
    -n AllowGrafana --priority 300 --destination-port-ranges 3000
az network nsg rule create -g $ResourceGroup --nsg-name odaa-nsg `
    -n AllowPrometheus --priority 400 --destination-port-ranges 9090

# 5. Створення Public IP
az network public-ip create -g $ResourceGroup --name odaa-public-ip --sku Standard

# 6. Створення NIC
az network nic create -g $ResourceGroup --name odaa-nic `
    --vnet-name odaa-vnet --subnet odaa-subnet `
    --network-security-group odaa-nsg --public-ip-address odaa-public-ip

# 7. Створення VM
az vm create -g $ResourceGroup --name odaa-vm `
    --nics odaa-nic --image Ubuntu2204 --size $VMSize `
    --admin-username azureuser --generate-ssh-keys `
    --custom-data cloud-init.yaml
```

### infra/cloud-init.yaml

```yaml
#cloud-config
package_update: true
package_upgrade: true

packages:
  - docker.io
  - docker-compose-v2
  - git

runcmd:
  - systemctl enable docker
  - systemctl start docker
  - usermod -aG docker azureuser
  - mkdir -p /home/azureuser/.docker
  - chown -R azureuser:azureuser /home/azureuser/.docker
  - git clone https://github.com/SatOks/open-data-ai-analytics.git /home/azureuser/app
  - chown -R azureuser:azureuser /home/azureuser/app
  - cd /home/azureuser/app && docker compose up -d
  - sleep 30
  - cd /home/azureuser/app && docker compose -f monitoring/docker-compose.monitoring.yml up -d
```

## 2.3. Команди для демонстрації на захисті

```bash
# === AZURE CLI ===

# Перевірка підключення до Azure
az account show --query "{Name:name, User:user.name}" -o table

# Список ресурсів у групі
az resource list -g odaa-rg -o table

# Інформація про VM
az vm show -g odaa-rg --name odaa-vm -o table

# Публічна IP-адреса
az vm show -g odaa-rg --name odaa-vm --show-details --query publicIps -o tsv

# === SSH на сервер ===

# Підключення
ssh azureuser@104.46.15.0

# Статус Docker
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Логи cloud-init
sudo cat /var/log/cloud-init-output.log | tail -50

# === Перевірка сервісів ===

# Health check
curl http://104.46.15.0:8080/health

# Prometheus
curl http://104.46.15.0:9090/-/ready

# Grafana
curl http://104.46.15.0:3000/api/health
```

---

# 📚 ЧАСТИНА 3: ПИТАННЯ ДЛЯ ЗАХИСТУ

## 🔴 Базові питання (обов'язково знати)

### 1. Що таке Infrastructure as Code?
**Відповідь:** IaC — це підхід до управління інфраструктурою через код замість ручних дій. Інфраструктура описується у файлах (YAML, JSON, HCL), версіонується в Git, автоматично застосовується. Переваги: відтворюваність, консистентність, аудит змін.

### 2. Що таке Azure Resource Group?
**Відповідь:** Resource Group — це логічний контейнер для ресурсів Azure. Всі ресурси (VM, мережі, IP) належать якійсь групі. При видаленні групи видаляються всі ресурси всередині. Це спрощує управління та білінг.

### 3. Що таке cloud-init і коли він виконується?
**Відповідь:** Cloud-init — це інструмент автоматичної ініціалізації VM при першому запуску. Він виконується ОДИН раз при створенні VM. Дозволяє встановлювати пакети, виконувати команди, створювати файли. Передається через `--custom-data` в Azure CLI.

### 4. Що таке NSG (Network Security Group)?
**Відповідь:** NSG — це фаєрвол рівня Azure, який фільтрує мережевий трафік. Містить правила з пріоритетами. Наприклад, правило AllowSSH з пріоритетом 100 дозволяє вхідні з'єднання на порт 22.

### 5. Яка різниця між публічною та приватною IP?
**Відповідь:** 
- **Публічна IP** — доступна з інтернету, потрібна для SSH та веб-доступу
- **Приватна IP** — доступна тільки всередині VNet (наприклад, 10.0.1.4)

## 🟡 Середні питання

### 6. Чому ви обрали Standard_D2s_v3 для VM?
**Відповідь:** Це оптимальний розмір для Docker-проєкту з моніторингом:
- 2 vCPU — достатньо для декількох контейнерів
- 8 GB RAM — потрібно для Prometheus, Grafana, застосунку
- SSD диск — швидкий I/O для Docker
- Менші розміри (B1s, B2s) не мали достатньо пам'яті

### 7. Як перевірити статус cloud-init?
**Відповідь:**
```bash
# Статус виконання
cloud-init status
# Повинно бути: status: done

# Детальні логи
sudo cat /var/log/cloud-init-output.log

# Аналіз часу виконання
sudo cloud-init analyze blame
```

### 8. Що станеться якщо видалити Resource Group?
**Відповідь:** При видаленні Resource Group каскадно видаляються ВСІ ресурси всередині: VM, мережі, IP, диски. Це зручно для очищення тестових середовищ. Команда: `az group delete --name odaa-rg --yes`

### 9. Як працює SSH автентифікація?
**Відповідь:** 
1. При `--generate-ssh-keys` Azure створює пару ключів
2. Публічний ключ копіюється на VM в `~/.ssh/authorized_keys`
3. Приватний ключ залишається на локальній машині
4. При підключенні сервер перевіряє підпис приватним ключем

### 10. Навіщо потрібен VNet та Subnet?
**Відповідь:**
- **VNet (Virtual Network)** — ізольована мережа в Azure, визначає address space (10.0.0.0/16)
- **Subnet** — сегмент VNet, де розміщуються ресурси (10.0.1.0/24)
- Дозволяє контролювати мережеву ізоляцію та маршрутизацію

## 🟢 Складні питання

### 11. Порівняйте Azure CLI та Terraform. Коли що використовувати?
**Відповідь:**
| Аспект | Azure CLI | Terraform |
|--------|-----------|-----------|
| Тип | Імперативний | Декларативний |
| State | Немає | Зберігає стан |
| Multi-cloud | Тільки Azure | AWS, GCP, Azure |
| Складність | Проста | Складніша |
| **Коли:** | Швидкі тести, навчання | Продакшн, складна інфраструктура |

### 12. Як забезпечити ідемпотентність при використанні Azure CLI?
**Відповідь:** Azure CLI імперативний, тому потрібно:
1. Перевіряти існування ресурсів перед створенням
2. Використовувати `--only-show-errors` для ігнорування "вже існує"
3. Або переходити на Terraform/Bicep для декларативного підходу

### 13. Що таке User Data vs Custom Data в Azure?
**Відповідь:**
- **Custom Data (cloud-init)** — виконується один раз при першому запуску
- **User Data** — доступні для VM, але не виконуються автоматично
- Для автоматизації використовуємо Custom Data з cloud-init

### 14. Як масштабувати це рішення?
**Відповідь:**
1. **Vertical scaling** — збільшити розмір VM (D4s_v3)
2. **Horizontal scaling** — Load Balancer + кілька VM
3. **Azure Container Instances** — без управління VM
4. **Azure Kubernetes Service** — для великих проєктів

### 15. Які проблеми безпеки в цьому рішенні?
**Відповідь:**
1. SSH відкритий для всіх (0.0.0.0/0) — краще обмежити IP
2. HTTP замість HTTPS — потрібен TLS сертифікат
3. Grafana admin/admin — потрібен сильний пароль
4. Немає Azure Key Vault для секретів

---

# 📚 ЧАСТИНА 4: ДЕМОНСТРАЦІЯ НА ЗАХИСТІ

## Чек-лист для демонстрації:

### 1. Azure Portal (5 хв)
- [ ] Показати Resource Group з ресурсами
- [ ] Показати VM та її параметри
- [ ] Показати NSG з правилами
- [ ] Показати публічну IP-адресу

### 2. Термінал (5 хв)
- [ ] `az account show` — підтвердити авторизацію
- [ ] `az vm show -g odaa-rg --name odaa-vm` — інформація про VM
- [ ] `ssh azureuser@<IP>` — підключитися до VM
- [ ] `docker ps` — показати запущені контейнери
- [ ] `cloud-init status` — показати статус

### 3. Веб-інтерфейси (3 хв)
- [ ] http://IP:8080 — веб-застосунок
- [ ] http://IP:9090 — Prometheus
- [ ] http://IP:3000 — Grafana

### 4. Код (2 хв)
- [ ] `infra/azure-deploy.ps1` — показати скрипт
- [ ] `infra/cloud-init.yaml` — показати конфігурацію

---

# 📚 ЧАСТИНА 5: ГЛОСАРІЙ

| Термін | Визначення |
|--------|------------|
| **IaC** | Infrastructure as Code — інфраструктура описана як код |
| **Azure CLI** | Command Line Interface для управління Azure |
| **Resource Group** | Логічний контейнер для ресурсів Azure |
| **VNet** | Virtual Network — ізольована мережа |
| **Subnet** | Сегмент мережі всередині VNet |
| **NSG** | Network Security Group — фаєрвол Azure |
| **NIC** | Network Interface Card — мережевий адаптер |
| **VM** | Virtual Machine — віртуальний сервер |
| **cloud-init** | Інструмент ініціалізації VM при першому запуску |
| **SSH** | Secure Shell — протокол віддаленого доступу |
| **Public IP** | IP-адреса доступна з інтернету |
| **Custom Data** | Дані передані VM при створенні (cloud-init) |

---

**Дата створення:** 29 квітня 2026
**Автор:** GitHub Copilot для Лабораторної роботи №4
