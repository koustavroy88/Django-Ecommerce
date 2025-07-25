from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django.db.models import Q
import json
from cart.cart import Cart
# Create your views here.

def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        if not searched:
            messages.success(request,("That Product doesnot exists"))
            return render(request, 'search.html', {})
        else:
            return render(request, 'search.html', {'searched':searched})
    else:
        return render(request, 'search.html', {})



def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        shipping_user = ShippingAddress.objects.get(user__id = request.user.id)

        # get original user form
        form = UserInfoForm(request.POST or None, instance = current_user)
        # get shipping form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request,("Your Info hasbeen updated"))
            return redirect('home')
        return render(request, 'update_info.html', {'form':form, 'shipping_form':shipping_form})
    else:
        messages.success(request,("You must be looged in to access that page"))
        return redirect('home')

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                login(request, current_user)
                messages.success(request,("User password has been Updated"))
                return redirect('home')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        else:
            form = ChangePasswordForm(current_user)
        return render(request, 'update_password.html', {'form':form})
    else:
        messages.success(request,("You must be looged in to access that page"))
        return redirect('home')

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance = current_user)
        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request,("User hasbeen Updated"))
            return redirect('home')
        return render(request, 'update_user.html', {'user_form':user_form})
    else:
        messages.success(request,("You must be looged in to access that page"))
        return redirect('home')

def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {'categories':categories})



def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {
        'products':products
    })

def about(request):
    return render(request, 'about.html', {})

def login_user(request):
    if request.method=='POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            saved_cart = current_user.old_cart
            if saved_cart:
                converted_cart = json.loads(saved_cart)
                cart = Cart(request)
                for key,value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)


            messages.success(request,("You have been logged in"))
            return redirect('home')
        else:
            messages.success(request,("There was an error"))
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request,('You haved been looged out'))
    return redirect('home')
    

def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request,("Username Created - Please fill out your user info Below"))
            return redirect('update_info')
        else:
            messages.success(request,("There was a problem registering"))
            return redirect('register')
    else:
        return render(request, 'register.html', {
            'form':form
        })
    
def product(request,pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {
            'product':product
        })


def category(request,foo):
    foo = foo.replace('-','')
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        print(category, products)
        return render(request, 'category.html', {
            'products':products,
            'category':category,
        })
    except:
        messages.success(request,("That category doesnot exist"))
        return redirect('home')