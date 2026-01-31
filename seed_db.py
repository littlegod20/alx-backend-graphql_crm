"""
Seed script to populate the database with sample data.
Run with: python manage.py shell < seed_db.py
Or: python manage.py runscript seed_db (if using django-extensions)
Or: python seed_db.py (if run as standalone script)
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order
from decimal import Decimal


def seed_database():
    """Populate database with sample data"""
    print("Starting database seeding...")

    # Clear existing data (optional - comment out if you want to keep existing data)
    print("Clearing existing data...")
    Order.objects.all().delete()
    Product.objects.all().delete()
    Customer.objects.all().delete()

    # Create Customers
    print("Creating customers...")
    customers_data = [
        {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol Williams", "email": "carol@example.com", "phone": "+1987654321"},
        {"name": "David Brown", "email": "david@example.com", "phone": "456-789-0123"},
        {"name": "Eva Davis", "email": "eva@example.com"},
    ]

    customers = []
    for data in customers_data:
        customer, created = Customer.objects.get_or_create(
            email=data["email"],
            defaults={
                "name": data["name"],
                "phone": data.get("phone", "")
            }
        )
        customers.append(customer)
        print(f"  {'Created' if created else 'Found'} customer: {customer.name}")

    # Create Products
    print("\nCreating products...")
    products_data = [
        {"name": "Laptop", "price": Decimal("999.99"), "stock": 10},
        {"name": "Mouse", "price": Decimal("29.99"), "stock": 50},
        {"name": "Keyboard", "price": Decimal("79.99"), "stock": 30},
        {"name": "Monitor", "price": Decimal("299.99"), "stock": 15},
        {"name": "Webcam", "price": Decimal("49.99"), "stock": 25},
        {"name": "Headphones", "price": Decimal("129.99"), "stock": 20},
    ]

    products = []
    for data in products_data:
        product, created = Product.objects.get_or_create(
            name=data["name"],
            defaults={
                "price": data["price"],
                "stock": data["stock"]
            }
        )
        products.append(product)
        print(f"  {'Created' if created else 'Found'} product: {product.name} - ${product.price}")

    # Create Orders
    print("\nCreating orders...")
    orders_data = [
        {
            "customer": customers[0],  # Alice
            "products": [products[0], products[1], products[2]],  # Laptop, Mouse, Keyboard
        },
        {
            "customer": customers[1],  # Bob
            "products": [products[3], products[4]],  # Monitor, Webcam
        },
        {
            "customer": customers[2],  # Carol
            "products": [products[5]],  # Headphones
        },
        {
            "customer": customers[0],  # Alice (another order)
            "products": [products[3], products[5]],  # Monitor, Headphones
        },
    ]

    for idx, data in enumerate(orders_data):
        total_amount = sum(product.price for product in data["products"])
        order = Order.objects.create(
            customer=data["customer"],
            total_amount=total_amount
        )
        order.products.set(data["products"])
        print(f"  Created order #{order.id} for {order.customer.name} - ${order.total_amount}")

    print("\nDatabase seeding completed successfully!")
    print(f"\nSummary:")
    print(f"  Customers: {Customer.objects.count()}")
    print(f"  Products: {Product.objects.count()}")
    print(f"  Orders: {Order.objects.count()}")


if __name__ == "__main__":
    seed_database()
