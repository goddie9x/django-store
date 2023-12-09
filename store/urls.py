from django.urls import path
from store import views
from .views import PrintableInvoiceView
app_name = 'store'

urlpatterns = [
    path('', views.ProductList.as_view(), name='product_list'),
    path('categories', views.CategoriesList.as_view(), name='categories_list'),
    path('product/<slug:slug>/', views.ProdcutDetails.as_view(),
         name='product_details'),
    path('printable_invoice/<int:invoice_id>/', PrintableInvoiceView.as_view(), name='printable_invoice'),
]
