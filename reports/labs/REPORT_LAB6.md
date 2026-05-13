# Звіт з виконання Лабораторної роботи №6

## Тема
Ознайомлення із практиками GitOps. Автоматизоване розгортання застосунку в Kubernetes за допомогою Argo CD.

## Мета
Ознайомитися з підходом GitOps і реалізувати автоматичне розгортання та оновлення застосунку в Kubernetes-середовищі на основі змін у GitHub-репозиторії.

## Коротко про GitOps
GitOps — це підхід, у якому Git-репозиторій є джерелом істини для бажаного стану системи. Зміни вносяться через `commit/push`, а агент у кластері (у цій роботі — Argo CD) автоматично синхронізує фактичний стан із декларативними YAML-описами в репозиторії.  
Rollback виконується поверненням Git-стану до попереднього коміту.

## Використане середовище
1. Azure Linux VM (`odaa-vm`, IP: `104.46.15.0`).
2. `k3s` як Kubernetes кластер (single-node, v1.35.4+k3s1).
3. Argo CD у namespace `argocd`.
4. GitHub репозиторій: `SatOks/open-data-ai-analytics`.
5. Kubernetes manifests у каталозі `k8s/`.
6. Публічні endpoint-и:
   - Застосунок: `http://104.46.15.0:30088`
   - Argo CD: `https://104.46.15.0:32756`
   - Prometheus: `http://104.46.15.0:9090`
   - Grafana: `http://104.46.15.0:3000`

## Структура GitOps у репозиторії
```text
k8s/
  namespace.yaml
  deployment.yaml
  service.yaml
  argocd-application.yaml
```

## Основні YAML-файли

### `k8s/namespace.yaml`
Створює namespace `odaa` для застосунку.

### `k8s/deployment.yaml`
Описує Deployment `odaa-web`:
1. Image: `nginx:alpine` з initContainer для генерації HTML
2. `replicas: 2`
3. Порт контейнера `80`
4. Labels/selectors для зв'язку з Service
5. `readinessProbe` і `livenessProbe` на `/`

### `k8s/service.yaml`
Створює Service `odaa-web` типу `NodePort`:
1. `port: 80`
2. `targetPort: 80`
3. `nodePort: 30088` (доступ іззовні через IP VM)

### `k8s/argocd-application.yaml`
Argo CD Application `odaa-app`:
1. Репозиторій: `https://github.com/SatOks/open-data-ai-analytics.git`
2. Гілка: `main`
3. Шлях до маніфестів: `k8s`
4. Namespace призначення: `odaa`
5. Автосинхронізація: `automated`, `prune`, `selfHeal`

## Покрокове виконання

### 1. Підготовка Kubernetes-середовища
На Azure VM встановлено `k3s`, перевірено вузол командою:
```bash
kubectl get nodes
```

### 2. Встановлення Argo CD
1. Створено namespace `argocd`.
2. Встановлено Argo CD з офіційного маніфесту.
3. Перевірено роботу pod-ів:
```bash
kubectl -n argocd get pods
```

### 3. Підключення GitHub до Argo CD
Створено `Application` через `k8s/argocd-application.yaml`, увімкнено автоматичну синхронізацію.

### 4. Перше розгортання
Після застосування `Application` Argo CD отримав стан `Synced`, а ресурси застосунку створені в `odaa`.

### 5. Демонстрація автоматичного оновлення
У GitHub змінено версію у `deployment.yaml` (`v1.0.0 -> v1.1.0`), виконано `commit` і `push`.  
Argo CD виконав синхронізацію без ручного `kubectl apply`.

### 6. Демонстрація rollback
Останню зміну скасовано через Git (`git revert HEAD`).  
Argo CD повернув кластер до попередньої конфігурації (`v1.0.0`).

### 7. Сумісність із моніторингом
Після GitOps-оновлень перевірено:
1. Застосунок доступний.
2. Prometheus доступний і продовжує збір метрик.
3. Grafana доступна.
4. Дашборд із Lab 5 працює.

## Приклад commit, що викликав оновлення
```text
30160bc feat: bump version to v1.1.0
```

## Приклад rollback
```text
ed72ff5 Revert "feat: bump version to v1.1.0"
```

## Скріншоти

### Скріншот 1. `kubectl get nodes`

<!-- 
🔧 ЯК ЗРОБИТИ СКРІНШОТ:
1. Підключитись до VM: ssh azureuser@104.46.15.0
2. Виконати команду: export KUBECONFIG=/home/azureuser/.kube/config && kubectl get nodes
3. Зробити скріншот терміналу з результатом
-->

![alt text](image-1.png)

Рис. 1. Активний вузол Kubernetes у k3s-кластері.

### Скріншот 2. Pod-и Argo CD

