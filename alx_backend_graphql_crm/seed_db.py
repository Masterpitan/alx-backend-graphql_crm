import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product

def seed():
    Customer.objects.all().delete()
    Product.objects.all().delete()

    Customer.objects.create(name="Adepitan", email="akoredeadetunji93@gmail.com", phone="+2348160033932")
    Customer.objects.create(name="Adetunji", email="adepitanadetunji93@gmail.com")

    Product.objects.create(name="Laptop", price=999.99, stock=5)
    Product.objects.create(name="Phone", price=499.99, stock=10)

    print("Database seeded!")

if __name__ == "__main__":
    seed()
