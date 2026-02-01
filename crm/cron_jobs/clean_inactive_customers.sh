#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Change to project directory
cd "$PROJECT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
fi

# Execute Python command to delete inactive customers
python manage.py shell << 'EOF'
import os
import django
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Max

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Order

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders since a year ago
# Customers who either have no orders at all, or their most recent order was more than a year ago
customers_to_delete = Customer.objects.annotate(
    last_order_date=Max('orders__order_date')
).filter(
    Q(orders__isnull=True) | Q(last_order_date__lt=one_year_ago)
).distinct()

# Count before deletion
count = customers_to_delete.count()

# Delete the customers
customers_to_delete.delete()

# Log the result
log_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Deleted {count} inactive customer(s) with no orders since {one_year_ago.strftime('%Y-%m-%d')}\n"

with open('/tmp/customer_cleanup_log.txt', 'a') as f:
    f.write(log_message)

print(f"Deleted {count} inactive customer(s)")
EOF
