from django.urls import path
from . import views

urlpatterns = [
    path('',views.admin_login,name='admin_login'),
    path('admin_home/',views.admin_home,name='admin_home'), 
    path('adminlogout/', views.adminlogout, name='adminlogout'),


    # USERS
    path('admin_userlist/', views.admin_userlist, name='admin_userlist'),
    path('<int:id>/blockuser/', views.blockuser, name='blockuser'),

    # PRODUCTS
    path('adminproduct/', views.adminproduct, name='adminproduct'),
    path('admin_addproducts/', views.admin_addproducts, name='admin_addproducts'),
    path('<int:id>/update_products/', views.update_products,name='update_products'),
    path('<int:id>/delete_products/', views.delete_products,name='delete_products'),
    # CATEGORIES
    path('admin_category/', views.admin_category, name='admin_category'),
    path('admin_addcategory/', views.admin_addcategory, name='admin_addcategory'),
    path('<int:id>/update_category/', views.update_category, name='update_category'),
    path('<int:id>/admin_deletecategory/', views.admin_deletecategory, name='admin_deletecategory'),
    # ORDERS
    path('admin_orders/', views.admin_orders, name='admin_orders'),
    path('update_order/<int:id>',views.update_order,name="update_order"),
    path('adminorder_detail/<int:id>',views.adminorder_detail,name="adminorder_detail"),


    #COUPON
    path('coupon/', views.coupon,name='coupon'),
    path('addCoupon/', views.addCoupon,name='addCoupon'),
    path('<int:id>/deleteCoupon/', views.deleteCoupon,name='deleteCoupon'),
    path('<int:id>/updateCoupon/', views.updateCoupon,name='updateCoupon'),

    # REVIEWS
    path('review_management/',views.review_management,name="review_management"),
    path('<int:id>/deleteReview/',views.deleteReview,name="deleteReview"),
    





]