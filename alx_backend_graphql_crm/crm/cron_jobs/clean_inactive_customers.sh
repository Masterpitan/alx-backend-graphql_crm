#!/bin/bash
# Script to delete customers with no orders in the past year
# Logs the number of deleted customers with timestamp

PROJECT_DIR="$(dirname "$(dirname "$(dirname "$0")")")"
LOG_FILE="/tmp/customer_cleanup_log.txt"

cd "$PROJECT_DIR" || exit 1

# Run Django shell command
DELETED_COUNT=$(python manage.py shell -c "
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta

cutoff_date = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(order__isnull=True, created_at__lt=cutoff_date)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log with timestamp
echo \"\$(date '+%Y-%m-%d %H:%M:%S') - Deleted \$DELETED_COUNT inactive customers\" >> \"$LOG_FILE\"
