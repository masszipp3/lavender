from django import forms
from store.models import Product
from category.models import Category
from carts.models import Coupon


class ProductForm(forms.ModelForm):
    class Meta:
        model   =   Product
        fields  =   [
            'product_name','slug','price','image','stock','category','description'
        ]
        labels =    {
            'product_name':'product_name',
            'slug':'slug',
            'price':'price',
            'image':'image',
            'stock':'stock',
            'category':'category',
            'description':'description'

        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields  =   ['category_name','slug','description']


class Update_CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'slug', 'description']
        labels = {
            'category_name': 'category_name',
            'slug': 'slug',
            'description': 'description'
        }
class Update_ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name','slug', 'price', 'image', 'stock', 'category',]
        labels = {
            'product_name': 'product_name',
                   'slug' :'slug' ,
                   'price': 'price',
                   'image': 'image',
                   'stock': 'stock',
                'category': 'category',
            
           
        }
class DateInput(forms.DateInput):
    input_type = 'date'

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            'code','discount','min_value','valid_at','active'
        ]
        widgets = {
            'valid_at': DateInput()
        }
        labels = {
            'code':'Coupon Code',
            'discount':'Discount in percentage',
            'min_value':'Minimum Value',
            'valid_at':'Expiry Date',
            'active':'Available',
        }