import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from decimal import Decimal
import re
from .models import Customer, Product, Order


# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ('id', 'name', 'email', 'phone', 'created_at', 'updated_at')


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'stock', 'created_at', 'updated_at')


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ('id', 'customer', 'products', 'total_amount', 'order_date', 'created_at', 'updated_at')


# Input Types
class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class BulkCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# Response Types
class CreateCustomerResponse(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    message = graphene.String()


class BulkCreateCustomersResponse(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)


class CreateProductResponse(graphene.ObjectType):
    product = graphene.Field(ProductType)


class CreateOrderResponse(graphene.ObjectType):
    order = graphene.Field(OrderType)


# Validation helpers
def validate_phone(phone):
    """Validate phone format: +1234567890 or 123-456-7890"""
    if not phone:
        return True, None
    pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
    if re.match(pattern, phone):
        return True, None
    return False, "Phone must be in format +1234567890 or 123-456-7890"


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    Output = CreateCustomerResponse

    def mutate(self, info, input):
        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")

        # Validate phone format
        if input.phone:
            is_valid, error_msg = validate_phone(input.phone)
            if not is_valid:
                raise Exception(error_msg)

        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone or ""
        )

        return CreateCustomerResponse(
            customer=customer,
            message="Customer created successfully"
        )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(BulkCustomerInput, required=True)

    Output = BulkCreateCustomersResponse

    @transaction.atomic
    def mutate(self, info, input):
        customers = []
        errors = []

        for idx, customer_data in enumerate(input):
            try:
                # Validate email uniqueness
                if Customer.objects.filter(email=customer_data.email).exists():
                    errors.append(f"Row {idx + 1}: Email '{customer_data.email}' already exists")
                    continue

                # Validate phone format
                if customer_data.phone:
                    is_valid, error_msg = validate_phone(customer_data.phone)
                    if not is_valid:
                        errors.append(f"Row {idx + 1}: {error_msg}")
                        continue

                customer = Customer.objects.create(
                    name=customer_data.name,
                    email=customer_data.email,
                    phone=customer_data.phone or ""
                )
                customers.append(customer)
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")

        return BulkCreateCustomersResponse(
            customers=customers,
            errors=errors
        )


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    Output = CreateProductResponse

    def mutate(self, info, input):
        # Validate price is positive
        if input.price <= 0:
            raise Exception("Price must be positive")

        # Validate stock is non-negative
        stock = input.stock if input.stock is not None else 0
        if stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=stock
        )

        return CreateProductResponse(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    Output = CreateOrderResponse

    def mutate(self, info, input):
        # Validate customer exists
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception(f"Invalid customer ID: {input.customer_id}")

        # Validate at least one product
        if not input.product_ids or len(input.product_ids) == 0:
            raise Exception("At least one product must be selected")

        # Validate all products exist
        products = []
        for product_id in input.product_ids:
            try:
                product = Product.objects.get(pk=product_id)
                products.append(product)
            except Product.DoesNotExist:
                raise Exception(f"Invalid product ID: {product_id}")

        # Calculate total amount
        total_amount = sum(product.price for product in products)

        # Create order
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount
        )
        order.products.set(products)

        return CreateOrderResponse(order=order)


# Query class (if needed for queries)
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    customer = graphene.Field(CustomerType, id=graphene.ID())
    products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.ID())
    orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.ID())

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_orders(self, info):
        return Order.objects.all()

    def resolve_order(self, info, id):
        try:
            return Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return None


# Mutation class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
