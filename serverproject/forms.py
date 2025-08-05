from django import forms
from .models import Order, ContactMessage

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['domain_name', 'broker_name', 'api_key', 'api_secret', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'state', 'phone',
                  'billing_name', 'billing_address', 'billing_city', 'billing_state', 'billing_postal_code', 'gst_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'input input-bordered w-full',
                'autocomplete': 'off'
            })

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Your Name'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Your Email'
        })
        self.fields['subject'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Subject'
        })
        self.fields['message'].widget.attrs.update({
            'class': 'textarea textarea-bordered w-full h-32',
            'placeholder': 'Your Message'
        })
