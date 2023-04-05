from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import Account
from django.db.models import Q ,Sum,FloatField

from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
from adminpanel.forms import ProductForm,CategoryForm,Update_CategoryForm,Update_ProductForm,CouponForm
from category.models import Category
from store.models import Product,ReviewRating
from orders.models import Order, Payment
from carts.models import Coupon
from datetime import datetime,timedelta,date
from django.db.models.functions import Cast



# Create your views here.

def admin_login(request):
        if request.user.is_authenticated:
            if request.user.is_admin:
                 return redirect('admin_home') 
            else:
                 return redirect('ghome')  
        else:
            if request.method == 'POST':
                email = request.POST['email']
                password = request.POST['password']

                user = authenticate(request, username=email, password=password)
                if user is not None:
                    if user.is_admin:
                        login(request, user)
                        messages.success(request, 'You are logged in as admin')
                        return redirect('admin_home')
                    # else:
                    #     messages.warning(request, 'You are logged in as admin')

                else:
                    messages.error(request, 'Email or Password is incorrect')
        return render(request,'admin/login.html')

@login_required(login_url='admin_login')
def admin_home(request):
    if request.user.is_admin:
     

          number_of_users  = Account.objects.filter(is_admin = False).count()
          print('user',number_of_users )

    

          total_payment_count=Payment.objects.all()
          try:
               total_payment_amount = Payment.objects.filter(status = 'True').annotate(total_amount=Cast('amount_paid', FloatField())).aggregate(Sum('total_amount'))
        
          except:
               total_payment_amount=0
          if total_payment_amount['total_amount__sum'] :
               revenue = total_payment_amount['total_amount__sum']
               revenue = format(revenue, '.2f')
          
          else:
               revenue = 0
       


          total_users = Account.objects.filter(is_admin=False).count()
          total_orders = Order.objects.all().count()
          total_products = Product.objects.all().count()
          total_categories = Category.objects.all().count()
   
          #status
          accepted = Order.objects.filter(status = 'Accepted', is_ordered=True).count()

          completed = Order.objects.filter(status = "Completed").count()
          returned = Order.objects.filter(status = "Returned").count()
          cancelled = Order.objects.filter(status = "Cancelled").count()


          context={
               'total_users':total_users,
               'total_orders':total_orders,
               'total_products':total_products,
               'total_categories':total_categories,
       
               'number_of_users':number_of_users,
               'total_payment_count':total_payment_count,
               'revenue':revenue,
               'accepted':accepted,
               'completed':completed,
               'returned':returned,
               'cancelled':cancelled,
      

               
          }
          return render(request, 'admin/admin_home.html',context)
    return redirect('admin_login')


@never_cache
def adminlogout(request):
    logout(request)
    return redirect('admin_login')


# USER MANAGEMENT
@login_required(login_url='admin_login')
def admin_userlist(request):
     if request.user.is_admin:
          if request.method == 'POST':
               search = request.POST['search']
               users = Account.objects.filter(Q(name__icontains=search) |  Q(email__icontains=search) ).order_by('id')
               print('helloo')
          
          else:
               users = Account.objects.filter(is_admin=False).order_by('id')

          paginator   = Paginator(users, 4) 
          page        = request.GET.get('page')
          paged_users = paginator.get_page(page)

          context = {
               'users' : paged_users,
          }
          return render(request, 'admin/admin_userlist.html', context)
     else:
          return redirect('ghome')
@login_required(login_url='admin_login')
def blockuser(request,id):
       
               user = Account.objects.get(id=id)
               if user.is_active:
                    user.is_active = False
                    user.save()
                    messages.success(request,'user successfully blocked')
               else:
                    user.is_active = True
                    user.save()
                    messages.success(request,'user successfully unblocked')
               return redirect('admin_userlist')



