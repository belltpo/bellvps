from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, OrderItem
from .forms import OrderCreateForm
from .cart import Cart
from django.conf import settings
from .ccavenue_utils import encrypt, decrypt
from django.views.decorators.csrf import csrf_exempt
import time
from urllib.parse import quote

def index(request):
    return render(request, 'serverproject/index.html')

def pricing(request):
    products = Product.objects.all()
    return render(request, 'serverproject/pricing.html', {'products': products})

def features(request):
    return render(request, 'serverproject/features.html')

def about(request):
    return render(request, 'serverproject/about.html')

def contact(request):
    return render(request, 'serverproject/contact.html')

def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    update_quantity = request.POST.get('update', False)

    if update_quantity:
        if quantity > 0:
            cart.add(product=product, quantity=quantity, update_quantity=True)
        else:
            cart.remove(product)
    else:
        cart.add(product=product, quantity=quantity)

    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'serverproject/cart_detail.html', {'cart': cart})

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            
            # Get total price before clearing the cart
            total_price = cart.get_total_price()
            cart.clear()

            # Prepare data for CCAvenue, ensuring no empty values are sent
            tid = str(int(time.time()))
            merchant_params = {
                'tid': tid,
                'merchant_id': settings.CCAVENUE_MERCHANT_ID,
                'order_id': tid, 
                'amount': str(total_price),
                'currency': 'INR',
                'redirect_url': settings.CCAVENUE_REDIRECT_URL,
                'cancel_url': settings.CCAVENUE_CANCEL_URL,
                'language': 'EN',
                'billing_name': f'{order.first_name} {order.last_name}',
                'billing_address': order.address,
                'billing_city': order.city,
                'billing_state': order.state,
                'billing_zip': order.postal_code,
                'billing_country': 'India',
                'billing_tel': order.phone,
                'billing_email': order.email,
            }
            
            # Filter out any keys with empty or None values and URL-encode the values
            merchant_data = '&'.join([f'{key}={quote(str(value))}' for key, value in merchant_params.items() if value is not None and value != ''])

            print('CCAvenue Merchant Data:', merchant_data)

            enc_request = encrypt(merchant_data, settings.CCAVENUE_WORKING_KEY)
            
            return render(request, 'serverproject/ccavenue_redirect.html', {'enc_request': enc_request, 'access_code': settings.CCAVENUE_ACCESS_CODE})

    else:
        form = OrderCreateForm()
    return render(request, 'serverproject/order_create.html', {'cart': cart, 'form': form})

@csrf_exempt
def ccavenue_success(request):
    if request.method == 'POST':
        enc_response = request.POST.get('encResp')
        dec_response = decrypt(enc_response, settings.CCAVENUE_WORKING_KEY)
        
        # Parse the decrypted data
        data = {key: val for key, val in [pair.split('=') for pair in dec_response.split('&')]}

        order_id = data.get('order_id')
        order_status = data.get('order_status')

        try:
            order = Order.objects.get(id=order_id)
            if order_status == 'Success':
                order.paid = True
                order.ccavenue_order_id = data.get('tracking_id')
                order.save()
                return render(request, 'serverproject/order_created.html', {'order': order})
            else:
                return render(request, 'serverproject/payment_failed.html', {'order': order, 'status': order_status})
        except Order.DoesNotExist:
            # Handle error: Order not found
            pass
    return redirect('index') # Or some error page

@csrf_exempt
def ccavenue_cancel(request):
    # You can render a template here to inform the user that the payment was cancelled.
    return render(request, 'serverproject/payment_failed.html', {'status': 'Cancelled by user'})