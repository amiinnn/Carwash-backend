from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.models import User
from decimal import Decimal
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User

class AdminProfile(models.Model):
    Firstname = models.CharField(max_length=30, blank=False)
    Lastname = models.CharField(max_length=30, blank=False)
    password = models.CharField(max_length=16, blank=False)
    nationalCode = models.CharField(max_length=10, blank=False)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    Firstname = models.CharField(max_length=30, blank=False)
    Lastname = models.CharField(max_length=30, blank=False)
    Email = models.EmailField(max_length=30, blank=False)
    nationalCode = models.CharField(max_length=10, blank=False, editable=False)
    phoneNumber = models.CharField(max_length=11, blank=False)
    password = models.CharField(max_length=128, blank=False) 
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)
        super(UserProfile, self).save(*args, **kwargs) 

class Car(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    model = models.CharField(max_length=16, blank=False)
    color = models.CharField(max_length=16, blank=False)
    firstId = models.CharField(max_length=2, blank=False)
    secondedId = models.CharField(max_length=1, blank=False)
    thirdId = models.CharField(max_length=3, blank=False)
    fourthId = models.CharField(max_length=2, blank=False)

class Workers(models.Model):
    Firstname = models.CharField(max_length=30, blank=False)
    Lastname = models.CharField(max_length=30, blank=False)
    nationalCode = models.CharField(max_length=10, blank=False, editable=False)
    phoneNumber = models.CharField(max_length=11, blank=False)
    shiftDate = models.DateField(blank=False, default=timezone.now)
    shiftStartTime = models.TimeField(blank=False, default=timezone.now)
    shiftEndTime = models.TimeField(blank=False, default=timezone.now)

class Position(models.Model):
    status = models.BooleanField(default=True)
    carStatus = models.CharField(max_length=50, blank=False)
    carId = models.ForeignKey('Car', on_delete=models.CASCADE, null=True)
    worker = models.ForeignKey(Workers, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=3, blank=False)
    freeTime = models.DateField(blank=False, default=timezone.now, null=True)
    capacity = models.IntegerField(default=10)
    queue_capacity = models.IntegerField(default=10)

class PositionQueue(models.Model):
    position = models.ForeignKey(Position, related_name='queue', on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['assigned_at']
    def __str__(self):
        return f"Car {self.car.id} in Position {self.position.name} Queue"

class Service(models.Model):
    name = models.CharField(max_length=100, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField(blank=False, default=timedelta(hours=1))

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    totalprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=Decimal('0.00'))
    tip = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    position = models.ForeignKey(Position, on_delete=models.CASCADE, default=20)
    statuspayment = models.BooleanField(default=True,blank=True, null=True)
    tax = models.DecimalField(default=Decimal('0.00'), null=True, blank=True, max_digits=10, decimal_places=2)
    worker=models.ForeignKey(Workers,on_delete=models.CASCADE,null=True,blank=True)
    def calculate_total_price(self):
        services_total = sum(item.service.price * item.quantity for item in self.order_items.all())
        self.total_price = services_total + self.tip
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        return f"{self.service.name} x {self.quantity}"

# product models
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='products/',null=True, blank=True)
    inventory = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.name

class ProductOrder(models.Model):
    user = models.ForeignKey(UserProfile, related_name='orders', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    statuspayment = models.BooleanField(default=True,blank=True, null=True)
    def __str__(self):
        username = self.user.user.username if self.user and self.user.user else "Unknown User"
        return f"Order {self.id} by {username}"

class ProductOrderItem(models.Model):
    order = models.ForeignKey(ProductOrder, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        product_name = self.product.name if self.product else "Unknown Product"
        return f"{self.quantity} x {product_name}"


class DiscountCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    def __str__(self):
        return self.code