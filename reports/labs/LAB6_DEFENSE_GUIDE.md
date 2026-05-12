# 🎓 Лабораторна робота №6 — Повний гайд для захисту

## Тема: GitOps з ArgoCD та Kubernetes (k3s) в Azure

---

# 📚 ЧАСТИНА 1: ТЕОРЕТИЧНІ ОСНОВИ

## 1.1. Що таке GitOps?

**GitOps** — це підхід до управління інфраструктурою та застосунками, де Git є єдиним джерелом істини (Single Source of Truth).

### Принципи GitOps:

```
┌─────────────────────────────────────────────────────────────┐
│                   ПРИНЦИПИ GITOPS                            │
├─────────────────────────────────────────────────────────────┤
│  1. ДЕКЛАРАТИВНІСТЬ    │  Описуємо бажаний стан, не дії    │
│  2. ВЕРСІОНУВАННЯ      │  Весь стан в Git з історією       │
│  3. АВТОМАТИЗАЦІЯ      │  Зміни застосовуються автоматично │
│  4. САМОВІДНОВЛЕННЯ    │  Система повертається до Git-стану│
└─────────────────────────────────────────────────────────────┘
```

### Переваги GitOps:

| Традиційний підхід | GitOps підхід |
|-------------------|---------------|
| Імперативні команди (kubectl apply) | Декларативний стан в Git |
| Хто і що змінив? Невідомо | Повний audit через git log |
| Rollback — складний процес | Rollback = git revert |
| Drift detection відсутній | ArgoCD постійно перевіряє |

---

## 1.2. ArgoCD — GitOps Controller

### Архітектура ArgoCD:

```
┌────────────────────────────────────────────────────────────┐
│                        ArgoCD                               │
├────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌────────────────────────────────┐  │
│  │   argocd-server  │  │  argocd-application-controller │  │
│  │   (Web UI/API)   │  │  (Sync Controller)              │  │
│  └──────────────────┘  └────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────┐  ┌────────────────────────────────┐  │
│  │ argocd-repo-     │  │  argocd-dex-server              │  │
│  │ server           │  │  (Authentication/SSO)           │  │
│  │ (Git clone/cache)│  └────────────────────────────────┘  │
│  └──────────────────┘                                       │
│                                                             │
│  ┌──────────────────┐  ┌────────────────────────────────┐  │
│  │   argocd-redis   │  │  argocd-notifications-         │  │
│  │   (Cache)        │  │  controller (Alerts)           │  │
│  └──────────────────┘  └────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Ключові концепції:

| Концепція | Опис |
|-----------|------|
| **Application** | Зв'язок між Git repo та Kubernetes namespace |
| **Project** | Логічне групування Applications |
| **Sync** | Приведення кластера до стану в Git |
| **Health** | Статус ресурсів Kubernetes |
| **Refresh** | Перечитування стану з Git |
| **Self-Heal** | Автоматичне відновлення після drift |

---

## 1.3. Kubernetes та k3s

### Чому k3s?

```
┌─────────────────────────────────────────────────────────────┐
│                    k3s vs k8s                                │
├─────────────────────────────────────────────────────────────┤
│  k8s (Kubernetes)           │  k3s (Lightweight K8s)        │
│  ──────────────────         │  ──────────────────────       │
│  • 1+ GB RAM                │  • 512 MB RAM                 │
│  • Складна установка        │  • Один curl команда          │
│  • etcd cluster             │  • SQLite/PostgreSQL          │
│  • Production-ready         │  • Edge/IoT/Dev friendly      │
└─────────────────────────────────────────────────────────────┘
```

### Основні ресурси Kubernetes:

| Ресурс | Призначення |
|--------|-------------|
| **Namespace** | Логічна ізоляція ресурсів |
| **Deployment** | Керування ReplicaSet та Pods |
| **Service** | Мережевий доступ до Pods |
| **Pod** | Мінімальна одиниця виконання |
| **ConfigMap/Secret** | Конфігурація та секрети |

---

# 📋 ЧАСТИНА 2: ПРАКТИЧНА РЕАЛІЗАЦІЯ

## 2.1. Структура проєкту

```
k8s/
├── namespace.yaml          # Namespace "odaa"
├── deployment.yaml         # 2 replicas nginx + initContainer
├── service.yaml            # NodePort :30088
└── argocd-application.yaml # ArgoCD Application resource
```

## 2.2. Ключові файли

### namespace.yaml
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: odaa
```

