Great objective 👌 — let’s implement your **Celery + Celery Beat weekly CRM report** step by step.

---

## 1. **Install Dependencies**

In `requirements.txt`, add:

```
celery
django-celery-beat
redis
```

Install:

```bash
pip install celery django-celery-beat redis
```

---

## 2. **Enable Celery in Django**

### `crm/settings.py`

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'django_celery_beat',
]
```

Add Celery configuration:

```python
from celery.schedules import crontab

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),  # every Monday at 6 AM
    },
}
```

---

### `crm/celery.py`

```python
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")

app = Celery("crm")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

---

### `crm/__init__.py`

```python
from .celery import app as celery_app

__all__ = ("celery_app",)
```

---

## 3. **Define the Celery Task**

Create **crm/tasks.py**:

```python
import datetime
import requests
from celery import shared_task

@shared_task
def generate_crm_report():
    log_file = "/tmp/crm_report_log.txt"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query = """
    {
        totalCustomers
        totalOrders
        totalRevenue
    }
    """

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": query},
            timeout=10
        )
        data = response.json().get("data", {})

        customers = data.get("totalCustomers", 0)
        orders = data.get("totalOrders", 0)
        revenue = data.get("totalRevenue", 0)

        message = f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue"

    except Exception as e:
        message = f"{timestamp} - Error generating report: {str(e)}"

    with open(log_file, "a") as f:
        f.write(message + "\n")

    return message
```

⚠️ **Note**: For this to work, your GraphQL schema must have fields like `totalCustomers`, `totalOrders`, `totalRevenue`. If they don’t exist yet, you’ll need to define resolvers in your `schema.py`.

---

## 4. **Run Celery + Beat**

Run database migrations (Celery Beat needs tables):

```bash
python manage.py migrate
```

Start Redis server (in another terminal):

```bash
redis-server
```

Start Celery worker:

```bash
celery -A crm worker -l info
```

Start Celery Beat:

```bash
celery -A crm beat -l info
```

---

## 5. **Documentation**

Create **crm/README.md**:

````markdown
# CRM Celery Beat Setup

## Requirements
- Redis
- Celery
- Django-Celery-Beat

## Setup
1. Install dependencies:
   ```bash
   pip install celery django-celery-beat redis
````

2. Run migrations:

   ```bash
   python manage.py migrate
   ```

3. Start Redis:

   ```bash
   redis-server
   ```

4. Start Celery worker:

   ```bash
   celery -A crm worker -l info
   ```

5. Start Celery Beat:

   ```bash
   celery -A crm beat -l info
   ```

6. Verify logs at:

   ```
   /tmp/crm_report_log.txt
   ```

Each Monday at 6 AM, the system will generate a report summarizing:

* Total customers
* Total orders
* Total revenue

```
