from django import forms
from .models import Account,EditProfile
from orders.models import Address

class RegistrationForm(forms.ModelForm):
    

    class Meta:
        model=Account
        fields=['name','email','phone','password']

    
    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control'})


class UserForm(forms.ModelForm):
    
    class Meta:
        model = Account
        fields =    ('name','phone')

class EditProfileForm(forms.ModelForm): 
    class Meta:
        model = EditProfile
        fields = ('address_line_1','address_line_2','city','state','country')

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields=['name','phone','email','address_line_1','address_line_2','country','state','city']
        
    
    def __init__(self, *args, **kwargs):
      super(AddressForm,self).__init__(*args, **kwargs)  
      for field  in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
             