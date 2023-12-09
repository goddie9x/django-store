from django.contrib import admin, messages
from store.models import Category, Product, InvoiceItem, Invoice, Supplier
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.core.exceptions import ValidationError

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    raw_id_fields = ('product',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier_name', 'created', 'total_price', 'printable_link')
    inlines = [InvoiceItemInline]
    list_per_page = 24

    def supplier_name(self, obj):
            return obj.supplier.name
    
    def save_model(self, request, obj, form, change):
        try:
            obj.save()
        except ValidationError as e:
            self.message_user(request, f"Error: {e.message}", level=messages.ERROR)
            return HttpResponse(f"Error: {e.message}")

    def printable_link(self, obj):
        url = reverse("store:printable_invoice", args=[obj.id])
        return format_html('<a href="{}" target="_blank">Print</a>', url)

    printable_link.short_description = 'Printable'

    actions = ['print_selected_invoices']

    def print_selected_invoices(self, request, queryset):
        printable_content = render_to_string('printable_invoice.html', {'invoices': queryset})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="invoices.pdf"'

        return response
    print_selected_invoices.short_description = 'Print selected invoices'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 24


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price','quantity', 'availability', 'updated', 'created')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('category',)
    list_editable = ('price', 'availability')
    list_per_page = 24

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name',)