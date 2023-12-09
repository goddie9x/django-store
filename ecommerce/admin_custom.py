from django.contrib import admin

class CustomAdminSite(admin.AdminSite):
    site_header = 'Quản lý bán hàng'