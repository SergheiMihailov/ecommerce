import json
from .models import (Product,
                     Order,
                     OrderItem, 
                     ShippingAddress)

from users.models import Profile

def cookie_cart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except KeyError:
        cart = {}
    print("Cart:", cart)
    #Create empty cart for now for non-logged in user
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    total_quantity_in_cart = order['get_cart_items']

    for key in cart:
        # We use try block to prevent items in cart that may have been removed from causing error
        try:
            total_quantity_in_cart += cart[key]['quantity']

            product = Product.objects.get(id=key)
            total = product.price * cart[key]['quantity']
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[key]['quantity'] 
    
            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
                },
                'quantity': cart[key]['quantity'],
                'get_total': total,
            }
            items.append(item)
            if product.digital == False:
                order['shipping'] = True

        except():
                pass
    return {'total_quantity_in_cart': total_quantity_in_cart, 'order': order, 'items': items}


def cart_data(request):

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        total_quantity_in_cart = order.get_cart_items 
        
    else:
        cookie_data = cookie_cart(request)
        total_quantity_in_cart = cookie_data['total_quantity_in_cart']
        order = cookie_data['order']
        items = cookie_data['items']

    return {'items': items, 'order': order, 'total_quantity_in_cart': total_quantity_in_cart}


def guest_order(request, data):
    name = data['form']['name']
    email = data['form']['email']

    cookie_data = cookie_cart(request)
    items = cookie_data['items']

    customer, created = Profile.objects.get_or_create(email=email,)
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in items:
        product = Product.objects.get(id=item['id'])
        order_item = order_item.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],
        )
    return customer, order
