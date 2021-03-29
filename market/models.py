from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    inventory = models.PositiveIntegerField(default=0, null=True)

    def increase_inventory(self, amount):
        pass

    def decrease_inventory(self, amount):
        pass


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    balance = models.PositiveIntegerField(default=20000, null=True)

    def deposit(self, amount):
        pass

    def spend(self, amount):
        pass


class Order(models.Model):
    STATUS_SHOPPING = 1
    STATUS_SUBMITTED = 2
    STATUS_CANCELED = 3
    STATUS_SENT = 4

    status_choices = (
        (STATUS_SHOPPING, "shopping"),
        (STATUS_SUBMITTED, "submitted"),
        (STATUS_CANCELED, "canceled"),
        (STATUS_SENT, "sent"),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_time = models.DateTimeField()
    total_price = models.IntegerField()
    status = models.IntegerField(choices=status_choices)

    @staticmethod
    def initiate(customer):
        pass

    def add_product(self, product:Product, amount:int):
        pass

    def remove_product(self, product:Product, amount=None):
        pass

    def submit(self):
        pass

    def cancel(self):
        pass

    def send(self):
        pass


class OrderRow(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.IntegerField()