from decimal import Decimal
from django.conf import settings
from .models import Plan

class Cart(object):

    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, plan, quantity=1, update_quantity=False):
        """
        Add a plan to the cart or update its quantity.
        """
        plan_id = str(plan.id)
        if plan_id not in self.cart:
            self.cart[plan_id] = {'quantity': 0,
                                     'price': str(plan.price)}
        
        if update_quantity:
            self.cart[plan_id]['quantity'] = quantity
        else:
            self.cart[plan_id]['quantity'] += quantity
        
        self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def remove(self, plan):
        """
        Remove a plan from the cart.
        """
        plan_id = str(plan.id)
        if plan_id in self.cart:
            del self.cart[plan_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the plans
        from the database.
        """
        plan_ids = self.cart.keys()
        plans = Plan.objects.filter(id__in=plan_ids)

        for plan in plans:
            # Create a copy of the cart item to avoid modifying the session
            item = self.cart[str(plan.id)].copy()
            item['plan'] = plan
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()
