#!/usr/bin/env python3
"""
Order Reminder Script
Queries GraphQL endpoint for orders from the last 7 days and logs reminders.
"""
import os
import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Add project directory to Python path
sys.path.insert(0, PROJECT_DIR)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')

# Import Django after setting environment
import django
django.setup()

from django.utils import timezone

# GraphQL endpoint
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

# Calculate date 7 days ago
seven_days_ago = (timezone.now() - timedelta(days=7)).isoformat()

# GraphQL query to get orders from the last 7 days
query = gql("""
    query GetRecentOrders($orderDateGte: DateTime!) {
        allOrders(filter: { orderDateGte: $orderDateGte }) {
            edges {
                node {
                    id
                    customer {
                        email
                    }
                    orderDate
                }
            }
        }
    }
""")

def send_order_reminders():
    """Query GraphQL for recent orders and log reminders"""
    try:
        # Create GraphQL client
        transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # Execute query
        variables = {
            "orderDateGte": seven_days_ago
        }
        
        result = client.execute(query, variable_values=variables)
        
        # Process results
        orders = result.get('allOrders', {}).get('edges', [])
        
        # Log each order
        log_entries = []
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for edge in orders:
            node = edge.get('node', {})
            order_id = node.get('id')
            customer = node.get('customer', {})
            customer_email = customer.get('email', 'N/A')
            order_date = node.get('orderDate', 'N/A')
            
            log_entry = f"[{timestamp}] Order ID: {order_id}, Customer Email: {customer_email}, Order Date: {order_date}\n"
            log_entries.append(log_entry)
        
        # Write to log file
        log_file = '/tmp/order_reminders_log.txt'
        with open(log_file, 'a') as f:
            if log_entries:
                f.writelines(log_entries)
            else:
                f.write(f"[{timestamp}] No orders found in the last 7 days\n")
        
        print("Order reminders processed!")
        
    except Exception as e:
        # Log error
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_message = f"[{timestamp}] Error processing order reminders: {str(e)}\n"
        with open('/tmp/order_reminders_log.txt', 'a') as f:
            f.write(error_message)
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    send_order_reminders()
