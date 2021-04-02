from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    inventory = models.PositiveIntegerField(default=0, null=True)

    def increase_inventory(self, amount:int):
        if amount < 1:
            raise Exception('ورودی غیرقابل قبول می باشد')
        self.inventory += amount
        self.save()

    def decrease_inventory(self, amount:int):
        if amount < 1:
            raise Exception('ورودی غیرقابل قبول می باشد')
        if self.inventory >= amount:
            self.inventory -= amount
            self.save()
        else:
            raise Exception("به این میزان کالا موجود نمی باشد")


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    balance = models.PositiveIntegerField(default=20000, null=True)

    def deposit(self, amount:int):
        if amount < 1:
            raise Exception('ورودی غیرقابل قبول می باشد')
        self.balance += amount

    def spend(self, amount:int):
        if amount < 1:
            raise Exception('ورودی غیرقابل قبول می باشد')
        if self.balance >= amount:
            self.balance -= amount
        else:
            raise Exception("موجودی مشتری کافی نمی باشد")


class Order(models.Model):
    STATUS_SHOPPING = 1
    STATUS_SUBMITTED = 2
    STATUS_CANCELED = 3
    STATUS_SENT = 4

    status_choices = (
        (STATUS_SHOPPING, "در حال خرید"),
        (STATUS_SUBMITTED, "ثبت شده"),
        (STATUS_CANCELED, "لغو شده"),
        (STATUS_SENT, "ارسال شده"),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_time = models.DateTimeField()
    total_price = models.IntegerField()
    status = models.IntegerField(choices=status_choices)

    @staticmethod
    def initiate(customer:Customer):
        from django.utils import timezone

        #if self.status
        if Order.STATUS_SHOPPING in [item.status for item in Order.objects.filter(customer=customer)]:
            return Order.objects.filter(status=Order.STATUS_SHOPPING).get(customer=customer)

        self.status=Order.STATUS_SHOPPING
        self.order_time=timezone.now()
        self.total_price=0
        order.save()
        #order.getRows()
        return order

    def add_product(self, product:Product, amount:int):
        if amount <= 0:
            raise Exception("Wrong operation.")
        if amount > Product.objects.get(code=product.code).inventory:
            raise Exception("Inventory is not enough.")
        if product.code in [item.product.code for item in self.getRows()]:
            order_row = self.getOrderRow(product)
            order_row.amount += amount
            if order_row.amount > Product.objects.get(code=product.code).inventory:
                raise Exception("Inventory is not enough.")
            order_row.save()
        else:
            order_row = OrderRow(product=product, amount=amount, order=self)
            order_row.save()

        from django.utils import timezone
        self.order_time = timezone.now()
        self.total_price += product.price * amount
        self.save()

    def remove_product(self, product:Product, amount=None):
        if amount and amount <= 0 or not Product.objects.filter(code=product.code).exists():
            raise Exception("Wrong operation.")

        if product.code in [item.product.code for item in self.getRows()]:
            order_row = self.getOrderRow(product)
            if amount is None or order_row.amount == amount:
                order_row.delete()
                self.total_price -= product.price * order_row.amount
            elif order_row.amount > amount:
                order_row.amount -= amount
                self.total_price -= product.price * amount
                order_row.save()
            else:
                raise Exception("Entered amount is much than the amount in the card.")

        else:
            raise Exception("There is no such product in customer's card.")

        from django.utils import timezone
        self.order_time = timezone.now()
        self.save()

    def submit(self):
        if self.status != Order.STATUS_SHOPPING:
            raise Exception("This order is not submittable.")
        if len(self.getRows()) == 0:
            raise Exception("The cart is empty.")

        temporarily_reduced = dict()

        def recharge_inventories(max_):
            for order_row_ in self.getRows():
                order_row_.product.increase_inventory(temporarily_reduced[order_row_.id])

        i = 0
        for order_row in self.getRows():
            if order_row.amount > order_row.product.inventory:
                recharge_inventories(i)
                raise Exception(
                    """The product \"%s\" has been bought by other customers while you where shopping. 
                    Now the product's inventory is %i numbers.""" \
                    % (order_row.product.name, order_row.product.inventory))
            else:
                temporarily_reduced[order_row.id] = order_row.amount
                order_row.product.decrease_inventory(order_row.amount)
            i += 1


        price_sum = sum([item.product.price * item.amount for item in self.getRows()])
        customer_balance = self.customer.balance
        if price_sum > customer_balance:
            recharge_inventories(i)
            raise Exception("Not enough balance.")

        self.customer.balance -= price_sum
        self.customer.save()
        self.status = Order.STATUS_SUBMITTED
        from django.utils import timezone
        self.order_time = timezone.now()
        self.save()

    def cancel(self):
        if self.status != Order.STATUS_SUBMITTED:
            raise Exception("Not permitted operation.")

        if self.status == Order.STATUS_SUBMITTED:
            for order_row in self.getRows():
                self.customer.balance += order_row.product.price * order_row.amount
                self.customer.save()
                order_row.product.increase_inventory(order_row.amount)

        self.status = Order.STATUS_CANCELED
        self.save()

    def send(self):
        if self.status != Order.STATUS_SUBMITTED:
            raise Exception("The order is not submitted or has been cancelled.")
        self.status = Order.STATUS_SENT
        self.save()
        pass

    def getOrderRow(self, product: Product):
        return self.orderrow_set.get(product=product)

    def getRows(self):
        self.rows = list(self.orderrow_set.all())
        return self.rows


class OrderRow(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.IntegerField()