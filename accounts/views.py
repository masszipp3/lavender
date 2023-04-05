from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm,UserForm,EditProfileForm,AddressForm
from .models import Account,EditProfile
from django.contrib.auth import get_user_model
from LavenderHaze.utils import send_activation_email,send_forgotpassword_mail
from carts.models import Cart,CartItem
from carts.views import _cart_id_
from orders.models import Order,Address, OrderProduct
from store.models import Product
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from LavenderHaze.settings import RAZOR_KEY_ID,RAZOR_KEY_SECRET
import razorpay
from orders.models import Payment
from django.urls import reverse

from razorpay.errors import BadRequestError
#for email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.shortcuts import HttpResponse
import requests
# Create your views here.

def signup(request):  
    if request.method == 'POST':
        form =   RegistrationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone=form.cleaned_data['phone']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']

            User    =   get_user_model()
            user= User.objects.create_user(name=name,email=email,password=password)
            # user.phone=phone
            setattr(user, 'phone', phone)
            user.save()
            EditProfile.objects.create(user=user)


            #sending email-helper function in utils
            send_activation_email(request,user)
            messages.success(request, "We have send you an email ,please verify it")
            return redirect('/accounts/signin/?command=verification&email='+email)
    else:
        form   = RegistrationForm()
    context =   {
        'form' : form,
    }
    return render(request,'accounts/signup.html',context)


             
def signin(request):
    if request.method == 'POST':
        email=request.POST['email']
        password=request.POST['password']
        user=authenticate(request,email=email,password=password)
        
        if user is not None:
            try:
                cart    =   Cart.objects.get(cart_id=_cart_id_(request))
                is_cart_item_exists =   CartItem.objects.filter(cart=cart).exists()

                if is_cart_item_exists :
                    cart_item   =   CartItem.objects.filter(cart=cart)
                   
                    for item in cart_item:
                        
                                item.user=  user
                                item.save()
            except:

                pass
            login(request,user)
            url =   request.META.get('HTTP_REFERER')
            try:
                query   =   requests.utils.urlparse(url).query
                params  =   dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage    =   params['next']
                    return redirect(nextPage)
                
                
            except:
                return redirect('ghome')
        else:
            messages.error(request,"Invalid credentials")
            return redirect('signup')
    return render(request,'accounts/signin.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='signin')
def signout(request):
    logout(request)
    return redirect('ghome')

def activate(request,uidb64,token):
   try:
    uid =urlsafe_base64_decode(uidb64).decode()
    user=Account._default_manager.get(pk=uid)
   except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
    user=None

   if user is not None and default_token_generator.check_token(user,token):
    user.is_active=True
    user.save()
    messages.success(request,'account activated')
    return redirect('signin')
   else:
    messages.error(request,"invalid activation link")
    return redirect('signup')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='signin')
def dashboard(request):
    orders  =   Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count=orders.count()
    context = {
        'orders_count' : orders_count
    }
    return render(request,'accounts/profile.html',context) 


def forgotPassword(request):
    if request.method=='POST':
        email= request.POST['email']
        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email__iexact=email) 
            send_forgotpassword_mail(request,user,email)
            messages.success(request,"Paswword reset email has been sent")
            return redirect('signin')
        else:
            messages.error(request,"Account doesnot exist")
            return redirect('forgotPassword')
    return render(request,'accounts/forgotPassword.html')

def resetpassword_validate(request,uidb64,token):
    try:
       uid =urlsafe_base64_decode(uidb64).decode()
       user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
       user=None
       
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,"Please reset your password")
        return redirect('resetPassword')
    else:
        messages.error(request,"This link has been expired")
        return redirect('signin')
@login_required(login_url='signin')
def resetPassword(request):
    if request.method=='POST':
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password==confirm_password:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset successfull")
            return redirect('signin')

        else:
            messages.error(request,"Passwords do not match")
            return redirect('resetPassword')

    else:

        return render(request,'accounts/resetPassword.html')

