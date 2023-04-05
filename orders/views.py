from django.shortcuts import render,redirect
from carts.models import CartItem
from . forms import OrderForm
from .models import Order,Address
from accounts.models import EditProfile
from carts.models import Coupon,UserCoupon
from django.http import JsonResponse
from django.db import IntegrityError

import datetime
import razorpay
from django.contrib.auth.decorators import login_required
from orders.models import Payment,OrderProduct
from LavenderHaze import settings
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib import messages
from store.models import Product
from django.views.decorators.csrf import csrf_exempt
from LavenderHaze.settings import RAZOR_KEY_ID,RAZOR_KEY_SECRET


# Create your views here.

@login_required(login_url='signin')
def payments(request,total=0):
    current_user    =   request.user
    cart_item       =   CartItem.objects.filter(user=current_user)



    tax  =  0
    grand_total     = 0

    for item in cart_item:
        total+= (item.product.price * item.quantity)

    # tax = (2 * total) / 100

    order_number    =   request.session['order_number']

    order_total = Order.objects.get(user=current_user,order_number=order_number)
    grand_total  =  order_total.order_total 
    try:

       coupon_discount = order_total.order_discout
    except:
        coupon_discount=0
    tax = order_total.tax
    order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)

    currency = 'INR'
    razorpay_client =  razorpay.Client(auth=(RAZOR_KEY_ID,RAZOR_KEY_SECRET)) 

    response_payment    =   razorpay_client.order.create(dict(amount=int(grand_total)* 100,currency=currency))
    print(response_payment)
    order_id    =   response_payment['id']
    order_status    =   response_payment['status']

    if order_status == 'created':
        payDetails  =   Payment(
            user = current_user,
            order_id    =   order_id,
            order_number    =   order_number,
            amount_paid =   grand_total

        )
        payDetails.save()

   

    context = {
            'order': order,
            'cart_items': cart_item,
            'total': total,
            'tax': tax,
            'grand_total': grand_total,
            'coupon_discount':coupon_discount,
            'payment': response_payment,
            'razorpay_merchant_key':RAZOR_KEY_ID,
        }        

    

    return render(request,'orders/payments.html',context)

@login_required(login_url='signin')
def place_order(request,total=0,quantity=0):
    current_user    =   request.user

    cart_items  =   CartItem.objects.filter(user=current_user)
    cart_count  =   cart_items.count()
    if cart_count <= 0 :
        return redirect('store')
    
    grand_total =   0
    tax =   0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity+=cart_item.quantity

    tax = (2 * total)/100
    coupon_discount = 0

    grand_total =  total+tax
    # grand_total = format(grand_total, '.2f')
   

    if request.method == 'POST':

        form = OrderForm(request.POST)
        if form.is_valid():
            try:
              coupon_code = request.session['coupon_code']
            except:
                pass


            #store the details in order table
            data =Order()
            data.user=current_user
            data.name=form.cleaned_data['name']
            data.phone=form.cleaned_data['phone']
            data.email=form.cleaned_data['email']
            data.address_line_1=form.cleaned_data['address_line_1']
            data.address_line_2=form.cleaned_data['address_line_2']
            data.country=form.cleaned_data['country']
            data.state=form.cleaned_data['state']
            data.city=form.cleaned_data['city']
            data.order_total= grand_total  
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            try:
                Address.objects.create(
                    user=current_user,
                    name=data.name ,
                    phone=data.phone,
                    email=data.email,
                    address_line_1=data.address_line_1,
                    address_line_2=data.address_line_2,
                    city=data.city,
                    state=data.state,
                    country=data.country)
            except IntegrityError:
                pass

            #generate order number
            yr  =   int(datetime.date.today().strftime('%Y'))
            dt  =   int(datetime.date.today().strftime('%d'))
            mt  =   int(datetime.date.today().strftime('%m'))
            d  =    datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #yyyy/mm/dd
            order_number    =   current_date + str(data.id)
            data.order_number   =   order_number
            data.save()



            # FOR COUPON 
            try:
                instance = UserCoupon.objects.get(user=request.user, coupon__code=coupon_code)

                if float(grand_total) >= float(instance.coupon.min_value):
                    coupon_discount = (
                        (float(grand_total) * float(instance.coupon.discount))/100)
                    grand_total =float(grand_total) - coupon_discount
        
                    grand_total = format(grand_total, '.2f')
            
                    coupon_discount = format(coupon_discount, '.2f')


                data.order_total = grand_total
                data.order_discout = coupon_discount
                data.save()

            except:
                pass   
            order   = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
         

     

            request.session['order_number'] = order_number
            
            

            return redirect('payments')
        else:
             return redirect('checkout')
                
