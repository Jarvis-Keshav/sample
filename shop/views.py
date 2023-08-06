from django.shortcuts import render,redirect
from .models import Product, Contact, Orders, OrderUpdate, Register
from math import ceil
from django.contrib import messages
import json
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.models import User, auth
from django.core.mail import send_mail

# Create your views here.
from django.http import HttpResponse


def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)
    
def recommend(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/recommend.html', params)

def searchMatch(query, item):
    if query in item.product_name or query in item.category:
        return True
    else:
        return False

def search(request):
    query= request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod=[item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod)!= 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg":""}
    if len(allProds)==0 or len(query)<4:
        params={'msg':"Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)
    

def register(request):
    error=False
    erroro=False
    errora=False
    if request.method=="POST":
        name = request.POST.get('name', '')
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if password1==password2:
            if Register.objects.filter(username=username).exists():
                erroro=True
                return render(request, 'shop/register.html',{'erroro': erroro})
            elif Register.objects.filter(email=email).exists():
                errora=True
                return render(request, 'shop/register.html',{'errora': errora})
            else:
                register = Register(name=name, username=username, email=email, password1=password1, password2=password2)
                register.save()
                return render(request, 'shop/login.html')
        else:
            error=True
            return render(request, 'shop/register.html',{'error': error})
        return redirect('/')
    else:    
        return render(request, 'shop/register.html')

def loginn(request):
    nope=False
    if request.method=="POST":
        username = request.POST.get('username', '')
        password1 = request.POST.get('password1', '')
        useri = Register.objects.filter(username=username,password1=password1).exists()
        # user = auth.authenticate(username=username,password1=password1)
        
        if useri:
            # auth.login(request,user)
            return redirect("/")
        else:
            nope=True
            return render(request, 'shop/login.html',{'nope': nope})
        # return redirect('/')
    else:
        return render(request, 'shop/login.html')

def logoutt(request):
    logout(request)
    return redirect('/')

def contact(request):
    thank = False
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html',{'thank': thank})


def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates, order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

    return render(request, 'shop/tracker.html')


def productView(request, myid):

    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/prodView.html', {'product':product[0]})


def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        send_mail(
            'Your Order Id: Avail Trial',
            'order.order_id',
            'kgupta3_be20@thapar.edu',
            [email],
            )
        return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
    return render(request, 'shop/checkout.html')

def trending(request):
    return render(request,'shop/trending.html')