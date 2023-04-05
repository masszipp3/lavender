from django.db import models
from accounts.models import Account
from store.models import Product
# Create your models here.

class Payment(models.Model):
    user            =   models.ForeignKey(Account,on_delete=models.CASCADE)
    payment_id      =   models.CharField(max_length=100)
    payment_method  =   models.CharField(max_length=100,default='razorpay')
    amount_paid     =   models.CharField(max_length=100)
    status          =   models.CharField(max_length=100)
    created_at      =   models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=130,blank=True)
    order_number = models.CharField(max_length=50, blank=True)
    

    def __str__(self):
        return self.payment_id       

class Address(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50,null=True)
    state =   models.CharField(max_length=50)
    country =   models.CharField(max_length=50,blank=True)
    city =   models.CharField(max_length=50,blank=True)
    
    def full_name(self):
        return f"{self.name} {self.name}"

    def address(self):
        return f"{self.address_line_1} {self.address_line_2}"

    def __str__(self):
        return self.name
    class Meta:
        unique_together = ('address_line_1', 'address_line_2') 
    
class Order(models.Model):
    STATUS = (
        
        ('Accepted','Accepted'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
        ('Returned','Returned'),

    )
    
    user            =   models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    payment         =   models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    order_number    =   models.CharField(max_length=20)
    name            =   models.CharField(max_length=50)
    phone           =   models.CharField(max_length=15)
    email           =   models.EmailField(max_length=50)
    address_line_1  =   models.CharField(max_length=50)   
    address_line_2  =   models.CharField(max_length=50,blank=True)   
    country         =   models.CharField(max_length=50)   
    state           =   models.CharField(max_length=50)   
    city            =   models.CharField(max_length=50)
    order_total     =   models.FloatField()
    order_discout     =   models.FloatField(null=True)
    tax             =   models.FloatField()
    status          =   models.CharField(max_length=10,choices=STATUS,default='Pending')
    ip              =   models.CharField(blank=True,max_length=20)
    is_ordered      =   models.BooleanField(default=False)
 

    created_at      =   models.DateTimeField(auto_now_add=True)
    updated_at      =   models.DateTimeField(auto_now=True,blank=True)  

    def full_address(self):
        return f'{self.address_line_1},{self.address_line_2}'




    def __str__(self):
        return self.name 
    

class OrderProduct(models.Model):
    order           =   models.ForeignKey(Order,on_delete=models.CASCADE)
    payment         =   models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    user            =   models.ForeignKey(Account,on_delete=models.CASCADE)
    product         =   models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity        =   models.IntegerField()
    product_price   =   models.FloatField()
    ordered         =   models.BooleanField(default=False)
    created_at      =   models.DateTimeField(auto_now_add=True)
    updated_at      =   models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name 