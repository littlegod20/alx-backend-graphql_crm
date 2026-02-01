"""
Celery tasks for CRM application
"""
import requests
from celery import shared_task
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report using GraphQL queries.
    Fetches total customers, orders, and revenue.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_file = '/tmp/crm_report_log.txt'
    
    try:
        # Create GraphQL client
        graphql_endpoint = "http://localhost:8000/graphql"
        transport = RequestsHTTPTransport(url=graphql_endpoint)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # GraphQL query to get total customers
        customers_query = gql("""
            query {
                customers {
                    id
                }
            }
        """)
        
        # GraphQL query to get total orders and revenue
        orders_query = gql("""
            query {
                orders {
                    id
                    totalAmount
                }
            }
        """)
        
        # Execute queries
        customers_result = client.execute(customers_query)
        orders_result = client.execute(orders_query)
        
        # Extract data
        customers = customers_result.get('customers', [])
        orders = orders_result.get('orders', [])
        
        total_customers = len(customers)
        total_orders = len(orders)
        
        # Calculate total revenue
        total_revenue = sum(
            float(order.get('totalAmount', 0)) 
            for order in orders 
            if order.get('totalAmount')
        )
        
        # Format revenue to 2 decimal places
        total_revenue_formatted = f"{total_revenue:.2f}"
        
        # Create report message
        report_message = (
            f"{timestamp} - Report: {total_customers} customers, "
            f"{total_orders} orders, {total_revenue_formatted} revenue\n"
        )
        
        # Log to file
        with open(log_file, 'a') as f:
            f.write(report_message)
        
        return {
            'customers': total_customers,
            'orders': total_orders,
            'revenue': total_revenue
        }
        
    except Exception as e:
        # Log error
        error_message = f"{timestamp} - Error generating CRM report: {str(e)}\n"
        with open(log_file, 'a') as f:
            f.write(error_message)
        raise
