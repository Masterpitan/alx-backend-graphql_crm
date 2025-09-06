from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
import datetime
from crm.models import Customer

def clean_inactive_customers():
    cutoff = timezone.now() - datetime.timedelta(days=365)
    qs = Customer.objects.filter(order__isnull=True, created_at__lt=cutoff)
    count = qs.count()
    qs.delete()
    print(f"Deleted {count} inactive customers")

def start():
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.add_job(
        clean_inactive_customers,
        trigger="cron",
        day_of_week="sun", hour=2, minute=0,  # Sundays at 2:00 AM
        id="clean_inactive_customers",
        replace_existing=True,
    )
    scheduler.start()