# PRODUCT MANAGEMENT
@never_cache
@login_required(login_url='admin_login')
def adminproduct(request):
     if request.user.is_admin:
            if request.method == 'POST':
                search = request.POST['search'] 
                products = Product.objects.filter(Q(product_name__icontains=search) | Q(category__category_name__icontains=search)).order_by('id')
            else:
                 products = Product.objects.all().order_by('id')
            
            paginator = Paginator(products, 4)
            page      = request.GET.get('page')
            paged_products = paginator.get_page(page)           
            context = {
            'products' : paged_products 
              } 
            return render (request,'admin/adminproduct.html', context)
     else:
          return redirect('ghome')
     
@never_cache
@login_required(login_url='admin_login')  
def admin_addproducts(request):
     if request.user.is_admin:
          if request.method== 'POST':
               form = ProductForm(request.POST,request.FILES)
               if form.is_valid():
                    form.save()
                    return redirect('adminproduct')
          else:
               form = ProductForm()
               context = {
                    'form':form
               }
               return render(request,'admin/admin_addproduct.html', context)
     else:
          return redirect('ghome')
@never_cache
@login_required(login_url='admin_login')    
def update_products(request,id):
      if request.user.is_admin:
          
           if request.method == 'POST':
                 product = Product.objects.get(pk=id)
                 form = ProductForm(request.POST,request.FILES,instance=product)
                 if form.is_valid():
                      form.save()
                      return redirect('adminproduct')
                 else:
                      return redirect('update_product',id)
           else:
               update = Product.objects.get(pk=id)
               form = ProductForm(instance=update)
           
            
               context = {
                    
                    'form' : form
               }
           return render(request,'admin/admin_updateproduct.html',context)

@never_cache
@login_required(login_url='admin_login')
def delete_products(request,id):
     if request.user.is_admin:
          product=Product.objects.get(id=id)
          product.delete()
          return redirect('adminproduct')
     else:
          return redirect('ghome')
          

# CATEGORY MANAGEMENT
@never_cache
@login_required(login_url='admin_login')
def admin_category(request):
     if request.user.is_admin:
          if request.method=='POST':
               search = request.POST['search']
               categories   =   Category.objects.filter(Q(category_name__icontains=search) | Q(slug__icontains=search)).order_by('id')
          else:
               categories = Category.objects.all().order_by('id')

          paginator =     Paginator(categories,4)
          page  =   request.GET.get('page')

          paged_categories  = paginator.get_page(page)
          context = {
            'categories': paged_categories
          }
       
          return render(request,'admin/admin_category.html',context)
     else:
          return redirect('ghome')

@never_cache
@login_required(login_url='admin_login')
def admin_addcategory(request):
     if request.user.is_admin:
          form = CategoryForm()
          if request.method == 'POST':
               try:
                    form = CategoryForm(request.POST,request.FILES)
                    if form.is_valid():
                         form.save()
                    return redirect('admin_category')
               except Exception as e:
                    raise e
          return render(request,'admin/admin_addcategory.html',{'form':form})
     else:
          return redirect('ghome')


@login_required(login_url='admin_login')
def update_category(request,id):
     if request.user.is_admin:
          if request.method ==  'POST':
               update= Category.objects.get(pk=id)
               form = Update_CategoryForm(request.POST,instance=update)
               if form.is_valid():
                    form.save()
                    return redirect ('admin_category')
               else:
                    return redirect('update_category',id)
          else:
               update = Category.objects.get(pk=id)
               form = Update_CategoryForm(instance=update)
               context ={
                    'form': form
                    }

              
          return render(request,'admin/update_category.html',context)
     else:
          return redirect('ghome')
     
     
@never_cache
@login_required(login_url='admin_login')
def admin_deletecategory(request,id):
     if request.user.is_admin:
          category  =   Category.objects.get(id=id)
          category.delete()
          return redirect('admin_category')
     else:
          return redirect ('ghome')
     
    
