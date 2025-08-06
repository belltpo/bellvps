from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pricing/', views.pricing, name='pricing'),
    path('features/', views.features, name='features'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('cart/add/<int:plan_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:plan_id>/', views.cart_remove, name='cart_remove'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('order/create/', views.order_create, name='order_create'),
    path('payment/verification/', views.payment_verification, name='payment_verification'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failed/<str:razorpay_order_id>/', views.payment_failed, name='payment_failed'),
    path('payment/cancelled/<str:razorpay_order_id>/', views.payment_cancelled, name='payment_cancelled'),
    path('debug/razorpay/', views.debug_razorpay, name='debug_razorpay'),

    # Policy pages
    path('terms-and-conditions/', views.terms_conditions, name='terms_conditions'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('support-policy/', views.support_policy, name='support_policy'),
]