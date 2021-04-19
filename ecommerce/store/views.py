from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from .models import (Product,
                     Order,
                     OrderItem,
                     ShippingAddress)
                     
from .utils import cookie_cart, cart_data, guest_order
from django.db.models import Q



def home(request):
    data = cart_data(request)
    total_quantity_in_cart = data['total_quantity_in_cart']

    template_name = 'store/home.html'
    context = {'total_quantity_in_cart': total_quantity_in_cart}

    return render(request, template_name, context)


def about(request):
    data = cart_data(request)
    total_quantity_in_cart = data['total_quantity_in_cart']

    template_name = 'store/about.html'
    context = {'total_quantity_in_cart': total_quantity_in_cart}
    return render(request, template_name, context)


def store(request):
    data = cart_data(request)
    total_quantity_in_cart = data['total_quantity_in_cart']
   
    query = request.GET.get('q')
    if query:
        products = Product.objects.all().filter(Q(name__icontains=query))
    else: 
        products = Product.objects.all()
    context = {'products': products, 'total_quantity_in_cart': total_quantity_in_cart}
    return render(request, 'store/store.html', context)


def product_detail(request, pk):
    data = cart_data(request)
    total_quantity_in_cart = data['total_quantity_in_cart']
    product = Product.objects.get(pk=pk)
    template_name = 'store/product_detail.html'
    context = {'product': product,
               'total_quantity_in_cart': total_quantity_in_cart}
    return render(request, template_name, context)


def cart(request):
    data = cart_data(request)

    total_quantity_in_cart = data['total_quantity_in_cart']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order,
               'total_quantity_in_cart': total_quantity_in_cart}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cart_data(request)

    total_quantity_in_cart = data['total_quantity_in_cart']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order,
               'total_quantity_in_cart': total_quantity_in_cart}
    return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', product_id)

    customer = request.user #.customer
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    order_item, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        order_item.quantity = (order_item.quantity + 1)
    elif action == 'remove':
        order_item.quantity = (order_item.quantity - 1)

    order_item.save()

    if order_item.quantity <= 0:
        order_item.delete()

    return JsonResponse('Item was added', safe=False)



def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        

    else:
        customer, order = guest_order(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            )

    return JsonResponse('Payment submitted..', safe=False)
