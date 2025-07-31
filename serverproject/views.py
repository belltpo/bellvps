from django.shortcuts import render, redirect, get_object_or_404
from .models import Plan, Order, OrderItem
from .forms import OrderCreateForm
from .cart import Cart
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import JsonResponse
import json

def index(request):
    return render(request, 'serverproject/index.html')

def pricing(request):
    plans = Plan.objects.prefetch_related('features', 'specifications').all()
    return render(request, 'serverproject/pricing.html', {'plans': plans})

def features(request):
    return render(request, 'serverproject/features.html')

def about(request):
    return render(request, 'serverproject/about.html')

def contact(request):
    return render(request, 'serverproject/contact.html')

def cart_add(request, plan_id):
    cart = Cart(request)
    plan = get_object_or_404(Plan, id=plan_id)
    quantity = int(request.POST.get('quantity', 1))
    update_quantity = request.POST.get('update', False)

    if update_quantity:
        if quantity > 0:
            cart.add(plan=plan, quantity=quantity, update_quantity=True)
        else:
            cart.remove(plan)
    else:
        cart.add(plan=plan, quantity=quantity)

    return redirect('cart_detail')

def cart_remove(request, plan_id):
    cart = Cart(request)
    plan = get_object_or_404(Plan, id=plan_id)
    cart.remove(plan)
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
                                       plan=item['plan'],
                                       price=item['price'],
                                       quantity=item['quantity'])
            
            # Get total cost
            total_cost = order.get_total_cost()

            # Check if total cost is below Razorpay's minimum
            if total_cost < 1:
                form.add_error(None, 'The total amount must be at least ₹1.00 to proceed with payment.')
                # Re-add items to cart since we cleared it prematurely
                for item in OrderItem.objects.filter(order=order):
                    cart.add(plan=item.plan, quantity=item.quantity)
                return render(request, 'serverproject/order_create.html', {'cart': cart, 'form': form})

            cart.clear()

            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Create Razorpay order
            razorpay_order = client.order.create({
                'amount': int(total_cost * 100),  # Amount in paise
                'currency': 'INR',
                'receipt': f'order_rcptid_{order.id}',
                'payment_capture': 1
            })

            # Store Razorpay order ID in the order
            order.razorpay_order_id = razorpay_order['id']
            order.save()

            context = {
                'order': order,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': int(total_cost * 100)
            }
            return render(request, 'serverproject/payment.html', context)
    else:
        form = OrderCreateForm()
    return render(request, 'serverproject/order_create.html', {'cart': cart, 'form': form})

def payment_verification(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            razorpay_payment_id = data.get('razorpay_payment_id', '')
            razorpay_order_id = data.get('razorpay_order_id', '')
            razorpay_signature = data.get('razorpay_signature', '')

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            client.utility.verify_payment_signature(params_dict)

            try:
                order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                order.razorpay_payment_id = razorpay_payment_id
                order.razorpay_signature = razorpay_signature
                order.status = 'paid'
                order.save()
                
                request.session['order_id'] = order.id
                return JsonResponse({'success': True, 'redirect_url': reverse('payment_success')})
            except Order.DoesNotExist:
                return JsonResponse({'success': False, 'redirect_url': reverse('payment_failed')})

        except Exception as e:
            try:
                order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                order.status = 'failed'
                order.save()
            except Order.DoesNotExist:
                pass
            return JsonResponse({'success': False, 'redirect_url': reverse('payment_failed')})
            
    return JsonResponse({'success': False, 'redirect_url': reverse('payment_failed')})

def payment_success(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id) if order_id else None
    return render(request, 'serverproject/payment_success.html', {'order': order})

def payment_failed(request):
    return render(request, 'serverproject/payment_failed.html')

def payment_cancelled(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        if order.status == 'pending': 
            order.status = 'cancelled'
            order.save()
    except Order.DoesNotExist:
        pass
    return render(request, 'serverproject/payment_cancelled.html')

# Policy Pages
def terms_conditions(request):
    return render(request, 'serverproject/terms_conditions.html')

def refund_policy(request):
    return render(request, 'serverproject/refund_policy.html')

def privacy_policy(request):
    return render(request, 'serverproject/privacy_policy.html')

def support_policy(request):
    return render(request, 'serverproject/support_policy.html')