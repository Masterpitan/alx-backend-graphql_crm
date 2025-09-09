import re
import decimal
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

# --------------------
# GraphQL Types
# --------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (relay.Node,)   # 🔹 Add this
        filter_fields = []


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (relay.Node,)   # 🔹 Add this
        filter_fields = []


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (relay.Node,)   # 🔹 Add this
        filter_fields = []


# --------------------
# Input Types
# --------------------
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(default_value=0)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.String()  # optional


# --------------------
# Mutations
# --------------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        # Email uniqueness check
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")

        # Phone validation
        if input.phone:
            phone_pattern = re.compile(r"^\+?\d{7,15}$|^\d{3}-\d{3}-\d{4}$")
            if not phone_pattern.match(input.phone):
                raise Exception("Invalid phone format")

        customer = Customer.objects.create(
            name=input.name, email=input.email, phone=input.phone
        )
        return CreateCustomer(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for idx, cust in enumerate(input):
                try:
                    if Customer.objects.filter(email=cust.email).exists():
                        raise Exception(f"Email {cust.email} already exists")

                    if cust.phone:
                        phone_pattern = re.compile(r"^\+?\d{7,15}$|^\d{3}-\d{3}-\d{4}$")
                        if not phone_pattern.match(cust.phone):
                            raise Exception(f"Invalid phone format: {cust.phone}")

                    customer = Customer.objects.create(
                        name=cust.name, email=cust.email, phone=cust.phone
                    )
                    created_customers.append(customer)
                except Exception as e:
                    errors.append(f"Row {idx+1}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")
        if input.stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product.objects.create(
            name=input.name, price=decimal.Decimal(input.price), stock=input.stock
        )
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        if not input.product_ids:
            raise Exception("At least one product must be selected")

        products = Product.objects.filter(id__in=input.product_ids)
        if products.count() != len(input.product_ids):
            raise Exception("One or more product IDs are invalid")

        total_amount = sum([p.price for p in products])

        order = Order.objects.create(customer=customer, total_amount=total_amount)
        order.products.set(products)
        return CreateOrder(order=order)


# --------------------
# Mutation Class
# --------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


# --------------------
# Query (minimal for now)
# --------------------
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)
# UpdateLowStockProducts, 10, from crm.models import Product
