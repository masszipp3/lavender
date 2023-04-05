from django.contrib import admin
from .models import Payment,Order,OrderProduct,Address
# Register your models here.

admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(OrderProduct)
admin.site.register(Address)