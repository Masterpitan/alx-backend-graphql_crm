#!/bin/bash
# Script to delete customers with no orders in the last year

PROJECT_DIR="/path/to/alx-backend-graphql_crm/alx_backend_graphql_crm"
PYTHON_BIN="$PROJECT_DIR/../myenv/Scripts/python"   # adjust if different venv path
MANAGE_PY="$PROJECT_DIR/manage.py"
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Run Django shell command to delete inactive customers
DELETED_COUNT=$($PYTHON_BIN $MANAGE_PY shell -c "
import datetime
from crm.models import Customer

one_year_ago = datetime.date.today() - datetime.timedelta(days=365)
inactive_customers = Customer.objects.filter(orders__isnull=True, created_at__lt=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log the result with timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $DELETED_COUNT inactive customers" >> "$LOG_FILE"
