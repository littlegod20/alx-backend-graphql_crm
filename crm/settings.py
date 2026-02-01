"""
CRM App Settings
App-specific configurations for the CRM application

Note: django_crontab is configured in the main settings.py (alx_backend_graphql_crm/settings.py)
and must be in INSTALLED_APPS for cron jobs to work.
"""

# CRM Model Settings
CRM_SETTINGS = {
    # Customer settings
    'CUSTOMER': {
        'NAME_MAX_LENGTH': 100,
        'EMAIL_MAX_LENGTH': 255,
        'PHONE_MAX_LENGTH': 20,
    },
    
    # Product settings
    'PRODUCT': {
        'NAME_MAX_LENGTH': 255,
        'PRICE_MAX_DIGITS': 10,
        'PRICE_DECIMAL_PLACES': 2,
        'DEFAULT_STOCK': 0,
    },
    
    # Order settings
    'ORDER': {
        'TOTAL_AMOUNT_MAX_DIGITS': 10,
        'TOTAL_AMOUNT_DECIMAL_PLACES': 2,
    },
}

# GraphQL Query/Mutation Settings
GRAPHQL_SETTINGS = {
    'PAGINATION_DEFAULT_PAGE_SIZE': 20,
    'PAGINATION_MAX_PAGE_SIZE': 100,
}

# Cron Job Settings
CRON_SETTINGS = {
    'HEARTBEAT_LOG_FILE': '/tmp/crm_heartbeat_log.txt',
    'CUSTOMER_CLEANUP_LOG_FILE': '/tmp/customer_cleanup_log.txt',
    'ORDER_REMINDERS_LOG_FILE': '/tmp/order_reminders_log.txt',
    'INACTIVE_CUSTOMER_DAYS': 365,  # Days before considering customer inactive
    'ORDER_REMINDER_DAYS': 7,  # Days to look back for order reminders
    'DJANGO_CRONTAB_ENABLED': True,  # Flag to indicate django_crontab is configured
}

# Validation Settings
VALIDATION_SETTINGS = {
    'PHONE_PATTERNS': [
        r'^\+\d{10,15}$',  # International format: +1234567890
        r'^\d{3}-\d{3}-\d{4}$',  # US format: 123-456-7890
    ],
    'LOW_STOCK_THRESHOLD': 10,  # Products with stock below this are considered low stock
}

# GraphQL Endpoint
GRAPHQL_ENDPOINT = 'http://localhost:8000/graphql'
