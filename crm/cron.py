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