@login_required(login_url='signin') 
def payment_success(request):
    order_number = request.session['order_number']
    transaction_id = Payment.objects.get(order_number=order_number)
  
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        
        # Change order status to Accepted when order is success
        order.status = 'Accepted' 
        order.save()
        
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        
        tax = 0
        total = 0
        grand_total = 0
        
        for item in ordered_products:
            total += (item.product_price * item.quantity)
        
        tax = (2 * total)/100
        grand_total = total + tax
        
        
        #Order Confirmmation Mail
        
        current_site = get_current_site(request)
        mail_subject = "Order Confirmation"
        message = render_to_string('orders/order_confirmation.html', {
        'order': order,
        'domain': current_site
        })
        to_mail = order.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_mail])
        send_email.send()
        messages.success(request, 'Order confirmation mail has been send to your registered email address')

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'transaction_id': transaction_id,
            'total': total,
            'tax': tax,
            'grand_total': grand_total
        }
        
        return render(request, 'orders/success.html', context)
    
    except Exception as e:
        raise e

def payment_fail(request):
  return render(request, 'orders/fail.html')


@csrf_exempt
def payment_status(request):

        response = request.POST
        params_dict = {
            'razorpay_order_id': response['razorpay_order_id'],
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_signature': response['razorpay_signature']
        } 
        

        # authorize razorpay client with API Keys.
        razorpay_client = razorpay.Client(
        auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))
        client = razorpay_client

        try:
            status = client.utility.verify_payment_signature(params_dict)
            transaction = Payment.objects.get(order_id=response['razorpay_order_id'])
            transaction.status = status
            transaction.payment_id = response['razorpay_payment_id']
            transaction.save()

            # get order number
            order_number = transaction.order_number
            order = Order.objects.get(is_ordered=False, order_number=order_number)

            order.payment = transaction
            order.is_ordered = True
            order.save()

            cart_items = CartItem.objects.filter(user=order.user)
            for item in cart_items:
                order_product = OrderProduct()
                order_product.order_id = order.id
                order_product.payment = transaction
                order_product.user_id = order.user.id
                order_product.product_id = item.product_id
                order_product.quantity = item.quantity 
                order_product.product_price = item.product.price
                order_product.ordered = True
                order_product.save()

                # Reducing Stock
                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()

                #  Clearing Cart Items
                cart_item = CartItem.objects.get(id=item.id)
                order_product = OrderProduct.objects.get(id=order_product.id)
                order_product.save()
            
            CartItem.objects.filter(user=order.user).delete()

            return redirect('payment_success')

        except Exception as e:
            transaction = Payment.objects.get(order_id=response['razorpay_order_id'])
            transaction.delete()
            return redirect('payment_fail')

def coupons(request):
    if request.method == 'POST':
        coupon_code = request.POST['coupon']
        grand_total = request.POST['grand_total']
        coupon_discount = 0
        try:
            instance = UserCoupon.objects.get(user = request.user ,coupon__code = coupon_code)
            if float(grand_total) >= float(instance.coupon.min_value):
                    coupon_discount = ((float(grand_total) * float(instance.coupon.discount))/100)
                    
                    grand_total = float(grand_total) - coupon_discount
                    
                    grand_total = format(grand_total, '.2f')
                    coupon_discount = format(coupon_discount, '.2f')
                    msg = 'Coupon Applied successfully'
                    instance.used = True
                    instance.save()
            else:
                msg='This coupon is only applicable for orders more than ₹'+ str(instance.coupon.min_value)+ '\- only!'
        except:
                msg = 'Coupon is not valid'
    response = {
               'grand_total': grand_total,
               'msg':msg,
               'coupon_discount':coupon_discount,
               'coupon_code':coupon_code,
                }
    try:
        request.session['coupon_code'] = coupon_code
    except:
        pass
    return JsonResponse(response)