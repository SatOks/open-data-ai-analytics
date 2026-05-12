# Лабораторна робота №6

## Тема: GitOps з ArgoCD та Kubernetes (k3s) в Azure

**Дата виконання:** 13 травня 2026 р.

---

## Мета роботи

Навчитися:
- розгортати Kubernetes-кластер на базі k3s в хмарному середовищі Azure
- встановлювати та конфігурувати ArgoCD для GitOps
- створювати декларативні описи застосунків у Kubernetes
- організовувати автоматичне розгортання через GitOps workflow
- виконувати rollback через систему контролю версій

---

## Виконані завдання

### Частина 1. Розгортання Kubernetes кластера (k3s)

#### Встановлення k3s на Azure VM:

```bash
# Встановлення k3s
curl -sfL https://get.k3s.io | sh -

# Налаштування kubectl
sudo mkdir -p /home/azureuser/.kube
sudo cp /etc/rancher/k3s/k3s.yaml /home/azureuser/.kube/config
sudo chown -R azureuser:azureuser /home/azureuser/.kube
export KUBECONFIG=/home/azureuser/.kube/config
```

#### Результат:
```
NAME      STATUS   ROLES           AGE   VERSION
odaa-vm   Ready    control-plane   22m   v1.35.4+k3s1
```

### Частина 2. Встановлення ArgoCD

#### Встановлення через офіційні маніфести:

```bash
# Створення namespace
kubectl create namespace argocd

# Застосування маніфестів ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Зміна типу сервісу на NodePort
kubectl patch svc argocd-server -n argocd --type=json \
  -p='[{"op": "replace", "path": "/spec/type", "value": "NodePort"}]'
```

#### Компоненти ArgoCD:
| Компонент | Призначення |
|-----------|-------------|
| argocd-server | Web UI та API сервер |
| argocd-repo-server | Клонування та кешування Git репозиторіїв |
| argocd-application-controller | Синхронізація стану кластера з Git |
| argocd-dex-server | Аутентифікація (SSO) |
| argocd-redis | Кешування |
| argocd-notifications-controller | Сповіщення |

#### Доступ до ArgoCD UI:
- **URL:** https://104.46.15.0:32756
- **Username:** admin
- **Password:** (отримано через `kubectl -n argocd get secret argocd-initial-admin-secret`)

### Частина 3. Kubernetes маніфести для GitOps

#### Структура k8s/:
```
k8s/
├── namespace.yaml        # Namespace odaa
├── deployment.yaml       # Deployment з nginx + initContainer
├── service.yaml          # NodePort сервіс (:30088)
└── argocd-application.yaml  # ArgoCD Application resource
```

#### deployment.yaml (ключові елементи):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: odaa-web
  namespace: odaa
spec:
  replicas: 2
  template:
    spec:
      initContainers:
        - name: init-html
          image: busybox
          command: ["/bin/sh", "-c", "cat > /html/index.html << 'EOF' ..."]
      containers:
        - name: web
          image: nginx:alpine
          ports:
            - containerPort: 80
```

#### argocd-application.yaml:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: odaa-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/SatOks/open-data-ai-analytics.git
    targetRevision: main
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: odaa
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Частина 4. Тестування Auto-Sync

#### Процес оновлення через GitOps:

1. **Зміна версії в deployment.yaml:**
   ```yaml
   <p class="version">Version: v1.1.0</p>  # було v1.0.0
   ```

2. **Commit та push:**
   ```bash
   git commit -m "feat: bump version to v1.1.0"
   git push
   ```

3. **ArgoCD автоматично синхронізує зміни:**
   - Виявляє розбіжність між Git і кластером
   - Застосовує нові маніфести
   - Виконує rolling update deployment

4. **Результат:**
   ```
   NAME       SYNC STATUS   HEALTH STATUS
   odaa-app   Synced        Healthy
   ```

### Частина 5. Тестування Rollback

#### GitOps Rollback через git revert:

```bash
# Відкат останнього коміту
git revert HEAD --no-edit
git push
```

#### Результат:
- ArgoCD автоматично синхронізувався
- Версія повернулась до v1.0.0
- Pods перестворені з новою конфігурацією

#### Kubernetes Rollback (для екстрених випадків):
```bash
# Перегляд історії
kubectl rollout history deployment/odaa-web -n odaa

# Відкат до конкретної ревізії
kubectl rollout undo deployment/odaa-web -n odaa --to-revision=3
```
**Примітка:** При увімкненому selfHeal ArgoCD повертає стан до Git-версії.

---

## Архітектура рішення

```
┌─────────────────────────────────────────────────────────────┐
│                       GitHub Repository                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ k8s/                                                 │    │
│  │   ├── namespace.yaml                                 │    │
│  │   ├── deployment.yaml                                │    │
│  │   ├── service.yaml                                   │    │
│  │   └── argocd-application.yaml                        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ git push (webhook/poll)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Azure VM (odaa-vm)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  k3s Kubernetes Cluster               │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │            ArgoCD (namespace: argocd)            │ │   │
│  │  │  • argocd-server (UI :32756)                     │ │   │
│  │  │  • argocd-repo-server                            │ │   │
│  │  │  • argocd-application-controller                 │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                         │                             │   │
│  │                         │ sync                        │   │
│  │                         ▼                             │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │         Application (namespace: odaa)            │ │   │
│  │  │  • odaa-web deployment (2 replicas)              │ │   │
│  │  │  • odaa-web service (NodePort :30088)            │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Налаштування мережі

### Azure NSG правила:

| Порт | Призначення | Priority |
|------|-------------|----------|
| 22 | SSH доступ | 300 |
| 8080 | Docker web app | 400 |
| 3000 | Grafana | 410 |
| 9090 | Prometheus | 420 |
| 32756 | ArgoCD UI | 500 |
| 30088 | K8s Application | 510 |

---

## Доступні ендпоінти

| Сервіс | URL | Опис |
|--------|-----|------|
| ArgoCD UI | https://104.46.15.0:32756 | GitOps dashboard |
| ODAA App | http://104.46.15.0:30088 | Kubernetes deployment |
| Prometheus | http://104.46.15.0:9090 | Моніторинг (Docker) |
| Grafana | http://104.46.15.0:3000 | Візуалізація (Docker) |

---

## Висновки

В результаті виконання лабораторної роботи:

1. **Розгорнуто Kubernetes кластер** на базі k3s в Azure VM
2. **Встановлено ArgoCD** для реалізації GitOps підходу
3. **Створено декларативні маніфести** для Kubernetes deployment
4. **Налаштовано автоматичну синхронізацію** між GitHub і кластером
5. **Протестовано auto-sync** при зміні версії застосунку
6. **Протестовано rollback** через git revert

GitOps підхід забезпечує:
- Версіонування інфраструктури в Git
- Автоматичне відновлення після збоїв (self-healing)
- Аудит змін через Git history
- Простий rollback через git revert

---

## Використані технології

- **k3s** - легкий Kubernetes дистрибутив
- **ArgoCD** - GitOps continuous delivery tool
- **nginx** - веб-сервер для застосунку
- **Azure** - хмарна платформа
- **GitHub** - система контролю версій

Моніторинг критично важливий для DevOps, оскільки дозволяє:
- Вчасно виявляти проблеми до того, як вони стануть критичними
- Аналізувати тренди та планувати масштабування
- Проводити post-mortem аналіз інцидентів
- Демонструвати SLA метрики

---

**Дата створення звіту:** 12 травня 2026
