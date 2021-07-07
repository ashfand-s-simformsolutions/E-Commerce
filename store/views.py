from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
import stripe
from django.urls import reverse
from .models import *
from .forms import CreateUserForm, CustomerForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .filters import ProductFilter
from django.db.models import Q
from .tasks import send_email_task
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = "sk_test_51IKzE3ESBnIcbysIhQkTY2Qx2QuMacDBqu5bTmK68xK8sD4HHoZVRLSzR77Puu4LEwOmnC6rBDB9QaN1LYHDnVD400ZxmNJO34"


@login_required(login_url='login')
def payment(request):
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    cartTotal = order.get_cart_total
    amount = cartTotal
    context = {'amount': amount}
    return render(request, 'store/payment.html', context)


@login_required(login_url='login')
def charge(request):
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    cartTotal = order.get_cart_total
    amount = int(cartTotal)
    if request.method == 'POST':
        print('Data: ', request.POST)

    cstmr = stripe.Customer.create(
        email=request.POST['email'],
        name=request.POST['nickname'],
        source=request.POST['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=cstmr,
        amount=amount,
        currency='inr',
        description='Cart Payment'
    )
    return redirect(reverse('success', args=[amount]))


@csrf_exempt
def profile(request):
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    cartItems = order.get_cart_items
    cartTotal = order.get_cart_total
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {'customer': customer, 'form': form, 'cartItems': cartItems, 'cartTotal': cartTotal}
    return render(request, 'store/profile.html', context)


@csrf_exempt
@login_required(login_url='login')
def home(request):
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    cartItems = order.get_cart_items
    category = Category.objects.all()

    context = {'category': category, 'cartItems': cartItems}
    return render(request, 'store/home.html', context)


@login_required(login_url='login')
def store(request, pk_test):
    customer = request.user.customer  # returns users
    order, created = Order.objects.get_or_create(customer=customer, complete=False)  # order returns orders
    cartItems = order.get_cart_items

    category = Category.objects.get(id=pk_test)
    products = Product.objects.filter(category=category)

    myFilter = ProductFilter(request.GET, queryset=products)
    products = myFilter.qs

    context = {'products': products, 'cartItems': cartItems, 'myFilter': myFilter}
    return render(request, 'store/store.html', context)


@login_required(login_url='login')
def search(request):
    customer = request.user.customer  # returns users
    order, created = Order.objects.get_or_create(customer=customer, complete=False)  # order returns orders
    cartItems = order.get_cart_items

    search_query = request.GET['search']
    products = Product.objects.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    context = {'cartItems': cartItems, 'products': products, 'search_query': search_query}
    return render(request, 'store/search.html', context)


def register_page(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for : ' + user)
                return redirect('login')
        context = {'form': form}
        return render(request, 'accounts/register.html', context)


def login_page(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username or Password is incorrect')

        context = {}
        return render(request, 'accounts/login.html', context)


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action : ', action)
    print('ProductId : ', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
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

    else:
        print('User is not logged in')
    return JsonResponse('Payment complete', safe=False)


def description(request, pk):
    products = Product.objects.filter(id=pk)
    context = {'products': products}
    return render(request, 'store/description.html', context)


@login_required(login_url='login')
def success(request, amnt):
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()

    user = request.user.customer
    send_email_task(user.name, user.email, items)
    amount = amnt

    context = {'name': user.name, 'items': items, 'amount': amount}
    return render(request, 'store/success.html', context)