### deployment.yaml (спрощено)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: odaa-web
  namespace: odaa
spec:
  replicas: 2
  selector:
    matchLabels:
      app: odaa-web
  template:
    spec:
      initContainers:
        - name: init-html
          image: busybox
          command: ["cat > /html/index.html << EOF ..."]
      containers:
        - name: web
          image: nginx:alpine
          ports:
            - containerPort: 80
```

### argocd-application.yaml
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
      prune: true      # Видаляти ресурси, яких немає в Git
      selfHeal: true   # Автоматично відновлювати при drift
```

---

# 🎯 ЧАСТИНА 3: СКРІНШОТИ ДЛЯ ЗАХИСТУ

## 📸 Скріншот 1: ArgoCD UI — Application Dashboard

**URL:** https://104.46.15.0:32756

**Що показати:**
- Зайти в ArgoCD (admin / [password])
- Показати Application "odaa-app"
- Статус: Synced, Healthy

**Що видно на скріншоті:**
```
┌─────────────────────────────────────────────────────────────┐
│  ArgoCD                                    [admin] [logout] │
├─────────────────────────────────────────────────────────────┤
│  Applications                                                │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  odaa-app                                          │     │
│  │  ────────────────────────────────────────────────  │     │
│  │  ✅ Synced       ❤️ Healthy                        │     │
│  │                                                    │     │
│  │  SOURCE: github.com/SatOks/open-data-ai-analytics │     │
│  │  PATH: k8s                                         │     │
│  │  TARGET: main                                      │     │
│  │                                                    │     │
│  │  DESTINATION: https://kubernetes.default.svc      │     │
│  │  NAMESPACE: odaa                                   │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📸 Скріншот 2: ArgoCD — Resource Tree

**Як отримати:**
- Клікнути на Application "odaa-app"
- Перейти на вкладку з деревом ресурсів

**Що видно:**
```
odaa-app
├── Namespace: odaa ✅
├── Deployment: odaa-web ✅
│   └── ReplicaSet: odaa-web-xxx ✅
│       ├── Pod: odaa-web-xxx-abc ✅
│       └── Pod: odaa-web-xxx-def ✅
└── Service: odaa-web ✅
```

---

## 📸 Скріншот 3: Kubernetes Pods

**Команда:**
```bash
kubectl get pods -n odaa
```

**Результат:**
```
NAME                       READY   STATUS    RESTARTS   AGE
odaa-web-8cb9b484-b9spd    1/1     Running   0          10m
odaa-web-8cb9b484-xlhgp    1/1     Running   0          10m
```

---

## 📸 Скріншот 4: Web Application

**URL:** http://104.46.15.0:30088

**Що видно:**
```
┌─────────────────────────────────────────────────────────────┐
│  🚀 Open Data AI Analytics                                   │
│  ─────────────────────────────────────────────────────────  │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Version: v1.0.0                                   │     │
│  │  Deployed via ArgoCD GitOps                        │     │
│  │  Status: Running on Kubernetes (k3s)               │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📸 Скріншот 5: GitOps Auto-Sync (Before/After)

### Крок 1: Зміна версії в Git

**Команди:**
```bash
# Змінити версію в k8s/deployment.yaml
# Version: v1.0.0 → Version: v1.1.0

git add k8s/
git commit -m "feat: bump version to v1.1.0"
git push
```

### Крок 2: ArgoCD автоматично синхронізується

**Що показати:**
1. ArgoCD UI показує "OutOfSync" (на кілька секунд)
2. Потім "Syncing..."
3. Потім "Synced"

### Крок 3: Нова версія на сайті

**URL:** http://104.46.15.0:30088
```
Version: v1.1.0  ← Нова версія!
```

---

## 📸 Скріншот 6: GitOps Rollback

### Крок 1: Rollback через git revert