# ORDER MANAGEMENT
@never_cache
@login_required(login_url='admin_login')
def admin_orders(request):
     if request.user.is_admin:
          if request.method == 'POST':
               search = request.POST['search']
               orders = Order.objects.filter(Q(is_ordered=True), Q(order_number__icontains=search) | Q(user__email__icontains=search) | Q(name__icontains=search) ).order_by('-order_number')

          else:
               orders=Order.objects.filter(is_ordered=True).order_by('-order_number')

          paginator = Paginator(orders, 4)
          page = request.GET.get('page')
          paged_orders = paginator.get_page(page)
          context = {
               'orders': paged_orders
          }
          return render(request,'admin/admin_orders_list.html',context)
     
     else:
          return redirect ('ghome')
     
@login_required(login_url='admin_login')
def update_order(request,id):
     if request.user.is_admin:
          if request.method == 'POST':
               order = get_object_or_404(Order, id=id)
               status = request.POST.get('status')
               order.status = status 
               order.save()
               
               return redirect('admin_orders')
     else:
          return redirect('ghome')

@never_cache
@login_required(login_url='admin_login')
def adminorder_detail(request,id):
     order=Order.objects.get(id=id)
     context = {
          'order': order
     }
     return render(request,'admin/adminorder_detail.html',context)

# COUPON
@never_cache
@login_required(login_url='admin_login')
def coupon(request):
       if request.user.is_admin:
               if request.method == 'POST':
                         search = request.POST['search']
                         coupons  = Coupon.objects.filter( Q(code__icontains=search) | Q( discount__icontains=search) | Q(min_value__icontains=search) ).order_by('id')

               else:
                     coupons   =    Coupon.objects.all()              
               paginator =Paginator(coupons,4)
               page = request.GET.get('page')
               paged_coupon = paginator.get_page(page)

               context = {
                    'coupons':paged_coupon
               }
               return render(request,'admin/coupon.html',context)
       else:
            return redirect('ghome')
       
@never_cache
@login_required(login_url='admin_login')
def addCoupon(request):
       if request.user.is_admin:
               if request.method == 'POST':
                    form = CouponForm(request.POST)
                    if form.is_valid():
                         form.save()
                         messages.success(request,'Coupon added successfully.')
                         return redirect('coupon')
                    else:
                         messages.error(request,'Invalid form!!')
                         return redirect('addCoupon')
               form=CouponForm()


               context = {
                    'form':form
               }
               return render(request,'admin/add_coupon.html',context)
       else:
            return redirect('ghome')

@login_required(login_url='admin_login')
def deleteCoupon(request,id):
     dlt= Coupon.objects.get(pk=id)
     dlt.delete()
     return redirect('coupon')
     
@login_required(login_url='admin_login')
def updateCoupon(request,id):

     if request.user.is_admin:
          if request.method=='POST':
               update = Coupon.objects.get(pk=id)
               form=CouponForm(request.POST,instance=update)
               if form.is_valid():
                    form.save()
                    return redirect('coupon')
               else:
                    messages.error(request,'Invalid form!!')
                    return redirect('updateCoupon',id)
          else:
               update= Coupon.objects.get(pk=id)
               form= CouponForm(instance=update)
               context={
                    'form':form
               }
          return render(request,'admin/update_coupon.html',context)
     

# REVIEW 
login_required(login_url='admin_login')
def review_management(request):
     if request.user.is_admin:
          if request.method== 'POST':
               search=request.POST['search']
               reviews = ReviewRating.objects.filter(Q(product__product_name__icontains=search) | Q(user__name__icontains=search) |Q(review__icontains=search) | Q(rating__exact=search))
          else:
               reviews = ReviewRating.objects.all()
          paginator = Paginator(reviews,4)
          page=request.GET.get('page')
          paged_reviews  = paginator.get_page(page)
          context ={
               'reviews' :paged_reviews 
          }   
          return render(request,'admin/review_management.html',context)  

     else:
          return redirect('ghome')
     
login_required(login_url='admin_login')
def deleteReview(request,id):
     review = ReviewRating.objects.get(id=id)
     review.delete()
     return redirect('review_management')
