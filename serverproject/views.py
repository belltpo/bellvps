from django.shortcuts import render, redirect, get_object_or_404
from .models import Plan, Order, OrderItem, ContactMessage
from .forms import OrderCreateForm, ContactForm
from .cart import Cart
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import JsonResponse
import json
from razorpay import errors
import logging
from django.contrib import messages
from .utils import send_invoice_email

# Get an instance of a logger
logger = logging.getLogger(__name__)

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
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'serverproject/contact.html', {'form': form})

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
        # For server plans, always set quantity to 1
        cart.add(plan=plan, quantity=1)

    # Redirect back to the referring page or cart_detail if no referrer
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'cart_detail'))
    if 'cart' not in next_url:  # If coming from pricing page, stay there
        return redirect(next_url)
    else:
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
            
            total_cost = order.get_total_cost()

            if total_cost < 1:
                return JsonResponse({'error': 'The total amount must be at least ₹1.00.'}, status=400)

            cart.clear()

            try:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

                razorpay_order = client.order.create({
                    'amount': int(total_cost * 100),
                    'currency': 'INR',
                    'receipt': f'order_{order.id}',
                    'payment_capture': 1
                })

                order.razorpay_order_id = razorpay_order['id']
                order.save()

                return JsonResponse({
                    'order_id': razorpay_order['id'],
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'amount': int(total_cost * 100), 
                    'currency': 'INR',
                    'first_name': order.first_name,
                    'last_name': order.last_name,
                    'email': order.email,
                    'phone': order.phone,
                    'address': order.address,
                })
            except Exception as e:
                logger.error(f"Error creating Razorpay order: {e}")
                return JsonResponse({'error': 'Could not connect to payment gateway.'}, status=500)
        else:
            return JsonResponse({'error': 'Invalid form data.', 'errors': form.errors}, status=400)

    else: # GET request
        form = OrderCreateForm()
    
    return render(request, 'serverproject/order_create.html', {
        'cart': cart,
        'form': form,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID
    })

@csrf_exempt
def payment_verification(request):
    if request.method == "POST":
        logger.info(f"Received payment verification data: {request.body.decode()}")
        
        try:
            data = json.loads(request.body)
            razorpay_payment_id = data['razorpay_payment_id']
            razorpay_order_id = data['razorpay_order_id']
            razorpay_signature = data['razorpay_signature']
            
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            logger.info(f"Order ID: {razorpay_order_id}")
            logger.info(f"Payment ID: {razorpay_payment_id}")
            logger.info(f"Signature: {razorpay_signature}")

        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Invalid payload received: {e}")
            return JsonResponse({'success': False, 'redirect_url': reverse('payment_failed')})

        # Initialize Razorpay client
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            logger.info("Razorpay client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Razorpay client: {e}")
            return JsonResponse({'success': False, 'redirect_url': reverse('payment_failed')})

        try:
            # Verify payment signature
            client.utility.verify_payment_signature(params_dict)
            logger.info("Payment signature verified successfully")
            
            try:
                order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                logger.info(f"Found order: {order.id}")
                
                order.razorpay_payment_id = razorpay_payment_id
                order.razorpay_signature = razorpay_signature
                order.status = 'paid'
                order.save()
                logger.info(f"Order {order.id} updated successfully")
                
                # Clear the cart
                cart = Cart(request)
                cart.clear()
                
                # Send invoice email
                try:
                    send_invoice_email(order)
                    logger.info(f"Invoice email sent successfully for order {order.id}")
                except Exception as email_error:
                    logger.error(f"Failed to send invoice email for order {order.id}: {email_error}")
                    # Don't fail the payment if email fails
                
                request.session['order_id'] = order.id
                logger.info(f"Payment verification successful for order {order.id}")
                return JsonResponse({'success': True, 'redirect_url': reverse('payment_success')})
                
            except Order.DoesNotExist:
                logger.error(f"Order not found for razorpay_order_id: {razorpay_order_id}")
                return JsonResponse({'success': False, 'redirect_url': reverse('payment_failed')})

        except errors.SignatureVerificationError as e:
            logger.error(f"Signature Verification Failed: {e}")
            try:
                order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                order.status = 'failed'
                order.save()
                logger.info(f"Order {order.id} marked as failed")
            except Order.DoesNotExist:
                logger.error(f"Order not found when marking as failed: {razorpay_order_id}")
            return JsonResponse({'success': False, 'redirect_url': reverse('payment_failed')})
        except Exception as e:
            logger.error(f"An unexpected error occurred in payment verification: {e}")
            return JsonResponse({'success': False, 'redirect_url': reverse('payment_failed')})
            
    logger.error("Payment verification called with non-POST method")
    return JsonResponse({'success': False, 'redirect_url': reverse('payment_failed')})

def payment_success(request):
    return render(request, 'serverproject/payment_success.html')

def payment_failed(request, razorpay_order_id):
    order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)
    order.status = 'failed'
    order.save()
    return render(request, 'serverproject/payment_failed.html', {'order': order})

def payment_cancelled(request, razorpay_order_id):
    order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)
    order.status = 'cancelled'
    order.save()
    return render(request, 'serverproject/payment_cancelled.html', {'order': order})

def debug_razorpay(request):
    """Debug view to test Razorpay configuration"""
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Test creating a simple order
        test_order = client.order.create({
            'amount': 100,  # ₹1.00 in paise
            'currency': 'INR',
            'receipt': 'test_receipt_123',
            'payment_capture': 1
        })
        
        return JsonResponse({
            'success': True,
            'message': 'Razorpay configuration is working',
            'test_order_id': test_order['id'],
            'key_id': settings.RAZORPAY_KEY_ID[:8] + '...'  # Show only first 8 chars for security
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Razorpay configuration failed'
        })

# Policy Pages
def terms_conditions(request):
    return render(request, 'serverproject/terms_conditions.html')

def refund_policy(request):
    return render(request, 'serverproject/refund_policy.html')

def privacy_policy(request):
    return render(request, 'serverproject/privacy_policy.html')

def support_policy(request):
    return render(request, 'serverproject/support_policy.html')