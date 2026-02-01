"""
Cron jobs for CRM application
"""
import os
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    """
    Logs a heartbeat message to confirm CRM application health.
    Optionally queries the GraphQL hello field to verify endpoint is responsive.
    """
    # Format: DD/MM/YYYY-HH:MM:SS
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    message = f"{timestamp} CRM is alive\n"
    
    # Log to file (append mode)
    log_file = '/tmp/crm_heartbeat_log.txt'
    try:
        with open(log_file, 'a') as f:
            f.write(message)
        
        # Optionally query GraphQL hello field to verify endpoint is responsive
        try:
            graphql_endpoint = "http://localhost:8000/graphql"
            transport = RequestsHTTPTransport(url=graphql_endpoint)
            client = Client(transport=transport, fetch_schema_from_transport=False)
            
            query = gql("""
                query {
                    hello
                }
            """)
            
            result = client.execute(query)
            hello_response = result.get('hello', 'N/A')
            
            # Log GraphQL response
            graphql_message = f"{timestamp} GraphQL endpoint responsive: {hello_response}\n"
            with open(log_file, 'a') as f:
                f.write(graphql_message)
        except Exception as e:
            # Log GraphQL error but don't fail the heartbeat
            error_message = f"{timestamp} GraphQL endpoint check failed: {str(e)}\n"
            with open(log_file, 'a') as f:
                f.write(error_message)
    except Exception as e:
        # If file writing fails, this is a critical error
        # In production, you might want to send an alert here
        print(f"Error writing heartbeat log: {str(e)}")


def update_low_stock():
    """
    Executes the UpdateLowStockProducts mutation via GraphQL endpoint
    and logs updated product names and new stock levels.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_file = '/tmp/low_stock_updates_log.txt'
    
    try:
        # Create GraphQL client
        graphql_endpoint = "http://localhost:8000/graphql"
        transport = RequestsHTTPTransport(url=graphql_endpoint)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # GraphQL mutation to update low stock products
        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    products {
                        id
                        name
                        stock
                    }
                    message
                }
            }
        """)
        
        # Execute mutation
        result = client.execute(mutation)
        update_result = result.get('updateLowStockProducts', {})
        products = update_result.get('products', [])
        message = update_result.get('message', 'N/A')
        
        # Log the results
        log_entries = []
        log_entries.append(f"[{timestamp}] {message}\n")
        
        if products:
            for product in products:
                product_name = product.get('name', 'N/A')
                product_stock = product.get('stock', 'N/A')
                log_entries.append(f"[{timestamp}] Updated product: {product_name}, New stock level: {product_stock}\n")
        else:
            log_entries.append(f"[{timestamp}] No products with low stock found\n")
        
        # Write to log file
        with open(log_file, 'a') as f:
            f.writelines(log_entries)
        
    except Exception as e:
        # Log error
        error_message = f"[{timestamp}] Error updating low stock products: {str(e)}\n"
        with open(log_file, 'a') as f:
            f.write(error_message)
        print(f"Error updating low stock products: {str(e)}")