**Команди:**
```bash
git revert HEAD --no-edit
git push
```

### Крок 2: ArgoCD синхронізується

**ArgoCD UI:**
- Статус змінюється на "Syncing"
- Потім "Synced", "Healthy"

### Крок 3: Версія повернулась

**URL:** http://104.46.15.0:30088
```
Version: v1.0.0  ← Відкат успішний!
```

---

## 📸 Скріншот 7: kubectl status

**Команда:**
```bash
kubectl get all -n odaa
kubectl get applications -n argocd
```

**Результат:**
```
NAME                           READY   STATUS    RESTARTS   AGE
pod/odaa-web-8cb9b484-b9spd    1/1     Running   0          15m
pod/odaa-web-8cb9b484-xlhgp    1/1     Running   0          15m

NAME               TYPE       CLUSTER-IP   EXTERNAL-IP   PORT(S)
service/odaa-web   NodePort   10.43.8.49   <none>        80:30088/TCP

NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/odaa-web   2/2     2            2           15m

NAME       SYNC STATUS   HEALTH STATUS
odaa-app   Synced        Healthy
```

---

# ❓ ЧАСТИНА 4: ПИТАННЯ ДЛЯ ЗАХИСТУ

## Теоретичні питання

### Q: Що таке GitOps?
**A:** GitOps — це підхід до управління інфраструктурою, де Git є єдиним джерелом істини. Всі зміни робляться через Git commits, а спеціальний контролер (ArgoCD) автоматично синхронізує стан кластера з репозиторієм.

### Q: Які переваги GitOps?
**A:**
1. **Версіонування** — вся історія змін в Git
2. **Аудит** — хто, коли, що змінив
3. **Rollback** — простий відкат через git revert
4. **Self-healing** — автоматичне відновлення при drift
5. **Declarative** — описуємо бажаний стан

### Q: Що таке ArgoCD?
**A:** ArgoCD — це GitOps continuous delivery tool для Kubernetes. Він моніторить Git репозиторій і автоматично синхронізує Kubernetes кластер з декларативним описом в Git.

### Q: Що таке k3s?
**A:** k3s — це легкий дистрибутив Kubernetes від Rancher. Він потребує менше ресурсів (512MB RAM), має простішу установку (один curl команда), і підходить для edge, IoT та dev середовищ.

### Q: Як працює self-heal в ArgoCD?
**A:** Коли хтось вручну змінює ресурс в кластері (kubectl edit), ArgoCD виявляє розбіжність (drift) і автоматично повертає ресурс до стану, описаного в Git.

### Q: Як зробити rollback в GitOps?
**A:** Просто `git revert HEAD && git push`. ArgoCD побачить новий commit і автоматично застосує попередню версію маніфестів.

---

## Практичні питання

### Q: Як встановити k3s?
```bash
curl -sfL https://get.k3s.io | sh -
```

### Q: Як встановити ArgoCD?
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Q: Як отримати пароль ArgoCD?
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### Q: Як перевірити статус Application?
```bash
kubectl get applications -n argocd
```

### Q: Як примусово синхронізувати?
```bash
kubectl -n argocd patch application odaa-app --type merge -p '{"operation":{"sync":{}}}'
# Або через UI: натиснути "Sync"
```

---

# 📊 ЧАСТИНА 5: URL ДОСТУПУ

| Сервіс | URL | Credentials |
|--------|-----|-------------|
| ArgoCD UI | https://104.46.15.0:32756 | admin / vE1TQG-5jbU-V2nr |
| ODAA App (K8s) | http://104.46.15.0:30088 | - |
| Prometheus | http://104.46.15.0:9090 | - |
| Grafana | http://104.46.15.0:3000 | admin / admin |

---

# ✅ ЧЕКЛИСТ ПЕРЕД ЗАХИСТОМ

- [ ] ArgoCD UI доступний і показує Application
- [ ] Application статус: Synced + Healthy
- [ ] Web app відкривається на :30088
- [ ] Готові показати git commit → auto-sync
- [ ] Готові показати git revert → rollback
- [ ] Знаю теоретичні питання
- [ ] Знаю kubectl команди
