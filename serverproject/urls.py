from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pricing/', views.pricing, name='pricing'),
    path('features/', views.features, name='features'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('order/create/', views.order_create, name='order_create'),
    path('ccavenue/success/', views.ccavenue_success, name='ccavenue_success'),
    path('ccavenue/cancel/', views.ccavenue_cancel, name='ccavenue_cancel'),
]