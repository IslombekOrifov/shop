from django.urls import reverse
from django.shortcuts import render, redirect

from cart.cart import Cart

from .models import Order, OrderItem
from .forms import OrderCreatForm
from .tasks import order_created


def order_create(request): 
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreatForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            cart.clear()
            order_created.delay(order.id)
            request.session['order_id'] = order.id
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreatForm()
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})