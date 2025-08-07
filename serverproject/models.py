from django.db import models

# Create your models here.

class Plan(models.Model):
    DURATION_CHOICES = (
        ('1_month', '/month'),
        ('3_months', '/3 months'),
        ('6_months', '/6 months'),
        ('1_year', '/year'),
    )
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default='1_year')
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Feature(models.Model):
    plan = models.ForeignKey(Plan, related_name='features', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Specification(models.Model):
    plan = models.ForeignKey(Plan, related_name='specifications', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Order(models.Model):
    BROKER_CHOICES = [
        ('5paisa', '5paisa'),
        ('5paisa_xts', '5paisa (XTS)'),
        ('aliceblue', 'Aliceblue'),
        ('angelone', 'AngelOne'),
        ('compositedge_xts', 'Compositedge (XTS)'),
        ('dhan', 'Dhan'),
        ('dhan_sandbox', 'Dhan (Sandbox)'),
        ('firstock', 'Firstock'),
        ('flattrade', 'Flattrade'),
        ('fyers', 'Fyers'),
        ('groww', 'Groww'),
        ('iifl_xts', 'IIFL (XTS)'),
        ('indiabulls', 'IndiaBulls'),
        ('indmoney', 'IndMoney'),
        ('kotak_securities', 'Kotak Securities'),
        ('paytm', 'Paytm'),
        ('pocketful', 'Pocketful'),
        ('shoonya', 'Shoonya'),
        ('upstox', 'Upstox'),
        ('wisdom_capital_xts', 'Wisdom Capital (XTS)'),
        ('zebu', 'Zebu'),
        ('zerodha', 'Zerodha'),
    ]
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    domain_name = models.CharField(max_length=100, blank=True)
    broker_name = models.CharField(max_length=100, choices=BROKER_CHOICES, default='zerodha')
    api_key = models.CharField(max_length=100, blank=True)
    api_secret = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Billing Information
    billing_name = models.CharField(max_length=100, blank=True)
    billing_address = models.CharField(max_length=250, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    gst_number = models.CharField(max_length=15, blank=True, verbose_name="GST Number")

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ('-created_at',)
