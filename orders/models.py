from django.db import models
from store.models import Product
from django.urls import reverse
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.db import transaction

choices = (
    ('Pending', 'Pending'),
    ('Packed', 'Packed'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered')
)
class Order(models.Model):
    customer_name = models.CharField(default='', max_length=255, blank=False, null=False)
    address = models.CharField(max_length=150, blank=False, null=False)
    pin_code = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=choices, max_length=10, default='Pending')
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Order {self.id}'
    
    def total_price(self):
        return sum(item.total_price() for item in self.items.all())
    
    def get_absolute_url(self):
        return reverse('orders:invoice', kwargs={'pk': self.pk})
    
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='ordered', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Order Item {self.id}'

    def save(self, *args, **kwargs):
        with transaction.atomic():
            old_quantity = 0
            if self.pk:  
                old_item = OrderItem.objects.get(pk=self.pk)
                old_quantity = old_item.quantity
            super().save(*args, **kwargs)
            quantity_difference = self.quantity - old_quantity

            product = self.product
            if quantity_difference > product.quantity:
                raise ValidationError({'quantity': 'Not enough quantity available'})

            product.quantity -= quantity_difference
            product.save()

    def total_price(self):
        return self.quantity * self.product.price