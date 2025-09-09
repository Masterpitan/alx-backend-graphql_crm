import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.db import transaction
from graphql import GraphQLError


# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")


# ====================
# Mutations
# ====================

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise GraphQLError("Email already exists")

        customer = Customer(name=name, email=email, phone=phone or "")
        customer.full_clean()  # triggers validators
        customer.save()

        return CreateCustomer(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(
            graphene.NonNull(lambda: BulkCustomerInput), required=True
        )

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, customers):
        created_customers = []
        errors = []

        for data in customers:
            try:
                customer = Customer(name=data.name, email=data.email, phone=data.phone or "")
                customer.full_clean()
                customer.save()
                created_customers.append(customer)
            except Exception as e:
                errors.append(f"{data.email}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class BulkCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise GraphQLError("Price must be positive")
        if stock < 0:
            raise GraphQLError("Stock cannot be negative")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise GraphQLError("Invalid customer ID")

        if not product_ids:
            raise GraphQLError("At least one product must be selected")

        products = Product.objects.filter(id__in=product_ids)
        if len(products) != len(product_ids):
            raise GraphQLError("Some product IDs are invalid")

        order = Order(customer=customer)
        order.save()
        order.products.set(products)
        order.calculate_total()

        return CreateOrder(order=order)


# ====================
# Root Mutation + Query
# ====================

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()