@login_required(login_url='signin')    
def edit_profile(request):
    userprofile = get_object_or_404(EditProfile,user=request.user)
    if request.method ==  'POST':
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = EditProfileForm(request.POST,instance=userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Your Profile has been updated')
            return redirect('edit_profile')
        
    else:
        user_form=UserForm(instance=request.user)
        profile_form=EditProfileForm(instance=userprofile)

    context =   {
        'user_form' : user_form,
        'profile_form' : profile_form,
    }
    return render(request,'accounts/edit_profile.html',context)


@login_required(login_url='signin')    
def my_orders(request):
    orders  =   Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context =   {
        'orders' :orders
    }
    return render(request,'accounts/my_orders.html',context)


@login_required(login_url='signin')    
def change_password(request):
    if request.method == 'POST':
        current_password    =   request.POST['current_password']
        new_password    =   request.POST['new_password']
        confirm_password    =   request.POST['confirm_password']

        user    =   Account.objects.get(name__iexact=request.user.name)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,'Password updated successfully')
                return redirect('change_password')
            else:
                messages.error(request,'Incorrect password')
                return redirect('change_password')
        else:
            messages.error(request,'Please enter valid password')
            return redirect('change_password')

    return render(request,'accounts/change_password.html')

@login_required(login_url='login')
def my_address(request):
   

    current_user = request.user
    address = Address.objects.filter(user=current_user)
    Address.objects.filter(user=current_user).order_by('id')


   

  
    context = {
        'address':address,
    }
    return render(request,'accounts/my_address.html',context)

@login_required(login_url='signin')
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST,request.FILES,)
        if form.is_valid():
            print('form is valid')
            detail = Address()
            detail.user = request.user
            detail.name =form.cleaned_data['name']
            detail.phone =  form.cleaned_data['phone']
            detail.email =  form.cleaned_data['email']
            detail.address_line_1 =  form.cleaned_data['address_line_1']
            detail.address_line_2  = form.cleaned_data['address_line_2']
            detail.state =  form.cleaned_data['state']
            detail.city =  form.cleaned_data['city']
            detail.save()
            messages.success(request,'Address added Successfully')
            return redirect('my_address')
        else:
            messages.success(request,'Form is Not valid')
            return redirect('my_address')
    else:
        form = AddressForm()
        context={
            'form':form
            }   
    return render(request,'accounts/add_address.html',context)

@login_required(login_url='login')
def delete_address(request,id):
    address=Address.objects.get(id = id)
    messages.success(request,"Address Deleted")
    address.delete()
    return redirect('my_address') 

@login_required(login_url='login')
def edit_address(request, id):
  address = Address.objects.get(id=id)
  if request.method == 'POST':
    form = AddressForm(request.POST, instance=address)
    if form.is_valid():
      form.save()
      messages.success(request , 'Address Updated Successfully')
      return redirect('my_address')
    else:
      messages.error(request , 'Invalid Inputs!!!')
      return redirect('my_address')
  else:
      form = AddressForm(instance=address)
      
  context = {
            'form' : form,
        }
  return render(request , 'accounts/edit_address.html' , context)

@login_required(login_url ='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
        
    }
    return render(request, 'accounts/order_detail.html', context)

@login_required(login_url='login')
def user_cancel_order(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        payment = Payment.objects.get(order_number=order_number)
        amount = order.order_total
        payment_id = payment.payment_id
        print(payment_id)

        client = razorpay.Client(auth=(RAZOR_KEY_ID,RAZOR_KEY_SECRET))
        print(client)
        client.payment.refund(payment_id, {
            "amount": amount,
            "speed": "instant",
        })
       

        order.status = 'Cancelled'
        order.save()
        # adding items back to store
        order_products=OrderProduct.objects.filter(user=request.user,order=order)
        for order_product in order_products:
            product= Product.objects.get(id=order_product.product)
            product.stock += order_product.quantity
            product.save()

        messages.success(request, 'Your order has been cancelled and a refund has been initiated.')
        return render(request,'accounts/cancel_order.html')

    except Exception as e:
        messages.error(request, str(e))
        return redirect('my_orders')
