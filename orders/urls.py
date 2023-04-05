from django.urls import path
from . import views
urlpatterns =   [
   path('place_order/',views.place_order,name='place_order'),
   
   path('payments/',views.payments,name='payments'),
   path('status/', views.payment_status, name='payment_status'),
   path('success/', views.payment_success, name='payment_success'),
   path('fail/', views.payment_fail, name='payment_fail'),
   path('coupons',views.coupons,name="coupons"),


]