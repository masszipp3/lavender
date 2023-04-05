from django.db import models
from store.models import Product
from accounts.models import Account
from orders.models import Order
from django.core.validators import MinValueValidator,MaxValueValidator
# Create your models here.
class Cart(models.Model):
    cart_id     =   models.CharField(max_length=250,blank=True)
    date_added  =   models.DateField(auto_now_add=True)


    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user        =   models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    product     =   models.ForeignKey(Product,on_delete=models.CASCADE)
    cart        =   models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
    quantity    =   models.IntegerField()
    is_active   =   models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity


    def __unicode__(self):
        return self.product
class Coupon(models.Model):
    code = models.CharField(max_length=50,unique=True)
    discount = models.IntegerField(validators = [MinValueValidator(0),MaxValueValidator(30)])
    min_value = models.IntegerField(validators = [MinValueValidator(0)])
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_at = models.DateField()
    active = models.BooleanField(default=False)
    def __str__(self):
        return self.code
    
class UserCoupon(models.Model):
    user =  models.ForeignKey(Account,on_delete=models.CASCADE, null= True)
    coupon = models.ForeignKey(Coupon,on_delete = models.CASCADE, null = True)
    order  = models.ForeignKey(Order,on_delete=models.SET_NULL,null = True,related_name='order_coupon')
    used = models.BooleanField(default = False)
    def __str__(self):  
        return str(self.id)