from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('store/<int:pk_test>/', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.update_item, name="update_item"),
    path('process_order/', views.process_order, name="process_order"),
    path('register/', views.register_page, name="register"),
    path('login/', views.login_page, name="login"),
    path('logout/', views.logout_user, name="logout"),
    path('search/', views.search, name="search"),
    path('description/<int:pk>/', views.description, name="description"),
    path('success/<int:amnt>/', views.success, name="success"),
    path('profile/', views.profile, name="profile"),
    path('payment/', views.payment, name="payment"),
    path('charge/', views.charge, name="charge"),
]
