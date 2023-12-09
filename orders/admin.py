from django.contrib import admin, messages
from orders.models import Order, OrderItem
from store.models import Product
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.db import transaction

class OrderItemTabular(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ['product', ]
    readonly_fields = ['total_price']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'product':
            # Limit the available products based on some condition if needed
            kwargs['queryset'] = Product.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'total_price', 'address', 'pin_code', 'city', 'status', 'paid']
    list_filter = ['paid', 'created', 'status']
    search_fields = ('customer_name', 'id')
    list_editable = ['status', 'paid']
    list_per_page = 24
    readonly_fields = ['total_price']
    inlines = [OrderItemTabular]

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            try:
                super().save_model(request, obj, form, change)
            except ValidationError as e:
                messages.error(request, f"Error: {', '.join(e.messages)}")
                transaction.set_rollback(True)