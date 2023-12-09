from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.contrib import messages

class Category(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    slug = models.SlugField(unique=True, max_length=100, db_index=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_absolute_path(self):
        return reverse('store:product_list') + f'?category={self.id}'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(unique_for_date='created')
    description = models.TextField(null=False, blank=False)
    price = models.IntegerField(null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='media/products/%Y/%m/%d/', blank=True)
    availability = models.BooleanField(null=False, default=True)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        index_together = ('id', 'slug')
        ordering = ('-created',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_details', kwargs={'slug': self.slug})

class Supplier(models.Model):
    name = models.CharField(max_length=255)

class Invoice(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    
    def total_price(self):
        return sum(item.total_price() for item in self.items.all())
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.quantity * self.price
    
@receiver(pre_save, sender=InvoiceItem)
def update_product_quantity(sender, instance, **kwargs):
    product = instance.product
    old_quantity = 0
    if instance.pk:
        old_item = InvoiceItem.objects.get(pk=instance.pk)
        old_quantity = old_item.quantity

    quantity_difference = instance.quantity - old_quantity
    product = instance.product
    product.quantity += quantity_difference
    product.save()