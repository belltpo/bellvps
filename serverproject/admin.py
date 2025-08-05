from django.contrib import admin
from .models import Order, OrderItem, Plan, Feature, Specification, ContactMessage
from import_export.admin import ImportExportModelAdmin
from django.utils import timezone
from datetime import timedelta

# Custom Date Filter for Admin
class DateRangeFilter(admin.SimpleListFilter):
    title = 'Date Range'
    parameter_name = 'date_range'
    date_field = None  # Must be overridden in subclass

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('past_7_days', 'Past 7 days'),
            ('this_month', 'This month'),
            ('this_year', 'This year'),
        )

    def queryset(self, request, queryset):
        if not self.date_field:
            raise NotImplementedError("The 'date_field' attribute must be set.")

        if self.value() == 'today':
            return queryset.filter(**{f'{self.date_field}__date': timezone.now().date()})
        if self.value() == 'past_7_days':
            return queryset.filter(**{f'{self.date_field}__gte': timezone.now() - timedelta(days=7)})
        if self.value() == 'this_month':
            return queryset.filter(**{f'{self.date_field}__year': timezone.now().year, f'{self.date_field}__month': timezone.now().month})
        if self.value() == 'this_year':
            return queryset.filter(**{f'{self.date_field}__year': timezone.now().year})

class OrderDateRangeFilter(DateRangeFilter):
    date_field = 'created'

class ContactMessageDateRangeFilter(DateRangeFilter):
    date_field = 'created_at'


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
    list_filter = [OrderDateRangeFilter, 'status', 'created', 'updated']
    search_fields = ['id', 'first_name', 'last_name', 'email', 'razorpay_order_id', 'razorpay_payment_id']
    inlines = [OrderItemInline]

@admin.register(ContactMessage)
class ContactMessageAdmin(ImportExportModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = (ContactMessageDateRangeFilter,)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
