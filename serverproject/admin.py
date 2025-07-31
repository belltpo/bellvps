from django.contrib import admin
from .models import Order, OrderItem, Plan, Feature, Specification
from import_export.admin import ImportExportModelAdmin

# Register your models here.

class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1

class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    inlines = [FeatureInline, SpecificationInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['plan']

@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'status', 'created', 'updated', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
    list_filter = ['status', 'created', 'updated']
    search_fields = ['id', 'first_name', 'last_name', 'email', 'razorpay_order_id', 'razorpay_payment_id']
    inlines = [OrderItemInline]
