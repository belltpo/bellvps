from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['domain_name', 'broker_name', 'api_key', 'api_secret', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'state', 'phone',
                  'billing_name', 'billing_address', 'billing_city', 'billing_state', 'billing_postal_code', 'gst_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'input input-bordered w-full'
            })