<!-- 
🔧 ЯК ЗРОБИТИ СКРІНШОТ:
1. Підключитись до VM: ssh azureuser@104.46.15.0
2. Виконати команду: export KUBECONFIG=/home/azureuser/.kube/config && kubectl -n argocd get pods
3. Зробити скріншот терміналу з усіма 7 pod-ами у статусі Running
-->

![alt text](image-2.png)

Рис. 2. Стан pod-ів Argo CD у namespace `argocd`.

### Скріншот 3. Інтерфейс Argo CD зі станом Synced

<!-- 
🔧 ЯК ЗРОБИТИ СКРІНШОТ:
1. Відкрити браузер: https://104.46.15.0:32756
2. Прийняти self-signed certificate
3. Логін: admin
4. Пароль: vE1TQG-5jbU-V2nr
5. Зробити скріншот з Application "odaa-app" у статусі Synced + Healthy
-->

![alt text](image-3.png)

Рис. 3. Стан `Synced` для застосунку `odaa-app`.

### Скріншот 4. Argo CD — Resource Tree

<!-- 
🔧 ЯК ЗРОБИТИ СКРІНШОТ:
1. В ArgoCD UI клікнути на Application "odaa-app"
2. Перейти на вкладку з деревом ресурсів (Resource Tree)
3. Зробити скріншот, де видно: Namespace, Deployment, ReplicaSet, Pods, Service
-->

![alt text](image-4.png)

Рис. 4. Дерево ресурсів застосунку в ArgoCD.

### Скріншот 5. Застосунок у браузері

<!-- 
🔧 ЯК ЗРОБИТИ СКРІНШОТ:
1. Відкрити браузер: http://104.46.15.0:30088
2. Зробити скріншот сторінки з "Open Data AI Analytics" і версією
-->

![alt text](image-5.png)

Рис. 5. Веб-застосунок, розгорнутий у Kubernetes і доступний через NodePort.

### Скріншот 6. Pods застосунку

<!-- 
🔧 ЯК ЗРОБИТИ СКРІНШОТ:
1. Підключитись до VM: ssh azureuser@104.46.15.0
2. Виконати команду: export KUBECONFIG=/home/azureuser/.kube/config && kubectl get pods -n odaa
3. Зробити скріншот терміналу з 2 pod-ами у статусі Running
-->

![alt text](image-6.png)

Рис. 6. Стан pod-ів застосунку у namespace `odaa`.

### Скріншот 7. Commit, що викликав автооновлення

<!-- 
🔧 ЯК ЗРОБИТИ СКРІНШОТ:
1. Відкрити GitHub: https://github.com/SatOks/open-data-ai-analytics/commits/main
2. Знайти коміт "feat: bump version to v1.1.0"
3. Зробити скріншот з комітом
-->

![alt text](image-7.png)

Рис. 7. Коміт у GitHub, після якого Argo CD автоматично синхронізував зміни.

### Скріншот 8. Застосунок після оновлення (v1.1.0)

<!-- 
🔧 ЯК ЗРОБИТИ СКРІНШОТ:
1. Спочатку зробити зміну версії в k8s/deployment.yaml (v1.0.0 → v1.1.0)
2. git add k8s/ && git commit -m "feat: bump version to v1.1.0" && git push
3. Почекати ~60 секунд
4. Відкрити http://104.46.15.0:30088
5. Зробити скріншот з Version: v1.1.0
-->

![alt text](image-8.png)

Рис. 8. Застосунок після автоматичного оновлення через GitOps (версія v1.1.0).

### Скріншот 9. Rollback (Git revert + Argo CD sync)

<!-- 
🔧 ЯК ЗРОБИТИ СКРІНШОТ:
1. Виконати: git revert HEAD --no-edit && git push
2. Почекати ~60 секунд
3. Відкрити http://104.46.15.0:30088
4. Зробити скріншот з Version: v1.0.0 (версія повернулась)
-->

![alt text](image-9.png)

Рис. 9. Повернення до попереднього стану через Git revert і автоматичний rollback у кластері.

### Скріншот 10. Grafana dashboard

<!-- 
🔧 ЯК ЗРОБИТИ СКРІНШОТ:
1. Відкрити браузер: http://104.46.15.0:3000
2. Логін: admin / admin
3. Перейти до дашборду "Open Data AI Analytics Dashboard"
4. Зробити скріншот дашборду
-->

![alt text](image-10.png)

Рис. 10. Дашборд Grafana після GitOps-оновлення застосунку.

## Висновки
У лабораторній роботі реалізовано повний GitOps-сценарій на базі Azure VM + k3s + Argo CD.  
Декларативні конфігурації винесено в GitHub-репозиторій, перше розгортання виконано через Argo CD, підтверджено автоматичне оновлення після зміни в Git і rollback через `git revert`.  
Моніторинг (Prometheus + Grafana) залишився працездатним після GitOps-змін.
