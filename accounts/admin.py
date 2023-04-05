from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account,EditProfile
# Register your models here.

class EditProfileAdmin(admin.ModelAdmin):

    list_display    =   ('user','city','state','country')

class AccountAdmin(UserAdmin):
    list_display=('email','name','last_login','date_joined','is_active')
    list_display_links=('email','name','date_joined')
    readonly_fields=('last_login',)
    filter_horizontal=()
    list_filter=()
    fieldsets=()
    ordering = ('date_joined', )

admin.site.register(Account,AccountAdmin)
admin.site.register(EditProfile,EditProfileAdmin)