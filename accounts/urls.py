from django.urls import path
from . import views

urlpatterns = [
    path('signup/',views.signup,name="signup"),
    path('signin/',views.signin,name="signin"),
    path('activate/<uidb64>/<token>/',views.activate,name="activate"),
    path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate,name="resetpassword_validate"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('signout/',views.signout,name="signout"),
    path('forgotPassword/',views.forgotPassword,name="forgotPassword"),
    path('resetPassword/',views.resetPassword,name="resetPassword"),
    path('edit_profile/',views.edit_profile,name="edit_profile"),
    path('my_orders/',views.my_orders,name="my_orders"),
    path('change_password/',views.change_password,name="change_password"),
    path('my_address/',views.my_address,name="my_address"),
    path('add_address/', views.add_address, name='add_address'),
    path('delete_address/<int:id>/', views.delete_address, name='delete_address'),
    path('edit_address/<int:id>/', views.edit_address, name='edit_address'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('user_cancel_order/<int:order_number>/', views.user_cancel_order, name='user_cancel_order'),


]
